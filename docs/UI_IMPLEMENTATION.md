# Thiết kế UI đã triển khai

## D034 — 2026-11-05: trang điều khiển riêng, tools và giải trí

Đã bỏ controls khỏi overview; `/app/quick-control` cùng shell, chọn máy kèm trạng thái, empty-state link pairing, ba thẻ đồng đều và lịch sử ACK. Tools card có hai hàng và hai nút dọc. Quota ba cột từ768px, nhãn/inputs thẳng hàng; scope label nowrap. App group selection riêng, quota giải trí lưu policy; KPI phút còn/tổng và progress theo aggregate riêng, ba footer cùng tâm. Đổi link child thành “Xem trước giao diện của con”.

Giữ framed-sheet/palette/type, CSS local. Chú thích rõ quỹ mới chưa tự chặn, counter thiếu được báo chờ. Đo11trang×6width, xem33ảnh cuối và các trạng tháiempty/online/33p từ45p; không overflow/text<14/heading dashboard>2line hoặc lệch footer/input. Inspector4trang×3width0finding với ngoại lệ user đã ghi. Evidence `evidence/d034-controls/README.md`.

## D033 — 2026-11-05: typography và parent dashboard

Giữ framed-sheet/palette/type hiện có; sidebar288px để account15px/600 một dòng, gear menu ba hành động, bảy icon SVG. Body16px, phụ/axis14px, breadcrumb/child-preview16px, H1 32px/700 (phone30px), h2 21px/700. Bỏ phụ đề/footer parent theo nguồn; login chỉ tăng caption13→14px, giữ ảnh gốc D032.

Ba KPI rounded16px, nền sáng/bóng nhẹ, bằng chiều cao cả phone; used/quota chung có progress50/75/90%, ngoại lệ/phần cộng chờ tách riêng; giải trí thiếu counter hiện dấu gạch và giải thích; pending requests nối báo cáo thật. Quick actions chọn máy + API/WS chờ ACK. Thẻ cân bằng phản ánh lịch hiện tại, ba hàng thống kê đều padding. Form/select và grid lịch co đúng viewport; lịch cuộn bên trong vùng riêng. Modal xóa focus Hủy trước, audit đọc đúng hồ sơ; keyboard/menu/HTMX hoạt động.

Đã đo60tổ hợp và xem30ảnh cuối, không overflow/text<14px/heading dashboard>2dòng/JSexception. Inspector0finding với ngoại lệ icon-chips và H1phone30px theo user. Chi tiết, nhận xét và bằng chứng: `evidence/parent-refinement-2026-11-05/README.md`. Giữ URL privacy cho liên kết cũ, chỉ bỏ khỏi sidebar; nội dung quyền riêng tư và audit child vẫn còn.

## 2026-11-05 — ảnh gia đình thay SVG login

Theo D032, dùng `dashboard/static/images/login-family.png` từ ảnh người dùng gửi, giữ nguyên1024×572/606243byte, SHA256 `1569b95c828384aa7dcf344d290de1d5745a5ba306ed08fc6183d44a6f071b09`. Không sửa bitmap hoặc tạo lại bằngAI. CSS width tối đa420px desktop,320px điện thoại, height:auto và bo16px; có alt mô tả, không méo/cắt hình. Logo KidSafe giữ nguyên. Thêm dấu chấm cuối H1, các câu đã bỏ không quay lại.

Browser8viewport từ320–1440px: ảnh tải đúng kích thước gốc, tỷ lệ được giữ, không overflow và tâm hai cột trùng nhau. Ở1440px, chiều cao cột trái456.4px/card457.5px; ảnh420×234.6px. Đã xem ảnh desktop/mobile, login sai/đúng/logout đạt và khôngJSexception. Bằng chứng `docs/evidence/login-family-image`; inspector khôngFAIL, H1-brand WARN giữ theo tỷ lệ chữ người dùng đã yêu cầu. Các mục SVG phía dưới là lịch sử, không mô tả minh họa hiện hành.

## /login — giản lược nội dung và SVG đồng hành

Theo D031, bỏ mô tả “Thời gian rõ ràng…” và slogan “Minh bạch với con / An tâm cùng bố mẹ”, bỏ badge/hình chữ K. H1 thành một câu “Một chút cân bằng, nhiều hơn kết nối”, không có dấu chấm hoặc thẻ br bắt buộc. Giữ eyebrow và form. SVG inline không có text/title/desc/foreignObject/image; tên truy cập đặt ở wrapper role=img, không chèn chữ hiển thị vào SVG.

