# KidSafe API contract v1

## D050: native child app

`GET /api/device/child-view` uses the device access bearer, not a web account. It derives the child exclusively from the authenticated device, rejects revoked/deleted identities, and returns the child's name, local day, today's top apps/domains, ten human-readable audit entries and that device's latest request state. It returns no raw audit snapshots or credentials. Parent report/child-view query helpers are reused to keep the same data.

Authenticated loopback `POST /request-time` accepts `minutes:5|10|15` (default15) behind the existing actual PID/interpreter/config/user/session checks. The service queues a normal seven-field `unlock_request` with `duration_sec` equal to the requested amount, atomically with private pending-request metadata. Retries within ten minutes of an outstanding request do not add another event. Existing batch idempotency and parent approval amounts apply. Offline requests stay queued; they do not grant time themselves.

Tray `/lease` responses additionally contain a child-facing snapshot with local device allocation remaining, entertainment local+last-known peer usage, offline status and cached transparency data. Warnings are still consumed only by the normal tray lease loop. UI does not obtain web credentials or add a separate lease.

## D049: public parent registration

`GET /register` provides the signup form and a pre-auth CSRF token in a meta element, bound to an HttpOnly/Secure/SameSite=Lax cookie (`kidsafe_signup_csrf`, 30 minutes, `/api/auth`). `POST /api/auth/register` requires the matching `X-CSRF-Token`, same origin when supplied, and rejects cross-site fetches. It accepts `{name, username, password, confirm_password}`: trimmed name 1–80 chars, trimmed username 3–100 ASCII letters/digits/`_.@-`, matching passwords 10–1024 chars. Extra fields, including role and child_id, are rejected. The only public role is `parent`.

Success returns HTTP201 `{ok:true}`, without an authenticated session; the browser continues to `/login`. Duplicate usernames return409, password mismatch400, invalid data422 without reflecting password inputs. Signup has a separate 10-request/minute/IP bucket. Names use AES-GCM, passwords scrypt. Schema migration v3 adds the encrypted display name without changing existing credentials. `/api/auth/me` additionally returns `name` to the account holder. Existing accounts without a display name fall back to their username.

## D040: child requests with a duration

`POST /api/children/{child_id}/requests` accepts `minutes` of 5, 10, or 15, defaulting to 15 for existing callers. If `device_id` is omitted, the server uses the most recently seen active pairing. It deduplicates a retry against the same child's original request. Reports expose `requested_minutes`. A request approval derives its signed grant from the stored request. A manual add-time command remains 15 minutes. Legacy requests without a duration are treated as 15 minutes.

## D039: recent changes

`GET /api/children/{child_id}/audit/recent` returns up to ten entries, newest first, for the authorized parent or child view. Each entry contains `ts`, `icon`, and a Vietnamese `message`. The server derives descriptions from the stored audit snapshots. Command descriptions say that the parent sent a command, since an audit entry can precede the device acknowledgment.

## D038: pairing, password reset, weekly CSV and temporary unlock

The agent enrollment endpoint accepts the eight-character code with or without a dash after character four. Codes remain single use and expire in ten minutes. `GET /api/children/{child_id}/account` returns the child's username or null. `PUT /api/children/{child_id}/account/password` takes the new password, revokes child sessions and audits the reset without recording credentials. Both routes require an authorized parent.

`GET /api/children/{child_id}/reports.csv` returns the seven local calendar days and the top apps/domains as a UTF-8 CSV attachment for the authorized parent. New unlock commands carry `mode: until_midnight` with a signed `expires_at` at the next local midnight. A later lock cancels the override. Legacy unlock payloads retain their earlier 900-second behavior.

## D037: website rules

`GET /api/children/{child_id}/web/domain?host=...` validates and normalizes a hostname to its registrable domain using the bundled suffix list. The dashboard extracts the hostname before making the request. The API accepts hostnames only. New rules for a hosted tenant keep its private suffix boundary.

