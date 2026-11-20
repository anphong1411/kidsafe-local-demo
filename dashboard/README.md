# Hai giao diện web KidSafe

D036 bổ sung năm thẻ tại `/app/apps`. Mỗi nhóm có cấu hình nhận diện tên/SHA-256, quỹ, giờ và lời nhắn. File picker băm tại trình duyệt qua Web Crypto trên HTTPS. Phần C cho phép nhập mã thủ công. Quy tắc allowlist/blocklist cũ nằm trong mục nâng cao. Xem [kiểm chứng](../docs/evidence/d036-app-groups/README.md).

D035: Trang Thời gian & lịch kiểm tra hạn mức ngay khi nhập. Lưới tuần có thước giờ, tổng từng ngày và cảnh báo khi khung xanh ngắn hơn hạn mức. Đổi phần chia offline nằm ở Thiết bị & ghép đôi. Tổng quan đọc quỹ còn lại từ bộ đếm foreground đã đồng bộ. Chọn nhóm giải trí tại Ứng dụng để agent bản mới áp dụng chặn khi hết quỹ. Xem `docs/evidence/d035-time/README.md`.

Cập nhật D033 (2026-11-05): thang chữ 14–32px, account một dòng và gear audit/xóa/logout, ba KPI/progress/quick actions. Giải trí chưa có budget riêng nên không hiển thị số mẫu. Bằng chứng 10 trang × 6 kích thước và kiểm thử trong `docs/evidence/parent-refinement-2026-11-05/README.md`; script QA riêng `scripts/check_ui_typography.mjs` và `scripts/check_dashboard_ui.mjs` chỉ dùng profile `.tmp/ui-review`.

Jinja2 render shell/ownership ở server. HTMX 2.0.4 được giữ local cho navigation cùng origin; form và dữ liệu gọi scoped JSON API, CSRF trên thao tác ghi. JS/CSS local, không cần CDN/font ngoài; không dùng unsafe-inline/unsafe-eval trong CSP. Giao diện chạy cùng backend HTTPS, không cần npm build.

- `/login`: đăng nhập bằng vai trò được server cấp, không có công tắc tự đổi thành parent.
- `/app/overview`: phụ huynh/quản trị; các trang thời gian/lịch, ứng dụng, lọc web, yêu cầu/lệnh, thiết bị, reports và dữ liệu.
- `/child`: trẻ; parent có thể xem trước hồ sơ mình quản lý, nhưng nút xin thêm giờ chỉ có cho tài khoản trẻ.

Hồ sơ, schedule7x48, quota, app name/hash, sáu nhóm web/SafeSearch, mã ghép một lần, tài khoản trẻ, chia phần offline, lệnh +15/mở/khóa, request, audit và xóa nối API thật. Không tự gắn nhãn máy đã áp dụng khi chưa có ACK/heartbeat version phù hợp. Mở/khóa/hạn mức còn phụ thuộc agent thực trên máy trẻ.

Nguồn màu/style parent: docs/Design-PH.md, hướng prose nền giấy sáng. Child mint/kem/pastel từ ảnh tham khảo, SVG minh họa code-native. Không dùng số minh họa làm số liệu thật. Hồ sơ có tên “hồ sơ demo” do browser smoke tạo sử dụng dữ liệu giao thức tổng hợp; đây không phải bằng chứng agent Windows đã khóa/chặn.

Kiểm tra: pytest các HTMLviews/ownership/XSS trong tests/server; `scripts/browser_check.mjs` dành môi trường Codex có skill design-taste-frontend (script QA tùy chọn, không là dependency app). Browser kiểm login/form/HTMX/childrequest/403 và chụp1440/768/390. Xem docs/evidence/ui. Nếu đóng gói để chạy app trên máy mới chỉ cần Python và requirements.lock.

Thư viện HTMX: MIT, bản2.0.4 từ https://unpkg.com/htmx.org@2.0.4/dist/htmx.min.js; giữ license MIT trong static/HTMX-LICENSE.txt. Tài liệu CSP/indicator: https://htmx.org/docs/ và https://htmx.org/attributes/hx-indicator/.
