from ipaddress import ip_address
from pathlib import Path
import re

from cryptography import x509
from cryptography.hazmat.primitives import hashes

from fastapi import Depends, HTTPException, Request
from fastapi.responses import FileResponse, JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy import select
from server.models import Child
from server.security import secret

ROOT = Path(__file__).parent
WINDOWS_SETUP = ROOT.parent / 'releases' / 'KidSafe-Setup-x64.exe'
VIEWS = {'overview': 'Tổng quan', 'time': 'Thời gian & lịch', 'apps': 'Ứng dụng',
         'web': 'Lọc website', 'requests': 'Yêu cầu từ con', 'devices': 'Thiết bị & ghép đôi',
         'quick-control': 'Điều khiển nhanh', 'reports': 'Báo cáo', 'privacy': 'Minh bạch & dữ liệu'}


def pairing_host(certificate, current):
    names = certificate.extensions.get_extension_for_class(x509.SubjectAlternativeName).value
    hosts = names.get_values_for_type(x509.DNSName)
    hosts.extend(str(address) for address in names.get_values_for_type(x509.IPAddress))
    reachable = []
    for host in hosts:
        try:
            address = ip_address(host)
            if address.is_loopback or address.is_unspecified or address.is_link_local:
                continue
        except ValueError:
            if host.lower() == 'localhost' or not re.fullmatch(r'[a-zA-Z0-9.-]+', host):
                continue
        reachable.append(host.lower())
    if current and current.lower() in reachable:
        return current.lower()
    return reachable[0] if len(set(reachable)) == 1 else None


def install(app, account, parent, db_session, owned):
    templates = Jinja2Templates(directory=str(ROOT / 'templates'))
    app.mount('/static', StaticFiles(directory=ROOT / 'static'), name='static')

    @app.get('/', include_in_schema=False)
    def root():
        return RedirectResponse('/app/overview', status_code=303)

    @app.get('/login', include_in_schema=False)
    def login(request: Request):
        return templates.TemplateResponse(request=request, name='login.html', context={'register': False})

    @app.get('/register', include_in_schema=False)
    def register(request: Request):
        token = secret()
        response = templates.TemplateResponse(request=request, name='login.html',
                                              context={'register': True, 'signup_csrf': token})
        response.set_cookie('kidsafe_signup_csrf', token, max_age=1800, path='/api/auth',
                            secure=app.state.settings.secure_cookie, httponly=True, samesite='lax')
        return response

    @app.get('/download', include_in_schema=False)
    def download_page(request: Request):
        return templates.TemplateResponse(request=request, name='download.html',
                                          context={'available': WINDOWS_SETUP.is_file()})

    @app.get('/download/windows', include_in_schema=False)
    def download_windows():
        if not WINDOWS_SETUP.is_file():
            raise HTTPException(404)
        return FileResponse(WINDOWS_SETUP, media_type='application/octet-stream',
                            filename=WINDOWS_SETUP.name)

    @app.get('/app/pairing-profile', include_in_schema=False)
    def pairing_profile(request: Request, actor=Depends(parent)):
        tls = getattr(app.state, 'pairing_tls', None)
        if not tls or request.url.scheme != 'https':
            raise HTTPException(409, 'Tệp kết nối cần máy chủ KidSafe chạy HTTPS.')
        ca_file, certificate_file, port = tls
        certificate = x509.load_pem_x509_certificate(certificate_file.read_bytes())
        host = pairing_host(certificate, request.url.hostname)
        if host is None:
            raise HTTPException(409, 'Mở dashboard qua địa chỉ LAN có trong chứng chỉ KidSafe rồi tải lại.')
        authority = f'[{host}]' if ':' in host else host
        return JSONResponse({
            'format': 'kidsafe-pairing-v1',
            'server_url': f'https://{authority}:{port}',
            'ca_pem': ca_file.read_text(encoding='ascii'),
            'certificate_pin': certificate.fingerprint(hashes.SHA256()).hex(),
            'signing_public_key': app.state.crypto.envelope({})['public_key'],
        }, headers={'Content-Disposition': 'attachment; filename="KidSafe-ket-noi.kidsafe"'})

    def render(request, view, child_view, db):
        try:
            actor = account(request, db)
        except HTTPException as error:
            if error.status_code == 401:
                return RedirectResponse('/login', status_code=303)
            raise
        if actor.role == 'child-view' and not child_view:
            return RedirectResponse('/child', status_code=303)
        if child_view and actor.role != 'child-view':
            # Parents may preview their own child's page without changing permissions.
            pass
        query = select(Child).where(Child.deleted == False)
        if actor.role == 'parent':
            query = query.where(Child.parent_id == actor.id)
        elif actor.role == 'child-view':
            query = query.where(Child.id == actor.child_id)
        children = [{'id': c.id, 'name': app.state.crypto.decrypt(c.name_enc)} for c in db.scalars(query)]
        selected = request.query_params.get('child')
        if selected:
            owned(db, actor, selected)
        elif children:
            selected = children[0]['id']
        child = next((c for c in children if c['id'] == selected), None)
        return templates.TemplateResponse(request=request, name='child.html' if child_view else 'parent.html',
            context={'actor': actor, 'actor_name': app.state.crypto.decrypt(actor.display_name_enc) if actor.display_name_enc else actor.username,
                     'children': children, 'child': child, 'views': VIEWS,
                     'view': view, 'title': VIEWS.get(view, 'Hôm nay của em')})

    @app.get('/app/{view}', include_in_schema=False)
    def page(request: Request, view: str, db=Depends(db_session)):
        if view not in VIEWS:
            raise HTTPException(404)
        return render(request, view, False, db)

    @app.get('/child', include_in_schema=False)
    def child_page(request: Request, db=Depends(db_session)):
        return render(request, 'child', True, db)