`PATCH /api/children/{child_id}/web` accepts `category`, `safesearch`, `add_domain`, or `remove_domain` actions. It returns the saved website fields and policy version. A change updates only the requested rule and creates an audit entry. Repeating an effective action keeps the same version. Removal matches the exact stored domain, including legacy subdomain entries.

## D036: application groups

Policy `app_groups` has exactly five keys: `study`, `games`, `video`, `social`, and `blocked`. Each group has `enabled`, `mode` (`daily`, `entertainment` or `custom`), optional `quota_sec`, optional `window` (weekday indexes Monday=0, inclusive start and exclusive end in minutes), `apps` (name and SHA-256), and `message`. Explicit groups cannot duplicate a name or hash. The blocked group always denies execution. Old policies receive default groups in a signed version upgrade with audit. A legacy PUT that omits `app_groups` preserves them.

Heartbeat optionally sends `group_used_sec` and receives `group_other_sec`, scoped to the same child and usage date. The server keeps monotonic values per device. Reports return `app_group_today_seconds` alongside the shared entertainment counter. No change to event payloads.

## D034: entertainment configuration and usage

Policy adds `entertainment_quota_sec` (0–86400, default3600) and `entertainment_apps` (unique case-folded executable names, no paths/URLs). Existing weekday/weekend values remain unchanged. Startup upgrades old active policies once, increments their version and writes an encrypted `upgrade_entertainment_policy` audit entry with actor `system`, so an agent never receives changed signed content under the old version.

`GET /api/children/{id}/policy` also returns `stats.controlled_app_count` (distinct explicitly controlled/grouped application names) and `stats.blocked_domain_count` (distinct custom plus category-expanded domains). These are configuration counts, not telemetry proving native enforcement.

Heartbeat accepts optional `entertainment_used_sec`; omitted/older values cannot erase a stored value. This is aggregate transport metadata; event payloads still have exactly seven fields and nine types. Reports add `entertainment_daily_seconds` and `entertainment_today` with `quota_sec`, `used_sec`, clamped `remaining_sec`, `reporting_devices`, and `devices_count`. Counters sum across the child's devices independently from ordinary/exception usage. Missing agent counters remain explicitly unknown to the UI.

D035 rejects explicit entertainment quotas above either daily quota with HTTP 422. Startup clamps older over-limit values to the lower daily quota, with a signed version increment and encrypted audit. For agents reporting entertainment, heartbeat returns `entertainment_other_sec`, the sum for the same child and usage date excluding the reporting device. The updated agent combines this with its current local counter to enforce exhaustion. Same-day peer snapshots remain available offline. Concurrent usage on another device counts after synchronization. This is not a distributed offline entertainment reservation.

Implemented in `server/app.py`. HTTPS only in the supported launcher; secure browser cookies require HTTPS. Device clients pin the lab certificate and Ed25519 public key before sending credentials. The backend binds to one Uvicorn worker because WebSocket connections and IP rate windows are process-local. SQLite writes use `BEGIN IMMEDIATE` before authentication/state reads; WAL and foreign keys are enabled.

## Browser authentication and ownership

`POST /api/auth/login` JSON `{username,password}` returns `{csrf_token,role,expires_in:43200}` and HttpOnly/Secure/SameSite=Lax `kidsafe_session`. All browser mutations require `X-CSRF-Token`; when Origin is present it must match the request origin. `GET /api/auth/me`; `POST /api/auth/logout` invalidates the server session. Five wrong passwords lock the account for 15 minutes. IP limits: 30 auth/enrollment/refresh requests/minute; 300 other API requests/minute. Forwarded IP headers are not trusted.

