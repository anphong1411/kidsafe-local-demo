# Bằng chứng kiểm thử 2026-11-04

## D034 — 2026-11-05

[Điều khiển riêng và quỹ giải trí](d034-controls/README.md):105core+3TLS=108testduynhất đạt theo nhóm;18browserchecks,66layoutchecks,33ảnh đã xem. Có lưu hai fullsuite lỗi socketWindows trước khi các ca mạng chạy riêng đạt. Ghi rõ chưa tự chặn/phân bổ offline quỹ giải trí hoặc nghiệm thu nativeWindows.

## D033 — 2026-11-05: typography và dashboard phụ huynh

Xem [chỉ mục mới](parent-refinement-2026-11-05/README.md): 46 backend tests, một ca TLS/WebSocket pin thật, 14 browser interaction checks; 10 trang × 6 chiều rộng không tràn trang/text dưới14px/heading dashboard quá2dòng. Ảnh trước/sau và JSON/XML đã lưu. Dữ liệu tổng hợp trong profile riêng; không phải nghiệm thu native Windows.

## Bản app cuối đợt D028

Gói giải nén với venv mới: **45 test backend/HTML/package đạt,34.42s**, `packaged-source.xml`. Lượt đầu phát hiện pytest chưa tạo parent của `.tmp/packaged-verification`; đã sửa tests/conftest.py và xác minh lại trên thư mục giải nén mới. Đây là kiểm thử gói nguồn, không phải chứng nhận Windows sạch/SCM. `tls-websocket.xml` là trích ba testcase TLS từ kết quả92pass, có ghi nguồn trong tên suite.

- **92 passed, 0 failed, 75.46s**, file `pytest-app-complete.xml`. Lệnh `.venv/Scripts/python.exe -m pytest tests -q --basetemp=.tmp/kidsafe-release-final --junitxml=docs/evidence/pytest-app-complete.xml`. Gồm45backend/HTML/package,41agent và6TLS/lab. Có một cảnh báo Starlette khuyến nghị httpx2 cho TestClient, chưa là lỗi API.
- Browser Chrome thực **19 kiểm tra đạt**: login/createchild,7view chính, edit/save lịch7x48, app rule với hash notepad thật (không chạy/kết thúc tiến trình), bộ lọc, HTMX, childlogin/request/403, parentapprove, protocolACK, childremaining đúng16phút sau grant15 trênquota3/used2. `ui/browser-result.json`; ảnh parent/child ở1440/768/390. Dữ liệu hồ sơ demo do giao thức tổng hợp, không phải enforcementWindows.
- Inspector app của skill chạy trong browser có auth: `ui/app-inspection.json` là mảng rỗng, không FAIL/WARN sau sửa chữ mobile. Đã tự xem ảnh parentdesktop/childphone. Staticlint còn eyebrow child/login theo giọng sản phẩm và enum `unlock` bị nhận nhầm marketingphrase; không có lỗi thực thi.
- WebSocket pinnedTLS và Ed25519 thật: `test_real_pinned_websocket_urgent_command` trong XML, property api_to_verified_agent_queue_seconds. Chỉ đo localhost protocol đến hàng nhận agent, không thay số đo khóaWindows<5s hoặc30mẫu M4.
- Venv mới `.tmp/clean-venv` cài47gói từ lockfile, import backend/agent/pywin32/pystray/DNS thành công. Không phải máy Windows sạch và không kết luận cài≤15phút.
- Bốn script PowerShell agent được parse không lỗi, không chạy thay đổi host. Start-KidSafe.ps1 thật khởi động server/login được. Không sửa DNS/registry/service/firewall/truststore hoặc khóa/kết thúc app trênhost.

Phần dưới là lịch sử các đợt trước. Chưa có ảnh Wireshark, số đo1giờ/30mẫu, native service/tray/ACL/userthường, SafeSearchbrowser/adapterWindows thật hoặc video nộp cuối.

Kiểm tra bổ sung sau đợt đầy đủ: `tls-deletion-regression.xml`, 2 passed/29.18s. Luồng HTTPS thử xóa con, ACK xóa lặp sau khi server đã thu hồi quyền thu thập, và xác nhận upload cũ bị từ chối. `compileall` và `git diff --check` đạt; file Design-PH.md vẫn giữ SHA256 gốc.

- `pytest-2026-11-04.xml`: kết quả thật 54 passed, 0 failed, 34.71s, Python 3.12.14 Windows 11 Home x64, dependency `requirements.lock`. Lệnh: `.venv/Scripts/python.exe -m pytest tests/server tests/agent tests/test_tls_integration.py tests/test_lab_tls.py -q --basetemp=.tmp/final-verification-04 --junitxml=docs/evidence/pytest-2026-11-04.xml`.
- Cảnh báo còn: Starlette khuyến nghị httpx2 cho TestClient; chưa đổi dependency vì bộ test hiện tại đạt. Không phải lỗi API sản phẩm.
- `tests/server/`: auth/ownership/CSRF/khóa đăng nhập/token/enrollment/policy/event idempotency/command/deletion/retention; xem tên test và XML để biết ca cụ thể.
- `tests/agent/`: quota monotonic, lịch/idle/clock, replay lệnh, policy integrity, durable queue/retention, app hash khi đổi tên, DNS exact/subdomain/SafeSearch và TCP/UDP loopback, suppression upload khi xóa.
- `tests/test_tls_integration.py`: Uvicorn HTTPS thật với chứng chỉ tạm, pinned agent enroll/policy/event retry/heartbeat/command ACK, sai pin bị từ chối. `tests/test_lab_tls.py`: CA/SAN/pin và TLS thật từ chối CA không tin cậy.
- Script chạy backend thật được khởi động riêng; `scripts.check_lab` PASS: TLS có kiểm CA, parent login, scoped read, logout. Sau smoke đã dừng server. Không lưu token/mật khẩu trong evidence.

Chưa có: ảnh chụp kết quả test, Wireshark, service LocalSystem/tray/ACL dưới user thường, DNS Windows thật/nslookup/browser, phép đo quota đủ một giờ, command <5s/policy ≤60s end-to-end, ≥30 mẫu M4, M3/M5 lab, video. File XML là log kiểm thử, không giả danh ảnh chụp.
