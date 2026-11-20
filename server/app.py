"""KidSafe API: query-scoped authorization and serialized SQLite write transactions."""
import asyncio
import base64
from collections import defaultdict, deque
from contextlib import asynccontextmanager
from datetime import date, datetime, timezone, timedelta
from io import StringIO
import json
import csv
import ipaddress
from pathlib import Path
import secrets
import time
from uuid import uuid4
from zoneinfo import ZoneInfo

from fastapi import Depends, FastAPI, HTTPException, Query, Request, Response, WebSocket, WebSocketDisconnect
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.exception_handlers import request_validation_exception_handler
from fastapi.responses import JSONResponse
from sqlalchemy import select, delete, text
from sqlalchemy.exc import IntegrityError

from .config import Settings
from .audit_summary import summarize_audit
from .database import Database
from .models import Account, Audit, Batch, Child, Command, Device, DeviceToken, Enrollment, Session, Transfer
from .schemas import AllocationInput, ChildAccountInput, ChildInput, CommandInput, Consent, Enroll, EventBatch, Heartbeat, Login, MoreTimeRequest, PolicyInput, Refresh, TransferInput, domain
from .schemas import ChildPasswordInput, DOMAIN_INPUT_ERROR, Register, WebRuleChange, website_domain
from .security import Crypto, canonical, digest, password_hash, password_verify, secret


def now():
    return int(time.time())


def stamp(epoch=None):
    return datetime.fromtimestamp(now() if epoch is None else epoch, timezone.utc).isoformat()


def uid():
    return str(uuid4())