`GET/POST /api/children` (POST `{name}`); `GET/PUT /api/children/{id}/policy`; `GET /api/children/{id}/devices`; `GET /api/children/{id}/reports?days=7` (1–90); `GET /api/children/{id}/audit?offset=0&limit=50` (limit ≤100). Parent queries enforce ownership. Child-view reads only its bound child and cannot mutate. Admin has global access. Accounts are provisioned through `python -m server.seed --username ... --password ... [--role parent|admin|child-view] [--child-id ...]`, not unauthenticated registration.

Parent can provision one scoped child-view account using `POST /api/children/{id}/account` `{username,password}`. Child-view can submit `POST /api/children/{id}/requests` `{device_id}` with `Idempotency-Key`, producing the same seven-field `unlock_request` event. `GET /api/auth/csrf` rotates the session CSRF token for page restore; cross-origin access is rejected and CORS access is disabled. Other tabs must refresh this token after a 403.

Policy body: `weekday_quota_sec`, `weekend_quota_sec` (0–86400), IANA `timezone`, boolean `schedule[7][48]` Monday first, `app_mode` allowlist/blocklist, `apps:[{name,sha256}]`, `blocked_domains`, `blocked_categories` from the six source categories, `safesearch`. Initial 7200 seconds is an editable implementation seed, not a user-approved quota. Selected category domains expand from the reviewed local CSV. Reducing shared quota below outstanding device allocations is refused (409); return allocations through the ACK protocol first.

## Enrollment and device tokens

`POST /api/children/{id}/enroll-codes` `{consent:true}` records parental consent and returns a single-use 8-character code, `expires_in:600`. `POST /api/device/enroll` `{code,fingerprint,name}` returns `{device_id,child_id,access_token,refresh_token,expires_in:900,signing_public_key,policy}`. Fingerprints and tokens are stored as SHA-256 verifiers; device/child names use AES-GCM. Access is bound to the enrolled device. `POST /api/device/refresh` `{device_id,refresh_token}` rotates all existing device tokens, with refresh lifetime 30 days. Every remaining device endpoint uses `Authorization: Bearer ...`.

`GET /api/device/policy` returns an Ed25519 envelope `{payload,signature,public_key}` (base64). Sign bytes are UTF-8 `json.dumps(payload,sort_keys=True,separators=(',',':'),ensure_ascii=False)`. Public key is deployment-pinned; the response key alone is not a trust anchor. Payload includes policy fields plus `policy_id:"child_id:version"`, `version`, `child_id`, `device_id`, `allocation:{weekday_sec,weekend_sec}`, `offline_mode:"keep_last"`, `offline_after_days:3`. There is no volatile issue time in policy payload. Policy identity/content remains stable until its version changes.

`POST /api/device/heartbeat` every 60 seconds: `{device_id,status,quota_used_sec,policy_version,usage_date,exception_used_sec:0}`, status active/locked/idle/tray_unavailable, usage_date ISO local date. Quota and exception counters are cumulative per device/date; server stores max values to prevent duplicate counting. Returns `{server_time,policy_version,commands,deletion_pending}`. A changed version requires policy fetch/verification.

Devices JSON includes `status` and `reported_policy_version` from the last heartbeat. This reports acknowledgment honestly rather than assuming an issued policy has reached the device. `GET /api/children/{id}/commands` paginates command delivery/ACK state.

Reports return `normal_seconds` separately from `exception_seconds` and total usage. `extra_granted_seconds` counts only ACKed add-time commands within the requested local dates; unacknowledged grants appear as `pending_extra_seconds`. Remaining normal quota must not subtract exception usage or promise pending grants.

## Events and privacy

`POST /api/device/events` `{events:[...]}` with `Idempotency-Key` 8–128 chars. Event has **exactly seven fields** `ts,device_id,child_id,type,subject,duration_sec,policy_id`; nine allowed types are REQUIREMENTS R-F3-01. No extra field accepted. Timestamp includes timezone and must be within retention and +5 minute clock tolerance. Domains must already be registrable domains according to the bundled offline PSL; URLs, paths and full subdomains are refused. Events use a seven-column SQL table with implicit SQLite rowid, preserving identical legitimate events. Separate per-device batch metadata deduplicates retries; conflicting content under the same key is 409. Batch ≤500 events; retention 90 days. Response `{accepted,duplicate}`. Old data for a deleted child is refused with 410.