Minh họa có người lớn/trẻ nhỏ hình học bo tròn, màn hình giữa hai người, đồng hồ không số, khiên/checkmark và ellipse nét đứt. Fill/stroke chỉ #4A5D4E, #E6DEC8, #F5EFE6; cao150px desktop/tablet,140px điện thoại. Giữ palette/form typography hiện có; ảnh hiện cả mobile và không tràn ngang.

Chrome kiểm8viewport1440/1366/1024/820/768/390/360/320: nội dung bỏ đúng, SVG không chữ/số hiển thị và đúng màu/chiều cao, hai cột cùng tâm, không JSexception; login sai/đúng/logout đạt. Đã xem ảnh1440/390 trong docs/evidence/login-connection. Inspector không FAIL; WARN H1 thương hiệu được giữ theo yêu cầu cỡ chữ của người dùng. Mục D030 phía dưới là lịch sử thiết kế trước khi giản lược.

## Tinh chỉnh /login theo tỷ lệ người dùng yêu cầu

Trang login dùng thêm `dashboard/static/login.css`, chỉ nạp ở login.html. Giữ toàn bộ màu kem/xanh rêu từ token hiện có. Logo24px/700, shield32×36px, khoảng logo–eyebrow28px; eyebrow14.5px/600/.02em; H1 desktop40px/700/1.2 (36px ở laptop), mô tả16px/1.6/max440px. Slogan14.5px/500 ghép vào figure viền nhẹ, art240×160 thu25% thành180×120. Card heading24px/700; subtitle14.5px, cách form24px; label14px/600/gap8px; input46px/font16px; CTA16px/600 căn giữa cùng mũi tên; caption13px/1.5.

Container max1120px, hai cột có tâm theo chiều dọc trùng nhau trong đo browser; chiều cao story430.9/card457.5px ở1440px. Dưới821px xếp một cột; điện thoại rút gọn minh họa/mô tả để ưu tiên form. Giữ tên input, autocomplete và JS/auth hiện có; thêm liên kết label-for/id và tên vùng truy cập.

Đã xem ảnh1440/390, đo8 viewport1440/1366/1024/820/768/390/360/320; không tràn ngang, font/input/alignment đúng. Chrome kiểm sai mật khẩu, đúng mật khẩu và logout đạt, không JSexception. `docs/evidence/login-refinement/results.json` và ảnh kèm theo. Inspector không FAIL; WARN app-title-size/eyebrow được giữ có chủ đích vì yêu cầu trực tiếp H1 thương hiệu36–42px và dòng dẫn nhập, không áp ngưỡng dashboard32px lên login.

Theo chỉ đạo mới nhất D028, tiếp tục hoàn thiện toàn bộ app, không dừng dựng giao diện vì thiếu máy lab. G-UI vẫn là cổng nghiệm thu nền; không tự đánh dấu đạt. Người dùng cho phép tự quyết chi tiết, không cần hỏi thêm.

Skill design-taste-frontend nhánh app screens: framed-sheet, seed 188968593, palette/type giữ từ nguồn người dùng. Parent dùng nền giấy #F5EFE6, surface #FCF8F1, chữ #1F1B16, moss #2E3A2F và be. Chọn hướng sáng theo phần prose Design-PH (thay cho YAML tối không thống nhất), có ghi đây là quyết định triển khai của Codex. Bố cục L-frame 232px, mép phải 8px, canvas32px; child giữ mint/kem/vàng và minh họa nhẹ bằng SVG code-native. Chữ system Segoe UI/Inter fallback có dấu Việt, không phụ thuộc font CDN.

Câu hỏi parent: con/máy nào cần phụ huynh xử lý? Dấu riêng là quota chung và phần giữ offline theo từng máy, các lệnh chờ ACK thật. Câu hỏi child: hôm nay em còn bao nhiêu thời gian, đã dùng gì và xin thêm thế nào? Dữ liệu API scoped, trạng thái thiếu dữ liệu không thay bằng số mẫu. Child time lớn và minh họa là ngoại lệ app house rules theo yêu cầu trực tiếp của người dùng về trẻ em.

Parent theo Design-PH, giữ nguồn nguyên bản; không nhập tên MentorBridge hoặc WebGL/landing motion vào app. Chưa coi UI đạt chỉ vì có markup; cần browser kiểm desktop/tablet/mobile và các thao tác thực.