def create_app(settings: Settings | None = None) -> FastAPI:
    settings = settings or Settings.from_env()
    database = Database(settings.database_url)
    crypto = Crypto(settings.encryption_key, settings.signing_seed)
    database.migrate()
    with database.session() as db:
        db.execute(text('BEGIN IMMEDIATE'))
        # Upgrade early lab audit rows without changing their meaning.
        for model, fields in ((Audit, ("ip", "old", "new")), (Enrollment, ("consent_ip",))):
            for record in db.scalars(select(model)):
                for field in fields:
                    value = getattr(record, field)
                    try:
                        crypto.decrypt(value)
                    except Exception as exc:
                        try:
                            if field in ("old", "new"):
                                json.loads(value)
                            elif value not in ("unknown", "testclient"):
                                ipaddress.ip_address(value)
                        except ValueError:
                            raise ValueError("Stored audit data cannot be decrypted with the configured key") from exc
                        setattr(record, field, crypto.encrypt(value))
        # New signed fields require a new version: an existing agent correctly
        # rejects changed content carrying the same policy version.
        for child in db.scalars(select(Child).where(Child.deleted == False)):
            old = json.loads(child.policy)
            daily_limit = min(old['weekday_quota_sec'], old['weekend_quota_sec'])
            upgrade_quota = ('entertainment_quota_sec' not in old or 'entertainment_apps' not in old
                             or old['entertainment_quota_sec'] > daily_limit)
            if upgrade_quota or 'app_groups' not in old:
                upgraded = PolicyInput.model_validate({
                    **old, 'entertainment_quota_sec': min(old.get('entertainment_quota_sec', 3600), daily_limit)
                }).model_dump()
                child.policy, child.version = json.dumps(upgraded, ensure_ascii=False), child.version + 1
                action = 'upgrade_entertainment_policy' if upgrade_quota else 'upgrade_app_groups'
                db.add(Audit(id=uid(), child_id=child.id, actor='system', ts=stamp(), action=action,
                             ip=crypto.encrypt('unknown'), old=crypto.encrypt(json.dumps(old, ensure_ascii=False)),
                             new=crypto.encrypt(json.dumps(upgraded, ensure_ascii=False))))
    rate_windows = defaultdict(deque)
    sockets: dict[str, WebSocket] = {}
    category_path = Path(__file__).resolve().parents[1] / "docs" / "data" / "domain_categories.csv"
    category_rows = list(csv.DictReader(category_path.open(encoding="utf-8-sig"))) if category_path.exists() else []

    def retention():
        cutoff = stamp(now() - 90 * 86400)
        with database.session() as db:
            db.execute(text("DELETE FROM events WHERE ts < :cutoff"), {"cutoff": cutoff})
            db.execute(delete(Batch).where(Batch.created < now() - 90 * 86400))
            db.execute(delete(Audit).where(Audit.ts < cutoff))
            db.execute(delete(Session).where(Session.expires < now()))
            # An expired refresh verifier remains cleanup-only until device erasure:
            # a long-offline machine must still retrieve a pending deletion.
            for token in db.scalars(select(DeviceToken).where(DeviceToken.expires < now())):
                device = db.get(Device, token.device_id)
                if token.kind != "refresh" or not device or device.deleted_ack:
                    db.delete(token)
            db.execute(delete(Enrollment).where(Enrollment.expires < now()))
            db.execute(delete(Command).where(Command.created < now() - 90 * 86400, Command.ack == True))
            for command in db.scalars(select(Command).where(Command.created < now() - 90 * 86400)):
                if json.loads(command.payload)["type"] not in ("delete_data", "reduce_budget"):
                    db.delete(command)
            cutoff_day = (datetime.now(timezone.utc) - timedelta(days=89)).date().isoformat()
            for device in db.scalars(select(Device)):
                usage = json.loads(device.usage)
                kept = {day: value for day, value in usage.items() if day >= cutoff_day}
                if kept != usage:
                    device.usage = json.dumps(kept)
            for transfer in db.scalars(select(Transfer).where(Transfer.applied == True)):
                if not db.scalar(select(Command.id).where(Command.key.in_([f"transfer:{transfer.id}", f"return:{transfer.id}"]))):
                    db.delete(transfer)

    @asynccontextmanager
    async def lifespan(_):
        async def clean():
            while True:
                await asyncio.to_thread(retention)
                await asyncio.sleep(3600)
        task = asyncio.create_task(clean())
        yield
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass
        database.engine.dispose()

    app = FastAPI(title="KidSafe", version="1.0.0", lifespan=lifespan)
    app.add_middleware(TrustedHostMiddleware, allowed_hosts=list(settings.allowed_hosts))
    app.state.database = database
    app.state.crypto = crypto
    app.state.settings = settings
    app.state.retention = retention

    @app.middleware("http")
    async def protect(request, call_next):
        if request.url.path.startswith("/api/"):
            identity = request.client.host if request.client else "unknown"
            bucket = "signup" if request.url.path == "/api/auth/register" else "auth" if request.url.path in ("/api/auth/login", "/api/device/enroll", "/api/device/refresh") else "api"
            key = (identity, bucket)
            queue = rate_windows[key]
            current = now()
            while queue and queue[0] < current - 60:
                queue.popleft()
            if len(queue) >= ({"signup": 10, "auth": 30}.get(bucket, 300)):
                return Response("Rate limit exceeded", status_code=429, headers={"Retry-After": "60"})
            queue.append(current)
            # Bound dormant IP state; proxy headers are intentionally not trusted.
            if len(rate_windows) > 10000:
                for old in list(rate_windows):
                    if not rate_windows[old] or rate_windows[old][-1] < current - 60:
                        del rate_windows[old]
        response = await call_next(request)
        response.headers["Cache-Control"] = "no-store"
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["Referrer-Policy"] = "same-origin"
        response.headers["Content-Security-Policy"] = "default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self' data:; frame-ancestors 'none'; base-uri 'self'; form-action 'self'"
        response.headers["Strict-Transport-Security"] = "max-age=31536000"
        return response

    def db_session(request: Request):
        with database.session() as db:
            if request.method not in ("GET", "HEAD", "OPTIONS"):
                db.execute(text("BEGIN IMMEDIATE"))
            yield db

    def begin_write(db):
        # Lock before reading state; this avoids double enrollment, grant, refresh and transfer races.
        if not db.in_transaction():
            db.execute(text("BEGIN IMMEDIATE"))

    def account(request: Request, db=Depends(db_session)):
        token = request.cookies.get("kidsafe_session", "")
        session = db.get(Session, digest(token))
        if not session or session.expires <= now():
            raise HTTPException(401, "Authentication required")
        actor = db.get(Account, session.account_id)
        if not actor:
            raise HTTPException(401, "Authentication required")
        if request.method not in ("GET", "HEAD", "OPTIONS"):
            if digest(request.headers.get("X-CSRF-Token", "")) != session.csrf_hash:
                raise HTTPException(403, "CSRF token required")
            origin = request.headers.get("origin")
            if origin and origin.rstrip("/") != str(request.base_url).rstrip("/"):
                raise HTTPException(403, "Cross-origin mutation rejected")
        return actor

    def parent(actor=Depends(account)):
        if actor.role not in ("parent", "admin"):
            raise HTTPException(403, "Parent permission required")
        return actor

    def owned(db, actor, child_id, write=False):
        query = select(Child).where(Child.id == child_id, Child.deleted == False)
        if actor.role == "parent":
            query = query.where(Child.parent_id == actor.id)
        elif actor.role == "child-view" and not write:
            query = query.where(Child.id == actor.child_id)
        elif actor.role != "admin":
            raise HTTPException(403, "Permission denied")
        result = db.scalar(query)
        if not result:
            raise HTTPException(404, "Child not found")
        return result

    def device_auth(request: Request, db=Depends(db_session)):
        raw = request.headers.get("Authorization", "")
        token = db.get(DeviceToken, digest(raw.removeprefix("Bearer ")))
        if not raw.startswith("Bearer ") or not token or token.kind != "access" or token.expires <= now():
            raise HTTPException(401, "Device access token required")
        device = db.get(Device, token.device_id)
        if device and request.url.path == "/api/device/events" and db.get(Child, device.child_id).deleted:
            raise HTTPException(410, "Child data deleted; discard old queue")
        cleanup_route = request.url.path == "/api/device/heartbeat" or (request.url.path.startswith("/api/device/commands/") and request.url.path.endswith("/ack"))
        if not device or (device.revoked and not cleanup_route):
            raise HTTPException(401, "Device revoked")
        return device

    def audit(db, request, actor, child_id, action, old=None, new=None):
        db.add(Audit(id=uid(), child_id=child_id, actor=actor.id, ts=stamp(),
                     ip=crypto.encrypt(request.client.host if request.client else "unknown"), action=action,
                     old=crypto.encrypt(json.dumps(old, ensure_ascii=False)), new=crypto.encrypt(json.dumps(new, ensure_ascii=False))))

    def policy_for(child, device):
        payload = PolicyInput.model_validate_json(child.policy).model_dump()
        payload.update(policy_id=f"{child.id}:{child.version}", version=child.version, child_id=child.id,
                       device_id=device.id, allocation={"weekday_sec": device.weekday_sec, "weekend_sec": device.weekend_sec},
                       offline_mode="keep_last", offline_after_days=3)
        if device.allocation_effective_date:
            payload["allocation"].update(effective_date=device.allocation_effective_date,
                                         previous_weekday_sec=device.previous_weekday_sec,
                                         previous_weekend_sec=device.previous_weekend_sec)
        payload["blocked_domains"] = sorted(set(payload["blocked_domains"]) | {row["domain"] for row in category_rows if row["category"] in payload["blocked_categories"]})
        return crypto.envelope(payload)

    def reserved(device, today):
        if device.allocation_effective_date and device.allocation_effective_date > today:
            return (max(device.weekday_sec, device.previous_weekday_sec), max(device.weekend_sec, device.previous_weekend_sec))
        return device.weekday_sec, device.weekend_sec

    def tokens(db, device):
        access, refresh = secret(), secret()
        db.add_all([DeviceToken(token_hash=digest(access), device_id=device.id, kind="access", expires=now() + 900),
                    DeviceToken(token_hash=digest(refresh), device_id=device.id, kind="refresh", expires=now() + 30 * 86400)])
        return {"device_id": device.id, "child_id": device.child_id, "access_token": access,
                "refresh_token": refresh, "expires_in": 900,
                "signing_public_key": crypto.envelope({})["public_key"]}

    def make_command(db, device, kind, key, *, issued=None, **extra):
        device.sequence += 1
        issued = now() if issued is None else issued
        expires = extra.pop("expires_at", stamp(issued + 86400))
        payload = {"id": uid(), "sequence": device.sequence, "type": kind, "device_id": device.id,
                   "issued_at": stamp(issued), "expires_at": expires, **extra}
        command = Command(id=payload["id"], child_id=device.child_id, device_id=device.id, key=key,
                          payload=json.dumps(payload), created=now())
        db.add(command)
        return command

    def pending(db, device):
        # delete_data remains deliverable until ACK even if deletion was requested while offline.
        rows = db.scalars(select(Command).where(Command.device_id == device.id, Command.ack == False).order_by(Command.created, Command.id)).all()
        valid = [json.loads(row.payload) for row in rows]
        valid.sort(key=lambda value: value["sequence"])
        return [crypto.envelope(value) for value in valid if value["type"] in ("delete_data", "reduce_budget") or datetime.fromisoformat(value["expires_at"]).timestamp() > now()]

    async def push(device_id):
        socket = sockets.get(device_id)
        if socket:
            try:
                with database.session() as db:
                    device = db.get(Device, device_id)
                    await socket.send_json({"commands": pending(db, device)})
            except (RuntimeError, WebSocketDisconnect):
                sockets.pop(device_id, None)

    @app.get("/health")
    def health():
        return {"status": "ok", "product": "KidSafe"}

    @app.exception_handler(RequestValidationError)
    async def invalid_input(request, error):
        if request.url.path == '/api/auth/register':
            # Do not reflect password inputs in Pydantic's default error payload.
            return JSONResponse({'detail': 'Thông tin chưa hợp lệ. Kiểm tra tên, tài khoản và mật khẩu (ít nhất 10 ký tự).'}, status_code=422)
        return await request_validation_exception_handler(request, error)

    @app.post('/api/auth/register', status_code=201)
    def register(body: Register, request: Request, db=Depends(db_session)):
        cookie = request.cookies.get('kidsafe_signup_csrf', '')
        header = request.headers.get('X-CSRF-Token', '')
        origin = request.headers.get('origin')
        if (not cookie or not secrets.compare_digest(digest(cookie), digest(header))
                or request.headers.get('sec-fetch-site') == 'cross-site'
                or (origin and origin.rstrip('/') != str(request.base_url).rstrip('/'))):
            raise HTTPException(403, 'Phiên tạo tài khoản đã hết hạn. Tải lại trang rồi thử lại.')
        if body.password != body.confirm_password:
            raise HTTPException(400, 'Hai mật khẩu chưa khớp.')
        if db.scalar(select(Account.id).where(Account.username == body.username)):
            raise HTTPException(409, 'Tên tài khoản đã được sử dụng. Hãy chọn tên khác.')
        actor = Account(id=uid(), username=body.username, display_name_enc=crypto.encrypt(body.name),
                        password=password_hash(body.password), role='parent')
        db.add(actor)
        try:
            db.flush()
        except IntegrityError:
            raise HTTPException(409, 'Tên tài khoản đã được sử dụng. Hãy chọn tên khác.')
        return {'ok': True}

    @app.post("/api/auth/login")
    def login(body: Login, request: Request, response: Response, db=Depends(db_session)):
        begin_write(db)
        actor = db.scalar(select(Account).where(Account.username == body.username))
        # Consume a normal scrypt check even when the username does not exist.
        if not actor:
            password_hash(body.password if len(body.password) >= 10 else body.password + "_" * 10)
            raise HTTPException(401, "Invalid credentials")
        if actor.locked_until > now():
            raise HTTPException(423, "Account temporarily locked")
        if not password_verify(body.password, actor.password):
            actor.failures += 1
            if actor.failures >= 5:
                actor.locked_until = now() + 900
                actor.failures = 0
            db.commit()  # Failure counters must survive the HTTP exception rollback.
            raise HTTPException(401, "Invalid credentials")
        actor.failures, actor.locked_until = 0, 0
        token, csrf = secret(), secret()
        db.add(Session(token_hash=digest(token), account_id=actor.id, csrf_hash=digest(csrf), expires=now() + 43200))
        response.set_cookie("kidsafe_session", token, max_age=43200, secure=settings.secure_cookie, httponly=True, samesite="lax", path="/")
        return {"csrf_token": csrf, "role": actor.role, "expires_in": 43200}

    @app.get("/api/auth/me")
    def me(actor=Depends(account)):
        return {"id": actor.id, "username": actor.username, "role": actor.role, "child_id": actor.child_id,
                "name": crypto.decrypt(actor.display_name_enc) if actor.display_name_enc else actor.username}

    @app.get("/api/auth/csrf")
    def csrf_token(request: Request, actor=Depends(account), db=Depends(db_session)):
        origin = request.headers.get("origin")
        if origin and origin.rstrip("/") != str(request.base_url).rstrip("/"):
            raise HTTPException(403, "Cross-origin request rejected")
        csrf = secret()
        db.get(Session, digest(request.cookies.get("kidsafe_session", ""))).csrf_hash = digest(csrf)
        return {"csrf_token": csrf}

    @app.post("/api/auth/logout")
    def logout(request: Request, response: Response, actor=Depends(account), db=Depends(db_session)):
        db.execute(delete(Session).where(Session.token_hash == digest(request.cookies.get("kidsafe_session", ""))))
        response.delete_cookie("kidsafe_session", path="/", secure=settings.secure_cookie, httponly=True, samesite="lax")
        return {"ok": True}

    @app.get("/api/children")
    def children(actor=Depends(account), db=Depends(db_session)):
        query = select(Child).where(Child.deleted == False)
        if actor.role == "parent":
            query = query.where(Child.parent_id == actor.id)
        elif actor.role == "child-view":
            query = query.where(Child.id == actor.child_id)
        return [{"id": row.id, "name": crypto.decrypt(row.name_enc), "version": row.version} for row in db.scalars(query)]

    @app.post("/api/children", status_code=201)
    def create_child(body: ChildInput, request: Request, actor=Depends(parent), db=Depends(db_session)):
        child = Child(id=uid(), parent_id=actor.id, name_enc=crypto.encrypt(body.name), policy=PolicyInput().model_dump_json())
        db.add(child)
        audit(db, request, actor, child.id, "create_child", new={"id": child.id})
        return {"id": child.id, "name": body.name}

    @app.get("/api/children/{child_id}/policy")
    def read_policy(child_id: str, actor=Depends(account), db=Depends(db_session)):
        child = owned(db, actor, child_id)
        policy = PolicyInput.model_validate_json(child.policy).model_dump()
        domains = set(policy['blocked_domains']) | {row['domain'] for row in category_rows if row['category'] in policy['blocked_categories']}
        apps = {rule['name'].casefold() for rule in policy['apps']} | set(policy['entertainment_apps'])
        apps.update(rule['name'].casefold() for group in policy['app_groups'].values() for rule in group['apps'])
        return {"version": child.version, "policy": policy,
                "stats": {"controlled_app_count": len(apps), "blocked_domain_count": len(domains)}}

    def child_login(db, child_id):
        return db.scalar(select(Account).where(Account.child_id == child_id, Account.role == "child-view"))

    @app.get("/api/children/{child_id}/account")
    def read_child_account(child_id: str, actor=Depends(parent), db=Depends(db_session)):
        owned(db, actor, child_id, True)
        target = child_login(db, child_id)
        return {"username": target.username if target else None}

    @app.post("/api/children/{child_id}/account", status_code=201)
    def create_child_account(child_id: str, body: ChildAccountInput, request: Request, actor=Depends(parent), db=Depends(db_session)):
        owned(db, actor, child_id, True)
        if db.scalar(select(Account).where(Account.username == body.username)):
            raise HTTPException(409, "Username already exists")
        if child_login(db, child_id):
            raise HTTPException(409, "Child-view account already exists")
        result = Account(id=uid(), username=body.username, password=password_hash(body.password), role="child-view", child_id=child_id)
        db.add(result)
        audit(db, request, actor, child_id, "create_child_account", new={"account_id": result.id, "username": result.username})
        return {"id": result.id, "username": result.username, "role": result.role}

    @app.put("/api/children/{child_id}/account/password")
    def reset_child_password(child_id: str, body: ChildPasswordInput, request: Request,
                             actor=Depends(parent), db=Depends(db_session)):
        owned(db, actor, child_id, True)
        target = child_login(db, child_id)
        if not target:
            raise HTTPException(404, "Hồ sơ này chưa có tài khoản đăng nhập cho con.")
        target.password = password_hash(body.password)
        target.failures = target.locked_until = 0
        db.execute(delete(Session).where(Session.account_id == target.id))
        audit(db, request, actor, child_id, "reset_child_password",
              new={"username": target.username, "sessions_revoked": True})
        return {"username": target.username}

    @app.get("/api/children/{child_id}/deletion-status")
    def deletion_status(child_id: str, actor=Depends(parent), db=Depends(db_session)):
        query = select(Child).where(Child.id == child_id)
        if actor.role != "admin":
            query = query.where(Child.parent_id == actor.id)
        record = db.scalar(query)
        if not record:
            raise HTTPException(404, "Child not found")
        devices = db.scalars(select(Device).where(Device.child_id == child_id)).all()
        return {"server_deleted": record.deleted, "pending_devices": [d.id for d in devices if not d.deleted_ack] if record.deleted else [],
                "complete": record.deleted and all(d.deleted_ack for d in devices)}

    @app.put("/api/children/{child_id}/policy")
    def write_policy(child_id: str, body: PolicyInput, request: Request, actor=Depends(parent), db=Depends(db_session)):
        child = owned(db, actor, child_id, True)
        devices = db.scalars(select(Device).where(Device.child_id == child.id, Device.deleted_ack == False)).all()
        # Never reduce a quota below still reserved recurring offline allocations.
        today = datetime.now(ZoneInfo(body.timezone)).date().isoformat()
        if sum(reserved(d, today)[0] for d in devices) > body.weekday_quota_sec or sum(reserved(d, today)[1] for d in devices) > body.weekend_quota_sec:
            raise HTTPException(409, "Hãy trả phần giờ máy đang giữ trong Thiết bị & ghép đôi trước khi giảm hạn mức.")
        old = json.loads(child.policy)
        if "app_groups" not in body.model_fields_set:
            body.app_groups = PolicyInput.model_validate(old).app_groups
        child.policy, child.version = body.model_dump_json(), child.version + 1
        audit(db, request, actor, child_id, "update_policy", old, body.model_dump())
        return {"version": child.version}

    @app.get("/api/children/{child_id}/web/domain")
    def normalize_website(child_id: str, host: str = Query(min_length=1, max_length=254),
                          actor=Depends(parent), db=Depends(db_session)):
        owned(db, actor, child_id, True)
        try:
            return {"domain": website_domain(host)}
        except ValueError as error:
            raise HTTPException(422, DOMAIN_INPUT_ERROR) from error

    @app.patch("/api/children/{child_id}/web")
    def update_website_rules(child_id: str, body: WebRuleChange, request: Request,
                             actor=Depends(parent), db=Depends(db_session)):
        child = owned(db, actor, child_id, True)
        policy = PolicyInput.model_validate_json(child.policy).model_dump()
        previous = {key: policy[key] for key in ("blocked_categories", "blocked_domains", "safesearch")}
        updated = previous.copy()
        if body.action == "category":
            categories = dict.fromkeys(previous["blocked_categories"])
            if body.enabled:
                categories[body.category] = None
            else:
                categories.pop(body.category, None)
            updated["blocked_categories"] = list(categories)
        elif body.action == "safesearch":
            updated["safesearch"] = body.enabled
        else:
            try:
                # Remove the exact stored rule, including legacy subdomain entries.
                name = website_domain(body.host) if body.action == "add_domain" else domain(body.host)
            except ValueError as error:
                raise HTTPException(422, DOMAIN_INPUT_ERROR) from error
            domains = previous["blocked_domains"]
            if body.action == "remove_domain":
                updated["blocked_domains"] = [value for value in domains if value != name]
            elif name not in domains:
                if len(domains) >= 2000:
                    raise HTTPException(422, "Danh sách đã đạt giới hạn 2000 tên miền.")
                updated["blocked_domains"] = [*domains, name]
        if updated != previous:
            policy.update(updated)
            child.policy, child.version = json.dumps(policy, ensure_ascii=False), child.version + 1
            audit(db, request, actor, child.id, "update_web_rules", previous, updated)
        return {"version": child.version, **updated}

    @app.post("/api/children/{child_id}/enroll-codes", status_code=201)
    def enroll_code(child_id: str, body: Consent, request: Request, actor=Depends(parent), db=Depends(db_session)):
        child = owned(db, actor, child_id, True)
        code = "".join(secrets.choice("ABCDEFGHJKLMNPQRSTUVWXYZ23456789") for _ in range(8))
        db.add(Enrollment(code_hash=digest(code), child_id=child.id, expires=now() + 600,
                          consent_at=stamp(), consent_ip=crypto.encrypt(request.client.host if request.client else "unknown")))
        audit(db, request, actor, child_id, "parental_consent", new={"consent": True, "expires_in": 600})
        return {"code": code, "expires_in": 600}

    @app.get("/api/children/{child_id}/devices")
    def devices(child_id: str, actor=Depends(account), db=Depends(db_session)):
        owned(db, actor, child_id)
        return [{"id": d.id, "name": crypto.decrypt(d.name_enc), "last_seen": d.last_seen, "revoked": d.revoked,
                 "reported_policy_version": d.reported_policy_version, "status": d.status,
                 "allocation": {"weekday_sec": d.weekday_sec, "weekend_sec": d.weekend_sec,
                                "effective_date": d.allocation_effective_date, "previous_weekday_sec": d.previous_weekday_sec,
                                "previous_weekend_sec": d.previous_weekend_sec}, "usage": json.loads(d.usage)}
                for d in db.scalars(select(Device).where(Device.child_id == child_id))]

    @app.post("/api/device/enroll", status_code=201)
    def enroll(body: Enroll, db=Depends(db_session)):
        begin_write(db)
        code = db.get(Enrollment, digest(body.code))
        if not code or code.expires <= now():
            raise HTTPException(400, "Invalid or expired enrollment code")
        child = db.get(Child, code.child_id)
        if not child or child.deleted:
            raise HTTPException(400, "Invalid enrollment")
        old_device = db.scalar(select(Device).where(Device.fingerprint_hash == digest(body.fingerprint)))
        if old_device:
            if not old_device.deleted_ack:
                raise HTTPException(409, "Device already enrolled; revoke and clear it before re-enrollment")
            old_device.fingerprint_hash = digest(f"deleted:{old_device.id}:{old_device.fingerprint_hash}")
            db.flush()
        policy = json.loads(child.policy)
        existing = db.scalars(select(Device).where(Device.child_id == child.id)).all()
        today = datetime.now(ZoneInfo(policy["timezone"])).date().isoformat()
        device = Device(id=uid(), child_id=child.id, fingerprint_hash=digest(body.fingerprint), name_enc=crypto.encrypt(body.name),
                        weekday_sec=max(0, policy["weekday_quota_sec"] - sum(reserved(d, today)[0] for d in existing)),
                        weekend_sec=max(0, policy["weekend_quota_sec"] - sum(reserved(d, today)[1] for d in existing)))
        db.add(device)
        db.flush()
        db.delete(code)
        result = tokens(db, device)
        result["policy"] = policy_for(child, device)
        return result

    @app.post("/api/device/refresh")
    def refresh(body: Refresh, db=Depends(db_session)):
        begin_write(db)
        token = db.get(DeviceToken, digest(body.refresh_token))
        if not token or token.kind != "refresh" or token.device_id != body.device_id:
            raise HTTPException(401, "Invalid refresh token")
        device = db.get(Device, body.device_id)
        cleanup = any(json.loads(c.payload)["type"] == "delete_data" for c in db.scalars(select(Command).where(Command.device_id == device.id, Command.ack == False)))
        if token.expires <= now() and not cleanup:
            raise HTTPException(401, "Refresh token expired")
        if device.revoked and not cleanup and not device.deleted_ack:
            raise HTTPException(401, "Device revoked")
        db.execute(delete(DeviceToken).where(DeviceToken.device_id == device.id))
        return tokens(db, device)

    @app.get("/api/device/policy")
    def device_policy(device=Depends(device_auth), db=Depends(db_session)):
        child = db.get(Child, device.child_id)
        if child.deleted:
            raise HTTPException(410, "Data deletion pending; acknowledge delete command")
        return policy_for(child, device)

    @app.post("/api/device/heartbeat")
    def heartbeat(body: Heartbeat, device=Depends(device_auth), db=Depends(db_session)):
        if body.device_id != device.id:
            raise HTTPException(403, "Device binding mismatch")
        child = db.get(Child, device.child_id)
        device.last_seen = now()
        device.reported_policy_version, device.status = body.policy_version, body.status
        entertainment_other_sec = 0
        group_other_sec = defaultdict(int)
        if not child.deleted:
            today = datetime.now(ZoneInfo(json.loads(child.policy)["timezone"])).date()
            try:
                usage_day = datetime.strptime(body.usage_date, "%Y-%m-%d").date()
            except ValueError:
                raise HTTPException(422, "Invalid usage_date")
            if usage_day > today or usage_day < today - timedelta(days=90) or body.quota_used_sec + body.exception_used_sec > 86400:
                raise HTTPException(422, "Usage counter outside daily or retention bounds")
            usage = json.loads(device.usage)
            previous = usage.get(body.usage_date, {"normal_sec": 0, "exception_sec": 0})
            usage[body.usage_date] = {"normal_sec": max(previous["normal_sec"], body.quota_used_sec),
                                      "exception_sec": max(previous["exception_sec"], body.exception_used_sec)}
            if body.entertainment_used_sec is not None or 'entertainment_sec' in previous:
                usage[body.usage_date]['entertainment_sec'] = max(previous.get('entertainment_sec', 0), body.entertainment_used_sec or 0)
            if body.group_used_sec is not None or 'group_sec' in previous:
                prior_groups = previous.get('group_sec', {})
                incoming_groups = body.group_used_sec or {}
                usage[body.usage_date]['group_sec'] = {
                    key: max(prior_groups.get(key, 0), incoming_groups.get(key, 0))
                    for key in prior_groups.keys() | incoming_groups.keys()
                }
            usage = {day: val for day, val in usage.items() if day >= (datetime.now(timezone.utc) - timedelta(days=90)).date().isoformat()}
            device.usage = json.dumps(usage)
            if (body.entertainment_used_sec is not None or body.group_used_sec is not None) and not device.revoked:
                other_usage = db.scalars(select(Device.usage).where(Device.child_id == child.id, Device.id != device.id))
                for value in other_usage:
                    peer = json.loads(value).get(body.usage_date, {})
                    entertainment_other_sec += peer.get('entertainment_sec', 0)
                    for key, seconds in peer.get('group_sec', {}).items():
                        group_other_sec[key] += seconds
        return {"server_time": stamp(), "policy_version": child.version, "commands": pending(db, device),
                "deletion_pending": child.deleted or device.revoked, "entertainment_other_sec": entertainment_other_sec,
                "group_other_sec": dict(group_other_sec)}

    @app.post("/api/device/events")
    def events(body: EventBatch, request: Request, device=Depends(device_auth), db=Depends(db_session)):
        child = db.get(Child, device.child_id)
        if child.deleted:
            raise HTTPException(410, "Child data deleted; discard old queue")
        key = request.headers.get("Idempotency-Key", "")
        if not 8 <= len(key) <= 128:
            raise HTTPException(400, "Idempotency-Key length must be 8–128")
        value = [event.model_dump(mode="json") for event in body.events]
        content_hash = digest(canonical({"events": value}).decode())
        old = db.scalar(select(Batch).where(Batch.device_id == device.id, Batch.key == key))
        if old:
            if old.body_hash != content_hash:
                raise HTTPException(409, "Idempotency key reused with different content")
            return {"accepted": len(value), "duplicate": True}
        for event in body.events:
            if event.device_id != device.id or event.child_id != child.id:
                raise HTTPException(403, "Event ownership mismatch")
            try:
                prefix, policy_version = event.policy_id.rsplit(":", 1)
                if prefix != child.id or not 1 <= int(policy_version) <= child.version:
                    raise ValueError
            except ValueError:
                raise HTTPException(422, "Event policy_id must identify a valid version of this child's policy")
            if event.ts.timestamp() < now() - 90 * 86400 or event.ts.timestamp() > now() + 300:
                raise HTTPException(422, "Event timestamp outside retention or clock tolerance")
            if event.type in ("domain_query", "blocked_domain"):
                subject = domain(event.subject)
                # tldextract uses its bundled Public Suffix List without network access.
                import tldextract
                extracted = tldextract.TLDExtract(suffix_list_urls=(), cache_dir=None)(subject)
                if not extracted.suffix or subject != extracted.top_domain_under_public_suffix:
                    raise HTTPException(422, "Domain subject must be a registered domain per Public Suffix List")
            data = event.model_dump(mode="json")
            data["ts"] = event.ts.isoformat()
            db.execute(text("INSERT INTO events(ts,device_id,child_id,type,subject,duration_sec,policy_id) VALUES(:ts,:device_id,:child_id,:type,:subject,:duration_sec,:policy_id)"), data)
        db.add(Batch(id=uid(), device_id=device.id, key=key, body_hash=content_hash, created=now()))
        try:
            db.flush()
        except IntegrityError:
            raise HTTPException(409, "Concurrent batch retry; retry request")
        return {"accepted": len(value), "duplicate": False}

    @app.post("/api/children/{child_id}/commands", status_code=201)
    async def command(child_id: str, body: CommandInput, request: Request, actor=Depends(parent), db=Depends(db_session)):
        child = owned(db, actor, child_id, True)
        device = db.scalar(select(Device).where(Device.id == body.device_id, Device.child_id == child.id, Device.revoked == False))
        if not device:
            raise HTTPException(404, "Device not found")
        key = request.headers.get("Idempotency-Key", "")
        if not 8 <= len(key) <= 128:
            raise HTTPException(400, "Idempotency-Key required")
        approval_prefix = f"request-{device.id}-"
        approval = body.type == "add_time" and key.startswith("request-")
        if approval and not key.startswith(approval_prefix):
            raise HTTPException(409, "Yêu cầu xin thêm giờ không thuộc thiết bị này.")
        approval_ts = key.removeprefix(approval_prefix) if approval else None
        previous = db.scalar(select(Command).where(Command.device_id == device.id,
                                                    Command.key.endswith(f":{key}", autoescape=True))) if approval else None
        key = f"{actor.id}:{key}"
        if not previous:
            previous = db.scalar(select(Command).where(Command.key == key))
        if previous:
            payload = json.loads(previous.payload)
            if previous.device_id != device.id or payload["type"] != body.type:
                raise HTTPException(409, "Idempotency key conflict")
            return crypto.envelope(payload)
        if body.type == "unlock":
            recent = [{**json.loads(row.payload), "_ack": row.ack} for row in db.scalars(select(Command).where(Command.child_id == child_id, Command.created >= now() - 86400))]
            for override in recent:
                if override["type"] != "unlock" or datetime.fromisoformat(override["expires_at"]).timestamp() <= now():
                    continue
                canceled = any(item["_ack"] and item["device_id"] == override["device_id"] and item["type"] in ("lock", "delete_data") and item["sequence"] > override["sequence"] for item in recent)
                if not canceled:
                    raise HTTPException(409, "Đã có một máy được mở khóa tạm thời. Hãy khóa máy đó trước khi mở máy khác.")
        extras = {}
        issued = now()
        if body.type in ("unlock", "add_time"):
            local = datetime.fromtimestamp(issued, ZoneInfo(json.loads(child.policy)["timezone"]))
            if body.type == "unlock":
                midnight = local.replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)
                extras = {"mode": "until_midnight", "expires_at": stamp(midnight.timestamp())}
            else:
                seconds = 900
                if approval_ts is not None:
                    requested = db.execute(text("""SELECT duration_sec FROM events
                        WHERE child_id=:child AND device_id=:device AND type='unlock_request' AND ts=:ts
                        ORDER BY rowid DESC LIMIT 1"""),
                        {"child": child.id, "device": device.id, "ts": approval_ts}).scalar_one_or_none()
                    if requested is None:
                        raise HTTPException(404, "Yêu cầu xin thêm giờ không còn tồn tại.")
                    seconds = requested if requested in (300, 600, 900) else 900
                extras = {"seconds": seconds, "day": local.date().isoformat()}
        row = make_command(db, device, body.type, key, issued=issued, **extras)
        audit(db, request, actor, child_id, f"command_{body.type}", new=json.loads(row.payload))
        db.commit()
        await push(device.id)
        return crypto.envelope(json.loads(row.payload))

    @app.get("/api/children/{child_id}/commands")
    def list_commands(child_id: str, offset: int = 0, limit: int = 50, actor=Depends(account), db=Depends(db_session)):
        owned(db, actor, child_id)
        if offset < 0 or not 1 <= limit <= 100:
            raise HTTPException(422, "Invalid pagination")
        return [{"id": row.id, "device_id": row.device_id, "type": json.loads(row.payload)["type"], "created": row.created,
                 "ack": row.ack, "payload": json.loads(row.payload)} for row in db.scalars(select(Command).where(Command.child_id == child_id).order_by(Command.created.desc()).offset(offset).limit(limit))]

    @app.post("/api/children/{child_id}/requests", status_code=201)
    def more_time(child_id: str, body: MoreTimeRequest, request: Request, actor=Depends(account), db=Depends(db_session)):
        child = owned(db, actor, child_id)
        if actor.role != "child-view":
            raise HTTPException(403, "Child-view permission required")
        key = request.headers.get("Idempotency-Key", "")
        if not 8 <= len(key) <= 128:
            raise HTTPException(400, "Idempotency-Key required")
        seconds = body.minutes * 60

        def request_hash(device_id):
            identity = f"request:{child.id}:{device_id}"
            return digest(identity if seconds == 900 else f"{identity}:{seconds}")

        batches = select(Batch).join(Device, Device.id == Batch.device_id).where(
            Device.child_id == child.id, Batch.key == f"web:{key}")
        if body.device_id is not None:
            batches = batches.where(Batch.device_id == body.device_id)
        previous = db.scalar(batches)
        if previous:
            if previous.body_hash != request_hash(previous.device_id):
                raise HTTPException(409, "Idempotency key conflict")
            return {"accepted": True, "duplicate": True}
        query = select(Device).where(Device.child_id == child.id, Device.revoked == False)
        if body.device_id is not None:
            query = query.where(Device.id == body.device_id)
        device = db.scalar(query.order_by(Device.last_seen.desc(), Device.id).limit(1))
        if not device:
            raise HTTPException(404, "Nhờ bố mẹ ghép máy để em có thể xin thêm giờ nhé.")
        db.execute(text("INSERT INTO events VALUES(:ts,:device_id,:child_id,'unlock_request','more_time',:seconds,:policy_id)"),
                   {"ts": datetime.now(timezone.utc).isoformat(timespec="microseconds"), "device_id": device.id,
                    "child_id": child.id, "seconds": seconds, "policy_id": f"{child.id}:{child.version}"})
        db.add(Batch(id=uid(), device_id=device.id, key=f"web:{key}", body_hash=request_hash(device.id), created=now()))
        return {"accepted": True, "duplicate": False}

    @app.post("/api/children/{child_id}/budget-transfers", status_code=201)
    async def transfer(child_id: str, body: TransferInput, request: Request, actor=Depends(parent), db=Depends(db_session)):
        child = owned(db, actor, child_id, True)
        donor = db.scalar(select(Device).where(Device.id == body.donor_id, Device.child_id == child.id, Device.revoked == False))
        recipient = db.scalar(select(Device).where(Device.id == body.recipient_id, Device.child_id == child.id, Device.revoked == False))
        if not donor or not recipient or donor.id == recipient.id:
            raise HTTPException(422, "Distinct active devices required")
        if db.scalar(select(Transfer).where(((Transfer.donor_id.in_([donor.id, recipient.id])) | (Transfer.recipient_id.in_([donor.id, recipient.id]))), Transfer.applied == False)):
            raise HTTPException(409, "A device already has a pending transfer")
        if body.weekday_sec == 0 and body.weekend_sec == 0:
            raise HTTPException(422, "Transfer must move a positive budget")
        if body.weekday_sec > donor.weekday_sec or body.weekend_sec > donor.weekend_sec:
            raise HTTPException(409, "Insufficient reserved budget")
        today = datetime.now(ZoneInfo(json.loads(child.policy)["timezone"])).date()
        if any(d.allocation_effective_date and d.allocation_effective_date > today.isoformat() for d in (donor, recipient)):
            raise HTTPException(409, "Wait until the previous recurring allocation becomes effective")
        if db.scalar(select(Transfer).where(Transfer.recipient_id == recipient.id, Transfer.applied == False)):
            raise HTTPException(409, "Recipient already has a pending transfer")
        effective_date = (today + timedelta(days=1)).isoformat()
        transfer_id = uid()
        db.add(Transfer(id=transfer_id, child_id=child_id, donor_id=donor.id, recipient_id=recipient.id,
                        weekday_sec=body.weekday_sec, weekend_sec=body.weekend_sec, effective_date=effective_date))
        row = make_command(db, donor, "reduce_budget", f"transfer:{transfer_id}", transfer_id=transfer_id,
                           weekday_sec=donor.weekday_sec - body.weekday_sec, weekend_sec=donor.weekend_sec - body.weekend_sec,
                           effective_date=effective_date)
        audit(db, request, actor, child_id, "budget_transfer_requested", new={"id": transfer_id, **body.model_dump()})
        db.commit()
        await push(donor.id)
        return {"id": transfer_id, "status": "awaiting_donor_ack", "command": crypto.envelope(json.loads(row.payload))}

    @app.put("/api/children/{child_id}/allocation")
    async def allocation(child_id: str, body: AllocationInput, request: Request, actor=Depends(parent), db=Depends(db_session)):
        child = owned(db, actor, child_id, True)
        device = db.scalar(select(Device).where(Device.id == body.device_id, Device.child_id == child_id, Device.revoked == False))
        if not device:
            raise HTTPException(404, "Device not found")
        policy = json.loads(child.policy)
        today = datetime.now(ZoneInfo(policy["timezone"])).date()
        if device.allocation_effective_date and device.allocation_effective_date > today.isoformat():
            raise HTTPException(409, "Previous allocation becomes effective tomorrow")
        if db.scalar(select(Transfer).where((Transfer.donor_id == device.id) | (Transfer.recipient_id == device.id), Transfer.applied == False)):
            raise HTTPException(409, "Allocation has a pending transfer")
        decreases = body.weekday_sec < device.weekday_sec or body.weekend_sec < device.weekend_sec
        increases = body.weekday_sec > device.weekday_sec or body.weekend_sec > device.weekend_sec
        if decreases and increases:
            raise HTTPException(422, "Split increases and decreases into separate acknowledged changes")
        old = {"weekday_sec": device.weekday_sec, "weekend_sec": device.weekend_sec}
        if not decreases:
            others = db.scalars(select(Device).where(Device.child_id == child_id, Device.id != device.id)).all()
            if body.weekday_sec + sum(reserved(d, today.isoformat())[0] for d in others) > policy["weekday_quota_sec"] or body.weekend_sec + sum(reserved(d, today.isoformat())[1] for d in others) > policy["weekend_quota_sec"]:
                raise HTTPException(409, "Shared quota is still reserved by another device")
            device.weekday_sec, device.weekend_sec = body.weekday_sec, body.weekend_sec
            device.allocation_effective_date = ""
            child.version += 1
            audit(db, request, actor, child_id, "allocate_unreserved_budget", old, body.model_dump())
            return {"status": "applied", "version": child.version}
        transfer_id = uid()
        effective_date = (today + timedelta(days=1)).isoformat()
        db.add(Transfer(id=transfer_id, child_id=child_id, donor_id=device.id, recipient_id="",
                        weekday_sec=device.weekday_sec - body.weekday_sec, weekend_sec=device.weekend_sec - body.weekend_sec,
                        effective_date=effective_date))
        row = make_command(db, device, "reduce_budget", f"return:{transfer_id}", transfer_id=transfer_id,
                           weekday_sec=body.weekday_sec, weekend_sec=body.weekend_sec, effective_date=effective_date)
        audit(db, request, actor, child_id, "return_budget_requested", old, body.model_dump())
        db.commit()
        await push(device.id)
        return {"status": "awaiting_donor_ack", "effective_date": effective_date, "command": crypto.envelope(json.loads(row.payload))}

    @app.post("/api/device/commands/{command_id}/ack")
    def ack(command_id: str, device=Depends(device_auth), db=Depends(db_session)):
        row = db.scalar(select(Command).where(Command.id == command_id, Command.device_id == device.id))
        if not row:
            raise HTTPException(404, "Command not found")
        payload = json.loads(row.payload)
        if row.ack:
            return {"ok": True, "duplicate": True}
        if payload["type"] == "reduce_budget":
            transfer = db.get(Transfer, payload["transfer_id"])
            if not transfer.applied:
                recipient = db.get(Device, transfer.recipient_id)
                for current in ([device, recipient] if recipient else [device]):
                    current.previous_weekday_sec = current.weekday_sec
                    current.previous_weekend_sec = current.weekend_sec
                    current.allocation_effective_date = transfer.effective_date
                device.weekday_sec -= transfer.weekday_sec
                device.weekend_sec -= transfer.weekend_sec
                if recipient:
                    recipient.weekday_sec += transfer.weekday_sec
                    recipient.weekend_sec += transfer.weekend_sec
                transfer.applied = True
                db.get(Child, device.child_id).version += 1
        if payload["type"] == "delete_data":
            device.deleted_ack, device.revoked = True, True
            device.fingerprint_hash = digest(f"purged:{device.id}")
            child = db.get(Child, device.child_id)
            if not child.deleted:
                device.previous_weekday_sec, device.previous_weekend_sec = device.weekday_sec, device.weekend_sec
                device.weekday_sec, device.weekend_sec = 0, 0
                device.allocation_effective_date = (datetime.now(ZoneInfo(json.loads(child.policy)["timezone"])).date() + timedelta(days=1)).isoformat()
                child.version += 1
            # Keep hashed cleanup credentials until expiry so a lost ACK response
            # can be retried. Revoked-device auth permits heartbeat/ACK only.
        row.ack = True
        return {"ok": True, "duplicate": False}

    @app.delete("/api/children/{child_id}")
    async def delete_child(child_id: str, request: Request, actor=Depends(parent), db=Depends(db_session)):
        child = owned(db, actor, child_id, True)
        child.deleted, child.name_enc, child.policy = True, crypto.encrypt("Deleted"), "{}"
        db.execute(text("DELETE FROM events WHERE child_id = :id"), {"id": child.id})
        db.execute(delete(Audit).where(Audit.child_id == child.id))
        db.execute(delete(Enrollment).where(Enrollment.child_id == child.id))
        devices = db.scalars(select(Device).where(Device.child_id == child.id)).all()
        ids = [d.id for d in devices]
        if ids:
            db.execute(delete(Batch).where(Batch.device_id.in_(ids)))
            db.execute(delete(Command).where(Command.device_id.in_(ids)))
        db.execute(delete(Transfer).where(Transfer.child_id == child.id))
        child_accounts = db.scalars(select(Account).where(Account.child_id == child.id)).all()
        for child_account in child_accounts:
            db.execute(delete(Session).where(Session.account_id == child_account.id))
            db.delete(child_account)
        for device in devices:
            device.name_enc, device.usage = crypto.encrypt("Deleted device"), "{}"
            device.last_seen, device.reported_policy_version, device.status = 0, 0, "deleted"
            if not device.deleted_ack:
                device.revoked = True
                make_command(db, device, "delete_data", f"delete:{child.id}:{device.id}")
        db.commit()
        for device_id in ids:
            await push(device_id)
        return {"server_deleted": True, "pending_devices": [d.id for d in devices if not d.deleted_ack],
                "note": "Minimal deletion tombstones remain until device ACK; old events are rejected"}

    @app.delete("/api/children/{child_id}/devices/{device_id}")
    async def revoke_device(child_id: str, device_id: str, request: Request, actor=Depends(parent), db=Depends(db_session)):
        owned(db, actor, child_id, True)
        device = db.scalar(select(Device).where(Device.id == device_id, Device.child_id == child_id))
        if not device:
            raise HTTPException(404, "Device not found")
        device.revoked = True
        # Reserved budget remains held; a revoked offline device may still spend its signed allocation.
        db.execute(delete(Command).where(Command.device_id == device.id, Command.ack == False))
        make_command(db, device, "delete_data", f"revoke:{device.id}:{uid()}")
        audit(db, request, actor, child_id, "revoke_device", new={"device_id": device_id})
        db.commit()
        if device_id in sockets:
            await sockets[device_id].close(code=1008)
            sockets.pop(device_id, None)
        return {"revoked": True, "reserved_budget_retained": True}

    @app.get("/api/children/{child_id}/audit")
    def audits(child_id: str, offset: int = 0, limit: int = 50, actor=Depends(account), db=Depends(db_session)):
        owned(db, actor, child_id)
        if offset < 0 or not 1 <= limit <= 100:
            raise HTTPException(422, "Invalid pagination")
        return [{"id": a.id, "actor": a.actor, "ts": a.ts, "ip": crypto.decrypt(a.ip), "action": a.action,
                 "old": json.loads(crypto.decrypt(a.old)), "new": json.loads(crypto.decrypt(a.new))} for a in db.scalars(
                     select(Audit).where(Audit.child_id == child_id).order_by(Audit.ts.desc()).offset(offset).limit(limit))]

    @app.get("/api/children/{child_id}/audit/recent")
    def recent_audits(child_id: str, actor=Depends(account), db=Depends(db_session)):
        owned(db, actor, child_id)
        # Timestamps have second precision. SQLite rowid orders writes within the same second.
        records = db.scalars(select(Audit).where(Audit.child_id == child_id)
                             .order_by(Audit.ts.desc(), text("audit.rowid DESC")).limit(10))
        result = []
        for record in records:
            icon, message = summarize_audit(record.action, json.loads(crypto.decrypt(record.old)),
                                           json.loads(crypto.decrypt(record.new)))
            result.append({"ts": record.ts, "icon": icon, "message": message})
        return result

    @app.get("/api/children/{child_id}/reports")
    def reports(child_id: str, days: int = 7, actor=Depends(account), db=Depends(db_session)):
        child = owned(db, actor, child_id)
        if not 1 <= days <= 90:
            raise HTTPException(422, "days must be 1–90")
        policy = PolicyInput.model_validate_json(child.policy).model_dump()
        local_now = datetime.now(ZoneInfo(policy["timezone"]))
        start = local_now.replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(days=days - 1)
        cutoff = start.astimezone(timezone.utc).isoformat()
        from types import SimpleNamespace
        events = [SimpleNamespace(**dict(row)) for row in db.execute(text("SELECT * FROM events WHERE child_id=:child AND ts>=:cutoff"), {"child": child_id, "cutoff": cutoff}).mappings()]
        apps, domains, daily, exceptions = defaultdict(int), defaultdict(int), defaultdict(int), defaultdict(int)
        entertainment = defaultdict(int)
        group_today = defaultdict(int)
        reporting_devices, active_devices = 0, 0
        today_key = local_now.date().isoformat()
        for d in db.scalars(select(Device).where(Device.child_id == child_id)):
            device_usage = json.loads(d.usage)
            if not d.revoked:
                active_devices += 1
                reporting_devices += 'entertainment_sec' in device_usage.get(today_key, {})
            for day, usage in device_usage.items():
                if day == today_key:
                    for key, seconds in usage.get('group_sec', {}).items():
                        group_today[key] += seconds
                if day >= start.date().isoformat():
                    daily[day] += usage["normal_sec"] + usage["exception_sec"]
                    exceptions[day] += usage["exception_sec"]
                    entertainment[day] += usage.get('entertainment_sec', 0)
        for event in events:
            if event.type == "app_stop":
                apps[event.subject] += event.duration_sec
            if event.type == "domain_query":
                domains[event.subject] += 1
        top = lambda data: [{"subject": k, "value": v} for k, v in sorted(data.items(), key=lambda v: (-v[1], v[0]))[:10]]
        def request_row(ts, device_id, subject, duration_sec):
            return {"ts": ts, "device_id": device_id, "subject": subject,
                    "requested_minutes": duration_sec // 60 if duration_sec in (300, 600, 900) else 15}

        requests = [request_row(e.ts, e.device_id, e.subject, e.duration_sec)
                    for e in events if e.type == "unlock_request"]
        grants, pending_grants = 0, 0
        responses = {}
        for row in db.scalars(select(Command).where(Command.child_id == child_id, Command.created >= now() - 90 * 86400)):
            command = json.loads(row.payload)
            # The approval button uses one stable key per device/timestamp. A
            # queued approval is already being handled, but is not an agent ACK.
            if command["type"] == "add_time" and ":request-" in row.key:
                responses[row.key.split(":request-", 1)[1]] = {
                    "status": "acknowledged" if row.ack else "sent", "command_id": row.id}
            if command["type"] == "add_time" and start.date().isoformat() <= command.get("day", "") <= local_now.date().isoformat():
                if row.ack:
                    grants += command["seconds"]
                else:
                    pending_grants += command["seconds"]
        for item in requests:
            item.update(responses.get(f"{item['device_id']}-{item['ts']}", {"status": "pending"}))
        # Outstanding requests must not disappear just because they are older
        # than the selected chart period. Retention still bounds stored events.
        outstanding = []
        for item in db.execute(text("SELECT ts, device_id, subject, duration_sec FROM events WHERE child_id=:child AND type='unlock_request' ORDER BY ts DESC"), {"child": child_id}).mappings():
            if f"{item['device_id']}-{item['ts']}" not in responses:
                outstanding.append({**request_row(**item), "status": "pending"})
        entertainment_today = entertainment.get(today_key, 0)
        return {"days": days, "through_date": today_key, "daily_seconds": dict(daily), "exception_seconds": dict(exceptions), "total_seconds": sum(daily.values()),
                "entertainment_daily_seconds": dict(entertainment), "app_group_today_seconds": dict(group_today),
                "entertainment_today": {"quota_sec": policy['entertainment_quota_sec'], "used_sec": entertainment_today,
                                        "remaining_sec": max(0, policy['entertainment_quota_sec'] - entertainment_today),
                                        "reporting_devices": reporting_devices, "devices_count": active_devices},
                "normal_seconds": sum(daily.values()) - sum(exceptions.values()), "extra_granted_seconds": grants, "pending_extra_seconds": pending_grants,
                "top_apps": top(apps), "top_domains": top(domains), "blocked_count": sum(e.type in ("blocked_app", "blocked_domain") for e in events),
                "requests": requests[-100:], "request_count": len(requests),
                "pending_request_count": len(outstanding), "pending_requests": outstanding[:100]}

    @app.get('/api/device/child-view')
    def device_child_view(device=Depends(device_auth), db=Depends(db_session)):
        from types import SimpleNamespace
        child = db.get(Child, device.child_id)
        if not child or child.deleted:
            raise HTTPException(410, 'Child data deleted')
        viewer = SimpleNamespace(role='child-view', child_id=child.id)
        report = reports(child.id, 1, viewer, db)
        own_requests = [item for item in report['requests'] if item['device_id'] == device.id]
        return {'name': crypto.decrypt(child.name_enc), 'day': report['through_date'],
                'top_apps': report['top_apps'], 'top_domains': report['top_domains'],
                'audit': recent_audits(child.id, viewer, db),
                'last_request': {key: own_requests[-1][key] for key in ('ts', 'status', 'requested_minutes')} if own_requests else None,
                'updated_at': stamp()}

    @app.get("/api/children/{child_id}/reports.csv")
    def export_report(child_id: str, actor=Depends(parent), db=Depends(db_session)):
        report = reports(child_id, 7, actor, db)
        last_day = date.fromisoformat(report["through_date"])
        output = StringIO(newline="")
        writer = csv.writer(output)
        writer.writerow(["Loại", "Ngày", "Mục", "Tổng giây", "Giây ngoại lệ", "Giây giải trí", "Lượt truy vấn"])
        for offset in range(6, -1, -1):
            day = (last_day - timedelta(days=offset)).isoformat()
            writer.writerow(["Thời lượng", day, "", report["daily_seconds"].get(day, 0),
                             report["exception_seconds"].get(day, 0), report["entertainment_daily_seconds"].get(day, 0), ""])
        for key, label in (("top_apps", "Ứng dụng"), ("top_domains", "Tên miền")):
            for entry in report[key]:
                subject = entry["subject"]
                if subject.startswith(("\t", "\r", "\n")) or subject.lstrip().startswith(("=", "+", "-", "@")):
                    subject = "'" + subject
                value = entry["value"]
                writer.writerow([label, "", subject, value if key == "top_apps" else "", "", "",
                                 value if key == "top_domains" else ""])
        return Response(output.getvalue().encode("utf-8-sig"), media_type="text/csv",
                        headers={"Content-Disposition": f'attachment; filename="kidsafe-report-{last_day}.csv"',
                                 "Cache-Control": "no-store"})

    @app.websocket("/api/device/ws")
    async def websocket(socket: WebSocket):
        # Authorization header prevents bearer leakage through URL, proxy logs or browser history.
        raw = socket.headers.get("authorization", "")
        with database.session() as db:
            token = db.get(DeviceToken, digest(raw.removeprefix("Bearer ")))
            if not raw.startswith("Bearer ") or not token or token.kind != "access" or token.expires <= now():
                await socket.close(code=1008)
                return
            device = db.get(Device, token.device_id)
            if not device or device.revoked:
                await socket.close(code=1008)
                return
            device_id, expires = device.id, token.expires
            initial = pending(db, device)
        await socket.accept()
        old = sockets.get(device_id)
        if old:
            await old.close(code=1000)
        sockets[device_id] = socket
        await socket.send_json({"commands": initial, "server_time": stamp()})
        try:
            while now() < expires:
                try:
                    await asyncio.wait_for(socket.receive_text(), timeout=min(30, max(1, expires - now())))
                except asyncio.TimeoutError:
                    await socket.send_json({"server_time": stamp()})
            await socket.close(code=1008)
        except (WebSocketDisconnect, RuntimeError):
            pass
        finally:
            if sockets.get(device_id) is socket:
                sockets.pop(device_id, None)

    from dashboard.routes import install
    install(app, account, parent, db_session, owned)
    return app