## Commands and recurring allocations

`POST /api/children/{id}/commands` `{device_id,type:lock|unlock|add_time}` plus `Idempotency-Key`. Returns signed command envelope. Payload includes `id,sequence,type,device_id,issued_at,expires_at`. Unlock adds `seconds:900` and expires after 15 minutes; add_time adds `seconds:900,day:YYYY-MM-DD`, usable only on that date. Add time is allocated to one device to increase the child's shared quota once. It never disables schedule or app/domain restrictions. Lock cancels existing unlock in the agent. Commands are ordered by strictly increasing per-device sequence; duplicate delivery never reapplies a grant. `POST /api/device/commands/{id}/ack` `{}` is idempotent. `GET` WebSocket `/api/device/ws` with Authorization header sends `{commands,server_time}` immediately and on push; token expiry closes the connection. The client refreshes/reconnects. Actual <5-second end-to-end latency requires lab measurement.

Recurring allocation: first device receives unreserved base quota; later devices receive zero until a transfer is acknowledged. No offline/revoked device's budget is automatically reclaimed. `POST /api/children/{id}/budget-transfers` `{donor_id,recipient_id,weekday_sec,weekend_sec}` creates pending transfer and signed donor `reduce_budget` command with **absolute new allocations** and `effective_date` tomorrow in policy timezone. Donor persists this reduction before ACK. Server then updates both allocations and policy version in one write transaction. Policy allocation includes `effective_date,previous_weekday_sec,previous_weekend_sec`: use previous values before that day. Delaying changes until the next day avoids reallocating already-spent current-day time. Unacknowledged transfer reserves donor budget. Overlapping changes involving a pending/future allocation are refused. Reduction/deletion commands remain deliverable until ACK, regardless of their transport expiry. Reduction must persist through restart and old-policy fetch until the new version confirms it.

`PUT /api/children/{id}/allocation` `{device_id,weekday_sec,weekend_sec}` assigns absolute shares from the unreserved pool immediately. A decrease instead queues the same durable reducer and returns budget to the pool after ACK, effective tomorrow. Current-day prior shares remain reserved until then, including after a device deletion ACK, to avoid reallocating already-spent quota. A lower shared policy quota is refused while those signed rights remain outstanding. This availability tradeoff is explicit; emergency lock can be sent separately.

## Deletion, revocation and limitations

`DELETE /api/children/{id}` immediately removes server events/batches/audit/name/policy/usage/child account sessions and queues durable `delete_data` per device. Returns `{server_deleted:true,pending_devices:[...],note}`; offline erasure is pending until ACK. Minimal tombstones retain IDs, verifier and cleanup credentials to prevent old uploads and deliver deletion. After deletion ACK, normal device access is revoked. `DELETE /api/children/{id}/devices/{device_id}` revokes normal access and queues deletion; cleanup-only heartbeat, refresh and ACK remain available until erased. Previous commands are canceled. Revoked offline budget remains reserved.

`GET /api/children/{id}/deletion-status` remains available to the owning parent after the child disappears from active listings. Cleanup token hashes remain until their original expiry to support a lost ACK response retry; they permit only cleanup heartbeat/ACK after revocation, never policy/events/normal access. Refresh after a successful deletion ACK is refused. Audit IP and old/new values, consent IP and display names are AES-GCM encrypted at rest; secret values are excluded from audit payloads.

Hourly maintenance deletes events, batch metadata and audit older than 90 days, expired sessions/tokens/codes and acknowledged old commands. TLS certificate creation, pin transport, Windows ACL, service/tray, DNS adapter changes and measurements belong to separate components and lab validation. The API never changes this host's DNS/firewall/services.
