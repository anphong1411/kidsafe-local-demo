# Trạng thái dự án và điểm tiếp tục

## D062 — Mở thẳng trang đăng ký và đăng nhập

Hai nút trên trang tải mở trực tiếp biểu mẫu tương ứng, bỏ hộp chọn địa chỉ. Gói mặc định dùng localhost 8446, có thể đặt đích LAN bằng `--server-origin` khi đóng gói. [Kiểm chứng](evidence/d062-direct-account/pages-check.json)

## D061 — Hai nút tài khoản ở bước 2

Bản tải công khai có cả Tạo tài khoản và Đăng nhập ở bước Mở bảng điều khiển phụ huynh. Hai nút dùng cùng hộp nhập địa chỉ máy chủ và mở đúng trang tương ứng. [Kiểm chứng](evidence/d061-pages-account-buttons/pages-check.json)

## D060 — Khôi phục Đăng nhập trên trang tải công khai

Menu và bước 2 có nút Đăng nhập. Bản GitHub Pages mở hộp nhập địa chỉ HTTPS của máy chủ, mặc định localhost 8446. Xác thực diễn ra trên FastAPI. Gói cập nhật giao diện đã dựng lại. [Kiểm chứng](evidence/d060-pages-login/pages-check.json)

## D059 — Sửa gói upload GitHub Pages thiếu tài nguyên

Đã kiểm trang công khai trả HTML 200 trong khi CSS, JavaScript và shader dưới `static/` trả 404. Repo chỉ có các tệp ở gốc. Gói phát hành mới đặt toàn bộ tệp ở gốc để upload qua trình duyệt. Gói `KidSafe-github-pages-web-update.zip` gồm 10 tệp giao diện dành cho repo đã có bộ cài. [Hướng dẫn](GITHUB_PAGES_DEPLOY.md)

## D058 — Bỏ nút điều khiển chuyển động nền

Phần Cách cài chỉ còn tiêu đề và ba bước. Shader tiếp tục tôn trọng tùy chọn Giảm chuyển động của hệ điều hành. Đã đóng gói lại GitHub Pages và kiểm trang local cùng bản tĩnh bằng Chrome. [Kiểm chứng](evidence/d058-remove-motion-button/pages-check.json)

## D057 — 2026-11-09: kiểm lại app và chuẩn bị phát hành qua GitHub Pages

Gói `releases/KidSafe-github-pages.zip` chứa trang tải công khai và bộ cài Windows x64 có runtime. Luồng demo dùng máy chủ FastAPI/SQLite/HTTPS riêng trong LAN. Đã làm rõ ba bước tải, mở dashboard phụ huynh, cài và ghép đôi; sửa race menu khi đổi breakpoint và cách hiển thị quỹ giải trí khi thiếu dữ liệu. Gói được kiểm cục bộ dưới đường dẫn con như GitHub Pages. Chưa publish repo/Pages và chưa nghiệm thu cài service/DNS trên máy trẻ sạch. [Hướng dẫn](GITHUB_PAGES_DEPLOY.md) · [Bằng chứng](evidence/d057-download/README.md)

## D056 — 2026-11-07: Mesh drift và rà toàn bộ web

Thanh menu và ba bước cài đặt dùng WebGL1 Mesh drift từ prompt người dùng, phủ màu ổn định để giữ tương phản; menu 16px/650 đồng nhất, mobile có đầy đủ liên kết. Đã sửa mất focus khi polling, vòng đời sidebar mobile, fallback POST cho auth và hướng dẫn xin giờ trong app Windows. Kiểm tra 13 trang × 6 kích thước (78 bố cục), tương tác và 54 test backend/auth/download đạt. Shader có pause, reduced-motion, context fallback/restore và giới hạn render. [Bằng chứng và giới hạn](evidence/d056-web-polish/README.md)

## D055 — 2026-11-07: nền tối chuyển sắc và tiêu đề gallery

Người dùng đính chính cách hiểu D054 bằng ảnh mẫu. Đã bỏ viền đen quanh chữ, dùng nền tối chuyển sắc ở đáy ảnh cho câu mô tả trắng ngắn và thêm lại “Đồng hành trong từng khoảnh khắc.”. Giữ nhãn pill, không thêm slogan/số/CTA vào ảnh. Năm kích thước và hover/dialog/reduced motion đạt. [Bằng chứng](evidence/d055-gradient/README.md)

## D054 — 2026-11-07: mô tả trắng viền đen trong ảnh

Theo chỉnh sửa mới, đưa câu mô tả của bốn ảnh vào góc dưới bên trong ảnh, chữ trắng viền đen và bóng nhẹ. Giữ ảnh sáng và nhãn pill. Đã kiểm tra năm kích thước, hover/dialog/reduced motion. [Bằng chứng](evidence/d054-caption/README.md)

## D053 — 2026-11-07: gallery sáng, ít chữ và gọn khoảng cách

Theo chỉnh sửa mới, phần Cách hoạt động bỏ lời dẫn/hướng dẫn phụ, nâng tiêu đề chính, thu gọn ba dòng giới thiệu. Ảnh nguyên màu, nhãn chức năng trong pill tối, chỉ một câu mô tả bên dưới mỗi ảnh; bỏ số, tiêu đề phụ và CTA xem ảnh. Khoảng chữ–ảnh khoảng 30px ở 1440px, pin rút còn 160px cuộn bổ sung. Đã kiểm tra tám kích thước và tương tác, rà bằng Taste/Emil/review-animations. [Bằng chứng](evidence/d053-clear-gallery/README.md)

## D052 — 2026-11-07: giới thiệu theo dòng và thư viện ảnh tương tác

Đã thay khối hai góc nhìn ở `/download#cach-hoat-dong` bằng ba dòng chữ hiện theo cuộn và bốn ảnh người dùng cung cấp, theo thứ tự 2.jpg → 1.jpg → 3.jpg → ảnh cuối. Hover mở rộng ảnh và hiện chức năng; bấm mở ảnh lớn, chuyển ảnh bằng nút/phím. Giữ Jinja2/CSS/JS, nội dung đọc được trên cảm ứng, reduced motion và khi tắt JS. [Bằng chứng](evidence/d052-how-gallery/README.md)

## D051 — 2026-11-07: làm gọn auth và căn hai góc nhìn

Đã bỏ dòng giải thích app/link tải dưới form login/register; tăng nhẹ chữ phụ/nhãn nhập, giữ Segoe UI thực tế. Hai tiêu đề Phía phụ huynh/Phía con căn cùng mép trên, không còn lệch theo chiều cao nội dung. Đo 24 bố cục và ba mốc cuộn, reduced motion: đạt. [Bằng chứng](evidence/d051-auth-layout/README.md)

## D050 — 2026-11-07: con dùng app Windows, không đăng nhập web

Đã tích hợp cửa sổ native `Hôm nay của em` vào tray: giờ thực trên máy/quỹ giải trí, hoạt động/audit và xin5/10/15 phút. Dùng danh tính thiết bị đã ghép, hàng đợi offline và IPC xác thực. Parent UI/hướng dẫn không còn yêu cầu tài khoản web cho con. Bộ cài1.0.1 đã tạo lại và kiểm tra UI bằng chính runtime đóng gói; server8446 đã cập nhật. Windows service/DNS trên child lab vẫn chưa nghiệm thu. [Hướng dẫn](CHILD_APP.md) · [Bằng chứng](evidence/d050-child-native/README.md)

## D049 — 2026-11-07: đăng ký phụ huynh và hướng dẫn bắt đầu

Đã có `/register`: tên, tài khoản, mật khẩu và nhập lại; tạo thành công chuyển sang đăng nhập. Tên mã hóa, mật khẩu scrypt; migration v3 giữ tài khoản cũ. Trang tải có nút bo tròn đăng ký/đăng nhập, bỏ hướng dẫn dòng lệnh và liên kết tắt bước 3, bỏ nút dừng tin nhắn theo yêu cầu, FAQ đổi thành 5 câu thân thiện. 93 test server đạt; kiểm tra 18 bố cục và luồng trình duyệt trên DB QA. Web 8446 đã cập nhật, đã sao lưu DB trước migration. [Bằng chứng](evidence/d049-registration/README.md) · [Lưu tài khoản khi deploy](ACCOUNT_SETUP.md)

## D048 — 2026-11-07: chuyển động trang tải theo video

Đã xem `vid.mp4` (48,57 giây) và áp dụng chuyển động tin nhắn có nút dừng, thanh điều hướng cố định, hai góc nhìn giữ vị trí khi cuộn và thẻ cài đặt thu nhỏ/xếp lớp. Đã kiểm chứng 7 kích thước, reduced motion, cảm ứng, tải bộ cài và chuyển hướng đăng nhập. D047 hover CTA trên cảm ứng đã sửa; hai lỗi focus/menu dashboard vẫn còn. [Bằng chứng](evidence/d048-video-motion/README.md)

## D047 — 2026-11-07: đánh giá UI và animation

Đã rà 12 trang gồm trang tải, 9 trang phụ huynh, trang trẻ và đăng nhập. Có 66 lượt đo bố cục ứng dụng không tràn ngang/chữ dưới 14px. Ba điểm cần sửa được xác nhận bằng Chrome gồm polling làm mất focus, menu mobile thiếu đóng Escape/quản lý focus và hover CTA trên cảm ứng. [Báo cáo đánh giá](../plans/UI_ANIMATION_AUDIT_2026-11-07.md)

## D046 — 2026-11-07: bộ 9 skill Emil mặc định

Đã cài 9 skill người dùng gửi vào `.agents/skills/`, kèm 5 tài liệu phụ trợ. AGENTS chỉ định cách phối hợp với Taste Skill cho các tác vụ thiết kế, animation, đánh giá và prototype trong KidSafe. [Bằng chứng](evidence/d046-emil-skills/README.md)

## D045 — 2026-11-07: Taste Skill 2.5.0 mặc định

Đã nâng skill thiết kế cục bộ lên 2.5.0 bằng tệp người dùng gửi và bộ tài nguyên chính thức. AGENTS yêu cầu áp dụng cho mọi công việc giao diện tiếp theo trong KidSafe. [Bằng chứng cài đặt](evidence/d045-taste-skill/README.md)

## D044 — 2026-11-07: hiệu ứng cuộn và hướng dẫn trang tải

Trang tải Windows có hội thoại mẹ và con, hai góc nhìn chuyển động ngược hướng khi cuộn, ba thẻ cài đặt xếp lớp, FAQ với nút mở có viền xanh và lời kết ngắn. Bước đăng nhập đứng trước bước quản lý hồ sơ con. Xem [kiểm chứng](evidence/d044-download-motion/README.md).

## D043 — 2026-11-07: trang tải theo phong cách Linea

Trang tải Windows dùng ảnh phủ nền tông navy, nút xanh và các lớp bo tròn. Phần hướng dẫn có xem trước tương tác cho ba bước ghép đôi. Xem [kiểm chứng](evidence/d043-linea-download/README.md).

## D042 — 2026-11-07: bộ cài Windows x64

Trang `/download` có bộ cài Windows chứa runtime. Phụ huynh lấy tệp kết nối từ dashboard rồi nhập mã ghép đôi trong wizard trên máy con. Xem [hướng dẫn](WINDOWS_SETUP.md) và [kiểm chứng](evidence/d042-windows-setup/README.md). Cài/gỡ, SCM, ACL, tray và DNS thật vẫn chờ máy Windows sạch.

## 2026-11-05 — Preview phụ huynh trên Streamlit

Bản xem trước riêng dùng giao diện KidSafe và dữ liệu minh họa. Người xem đi từ đăng nhập demo vào Tổng quan, rồi mở các trang phụ huynh. Đã kiểm tra gói ZIP chạy độc lập trong Chrome. Xem [kiểm chứng](evidence/streamlit-preview/README.md) và [hướng dẫn tạo gói và deploy](../demo/streamlit_preview/README.md).

Gói `KidSafe-streamlit-upload.zip` dùng tệp rời để tải qua trình chọn tệp GitHub. Đã chạy lại luồng preview trên Chrome từ gói này.

## D041 — 2026-11-05: giờ giải trí và nhật ký trên trang trẻ

Trang trẻ hiển thị thanh giải trí riêng theo dữ liệu báo cáo. Nút xin giờ rộng và nằm giữa đáy thẻ. Hai trạng thái trống có minh họa SVG. Nhật ký phân biệt khóa, mở khóa và thay đổi trung tính. Xem [kiểm chứng](evidence/d041-child-polish/README.md).

## D040 — 2026-11-05: Hôm nay của em

Trang trẻ có lời chào, thẻ thời gian và nhật ký màu sáng, bỏ topbar/footer và thông tin từng máy. Trẻ chọn 5, 10 hoặc 15 phút để xin thêm. Phụ huynh thấy đúng số phút và có thể duyệt, máy áp dụng qua lệnh có chữ ký. Xem [kiểm chứng](evidence/d040-child/README.md).

## D039 — 2026-11-05: nhật ký dễ đọc

Phụ huynh và trẻ xem cùng 10 thay đổi mới nhất dưới dạng danh sách có biểu tượng, câu mô tả và giờ địa phương. API riêng chỉ trả các trường cần hiển thị. Xem [kiểm chứng](evidence/d039-audit/README.md).

## D038 — 2026-11-05: ghép đôi, báo cáo và điều khiển demo

Thiết bị có mã ghép đôi 8 ký tự, đồng hồ 10 phút và đặt lại mật khẩu khi trẻ đã có tài khoản. Điều khiển nhanh có dropdown vô hiệu khi chưa ghép máy. Lệnh mở khóa mới kết thúc ở nửa đêm theo múi giờ hồ sơ hoặc khi nhận Khóa máy ngay. Báo cáo có lưới nhẹ, hai thẻ thống kê và tệp CSV tuần. Xem [kiểm chứng](evidence/d038-demo/README.md).

## D037 — 2026-11-05: bộ lọc website

Trang Lọc website có sáu công tắc danh mục và một công tắc SafeSearch tự lưu. Thêm/xóa tên miền qua thẻ. Trình duyệt tách hostname khỏi URL khi dán hoặc rời ô, server chuẩn hóa theo danh sách hậu tố có sẵn. Mỗi thay đổi cập nhật đúng phần lọc website, tăng version nếu dữ liệu đổi và ghi audit. Xem [kiểm chứng](evidence/d037-web/README.md).

## D036 — 2026-11-05: năm nhóm ứng dụng

Trang Ứng dụng dùng khung rộng chung, có năm nhóm và phần cấu hình mở theo hàng. Phụ huynh chọn tên tệp và SHA-256, chế độ quỹ, khung giờ và lời nhắn. SHA-256 tính tại trình duyệt. Lời nhắc trên trang Thời gian & lịch giải thích quỹ giải trí nằm trong hạn mức ngày.

Server ký và audit chính sách nhóm. Agent so tên hoặc SHA-256, trừ quỹ theo thời gian dùng ứng dụng đang ở foreground và đóng tiến trình bị khóa sau khi cửa sổ giải thích đã hiển thị. Dữ liệu từ máy khác được áp dụng sau đồng bộ. Cần cài agent mới trên lab trẻ để thực thi và nghiệm thu Windows. Xem [kiểm chứng](evidence/d036-app-groups/README.md).

## D035 — 2026-11-05: kiểm tra lịch và thực thi quỹ giải trí

Trang Thời gian & lịch có kiểm tra hạn mức ngay khi nhập, thước giờ chung với lưới 7 × 48, tổng giờ theo ngày và cảnh báo ngày có khung giờ ngắn hơn hạn mức. Hai nút lưu chỉ lưu phần tương ứng. Chuyển nút đổi phần chia offline sang Thiết bị & ghép đôi.

API từ chối quỹ giải trí lớn hơn một trong hai hạn mức ngày. Policy cũ vượt trần được hạ riêng quỹ giải trí, tăng version và ghi audit. Agent đóng các ứng dụng đã chọn khi tổng thời gian cục bộ cộng số giây đã đồng bộ từ máy khác đạt quỹ. Kiểm thử tự động qua tiến trình giả lập, vẫn cần chạy bản agent mới trên lab Windows. Nếu nhiều máy dùng song song hoặc offline, phần sử dụng chưa đồng bộ có thể vượt quỹ tổng. Xem `evidence/d035-time/README.md`.

## D034 — 2026-11-05: điều khiển riêng và quỹ giải trí

Đã tạo `/app/quick-control` với chọn máy/Online/Offline/ba thẻ lệnh; Tổng quan bỏ quick controls, đổi thẻ phải thành Công cụ & Kiểm soát với thống kê app/domain và hai link. Form quota ba cột có phút giải trí; trang Ứng dụng chọn nhóm.exe theo câu trả lời của người dùng. KPI dùng counter foreground riêng qua heartbeat, footer KPI thẳng hàng; nhãn Đang xem nowrap.

Policy cũ upgrade có version/audit, giữ quota thường/cuối tuần. Counter durable theo ngày/nhóm, không thêm event; thông tin thiếu từ agent cũ được báo rõ. **Chưa có tự chặn khi hết quỹ giải trí hoặc phân bổ offline theo nhóm**; NC/G-UI chưa đóng.

108 ca duy nhất đạt khi chia105core và3TLS; một test core được chạy lại trong nhómTLS. Hai lần fullsuite trước có lỗi IPC/WebSocket Windows, log giữ trong evidence. 18browserchecks và66layoutchecks đạt; đã xem33ảnh cuối. Hai profile8443/8446 đã backup/nạp lại/smokeTLS có CA đạt. Chi tiết: `docs/evidence/d034-controls/README.md`. SourceZIP cũ chưa dựng lại; chưa có nghiệm thu nativeWindows mới.

## D033 — 2026-11-05: rà chữ và cập nhật dashboard phụ huynh

Đã sửa theo file tinh chỉnh người dùng: thang chữ, tài khoản một dòng, gear audit/xóa/logout, bảy icon sidebar, bỏ footer/phụ đề, ba KPI bằng chiều cao, progress theo ngưỡng, quick actions và thống kê/lịch. Sửa tràn trang lịch và select ứng dụng trên phone/tablet. Reports phân biệt pending/sent/ACK, giữ pending ngoài cửa sổ 7 ngày và đếm tổng tuần trước giới hạn danh sách.

Chrome kiểm **10 trang × 6 chiều rộng**, không tràn trang/text dưới14px/tiêu đề dashboard quá2dòng/JSexception; đã xem 30 ảnh cuối. **46 test backend**, **1 test TLS/WebSocket thật** và **15 browser checks** đạt; hai test report được chạy lại trong XML TLS. Xem `docs/evidence/parent-refinement-2026-11-05/README.md`.

Giữ stack Jinja2/HTMX/CSS local. Ô giải trí hiện chưa có hạn mức riêng vì backend chưa triển khai NC counter nhóm; không bịa số. Thẻ cân bằng dùng lịch hiện tại, không giả thống kê giờ cao điểm. Chưa có bằng chứng native Windows mới; sourceZIP cũ chưa được dựng lại cho thay đổi này. Đã nạp lại server8443/8446 và smoke TLS có kiểm CA/login/read/logout đạt, giữ database hiện có. Các trạng thái chuẩn bị và số test bên dưới là lịch sử.

## Điều kiện lab mới D029

Người dùng chỉ có một máy vật lý. Hướng dẫn ONE_PC_SETUP: host web/server + WindowsVM agent, bắt đầu mộtVM. Đã chuẩn bị profile .runtime/vm cóSANlocalhost/10.0.2.2, port8446 loopback; chưa tìm thấy VirtualBox trong đườngdẫn cài thôngdụng, chưa tạoWindowsVM hoặc testnativeagent. Không dùng hướng dẫn haiPC làm mặcđịnh hiện tại. Quyền tự làm/kiểm tra đã cấp vẫn giữ; không giả định người mới đã cóVM/ISO hay biết thao tácquảntrị.

## Bản ứng dụng sau D028 — trạng thái mới nhất

Kết quả chốt: **92 test đạt**, **19 browser check đạt**, inspector app không có finding; venv mới cài47gói từ lock/import được. Có Start-KidSafe.ps1, hướng dẫn và sourceZIP ở releases/KidSafe-source.zip sau đóng gói. Không coi là đồ án đã sẵn sàng nộp: phần bằng chứng Windows/mạng và Word/PDF/video nộp vẫn còn.

Đã triển khai cả hai giao diện Jinja2/HTMX và nối API thật. Parent theo Design-PH nền giấy sáng/xanh rêu; child mint/kem, thời gian/hoạt động/xin giờ/audit. Có bộ cài/gỡ service, tray nhìn thấy, giám sát ứng dụng/hộp thoại giải thích, DNS IPv4/IPv6 và snapshot/restore, cache/quota/shared allocation, WebSocket/pinning, auth/ownership/CSRF, retention/xóa có ACK.

Đã chạy kiểm thử lõi/API/HTML/đóng gói, Chrome thực kiểm form/HTMX/childrequest/403 và screenshots1440/768/390; kết quả cuối trong docs/evidence. Đã tạo một venv mới và cài lại47 gói đúng lockfile để kiểm import backend/agent. Hồ sơ “An · hồ sơ demo” do kiểm thử browser tạo, dữ liệu giao thức tổng hợp, không phải ghi hoạt động Windows thật.

Theo chỉ đạo D028, G-UI không ngăn hoàn thiện mã/giao diện khi thiếu lab; vẫn **chưa đạt nghiệm thu Windows user thường**. Chưa tự sửa DNS/cài service/khóa host. Còn phải thử trên máy trẻ/VM: ACL/SCM/logon/logoff/icon, khóa/app terminate thực, DNS Windows/nslookup/SafeSearch browser, chống bypass, số đo1giờ và M1–M6. Báo cáo Word/PDF/video cuối của đồ án chưa có; không gọi sẵn sàng nộp.

Điểm tiếp tục sau bản app này: chạy lab theo agent/README và đối chiếu REQUIREMENTS bằng bằng chứng thật; không dựng lại UI hay đọc lại toàn bộ hồ sơ từ đầu. Người dùng đã cho quyền tự thực hiện, không hỏi lại quyền thao tác thường lệ.

## Trạng thái hiện hành sau lệnh bắt đầu (2026-11-04)

**Đang triển khai theo D027.** Mô tả chưa triển khai bên dưới được giữ làm lịch sử chuẩn bị. Xem [IMPLEMENTATION_LOG](IMPLEMENTATION_LOG.md).

- S1: venv Python 3.12.14, dependency và lockfile; scripts tạo CA/TLS/cấu hình private và seed tài khoản demo đã chạy được.
- S2/S3: backend đang triển khai/rà soát, chưa đóng nghiệm thu.
- S5/S6/S7: policy/cache/counter/apps/DNS và adapter Windows đang triển khai/rà soát. Đã chạy 23 test agent đạt gồm DNS TCP/UDP loopback; chưa thử service LocalSystem/DNS Windows thật.
- TLS: 3 kiểm thử đạt gồm kết nối thật và từ chối CA không tin cậy. Kiểm thử tích hợp HTTPS backend-agent đang chạy lại sau sửa lỗi xử lý domain.
- G-UI chưa đạt. Windows 11 Home x64 hiện tại chưa tìm thấy VM/máy trẻ/Wireshark. Chưa đổi DNS/firewall/trust store hoặc cài service trên host.
- Bảng mẫu 234 mục/sáu nhóm đã tạo, provisional_manual; chưa coi số dòng là bằng chứng phân loại đúng hoặc phép đo DNS đạt.

Kết quả mới nhất: **54 test đạt**, XML ở `docs/evidence/pytest-2026-11-04.xml`. Runtime/service entry và sync đã nối ở mức mã; chưa được nghiệm thu. Backend script thực tế đã chạy, smoke TLS/login/read/logout đạt và đã dừng sau kiểm tra. Điểm tiếp tục chi tiết trong `agent/README.md` và `IMPLEMENTATION_LOG.md`; UI vẫn chờ G-UI. Các agent phụ đã dừng do giới hạn sử dụng, phiên chính hoàn tất đợt kiểm chứng này.

Chưa có dashboard/báo cáo/video cuối hoặc tuyên bố sẵn sàng nộp. Các việc thiếu lab vẫn phải ghi rõ.

Cập nhật: 2026-11-04, Asia/Saigon. **Hồ sơ chuẩn bị bản 1 có bổ sung nguồn thiết kế phụ huynh, sẵn sàng để người dùng rà soát. Chưa triển khai phần mềm.**

## Đã thực hiện

- Đọc toàn bộ văn bản DoAn01, gồm nội dung bảng, sơ đồ chữ, header/footer; đối chiếu bản gợi ý Gemini được cung cấp.
- Lưu bản trích nguồn, mã băm nguồn và ma trận yêu cầu có locator Pxxx.
- Ghi các thiếu sót, hiểu sai và chỗ mơ hồ trong GEMINI_REVIEW/REQUIREMENTS.
- Lập sổ brainstorming, kế hoạch từng bước, thiết kế nháp, kế hoạch kiểm chứng và kế hoạch hồ sơ nộp.
- Khởi tạo nội dung privacy, threat model và khai báo AI ở trạng thái dự kiến/chưa triển khai.
- Bổ sung quy tắc bám đề và giới hạn chưa bắt đầu vào AGENTS.md, giữ nguyên hướng dẫn kho đã có.
- Lưu nguyên bản sáu ảnh UI người dùng gửi, lập UI_DESIGN_BRIEF; bổ sung D022–D024 và đổi thứ tự sang backend/mạng→G-UI→dashboard. Chưa dựng UI, mockup hoặc nhân vật.
- Theo quyền D025, tải UI UX Pro Max vào `.local-tools/design-skills/ui-ux-pro-max/` ở commit cố định, kèm LICENSE/README/metadata; đọc và thử sáu truy vấn domain, ghi DESIGN_SKILL_REVIEW. Không cài gói toàn cục hay tạo code sản phẩm; `.local-tools/`/`.tmp/` có gitignore.
- Ngày 2026-11-04, đã thấy và đọc toàn bộ `docs/Design-PH.md` do người dùng thêm; ghi D026 và đưa vào AGENTS/UI brief/kế hoạch S4 làm nguồn định hướng màu/style parent. Giữ nguyên nguồn, ghi hash; điểm YAML tối/prose sáng được để lại để thống nhất ở S4. Chưa tạo UI.

## Chưa thực hiện

Không có code sản phẩm, dependency sản phẩm, migration, service, cấu hình DNS/firewall/TLS, test KidSafe chạy, benchmark, dữ liệu 200 mục, ảnh Wireshark, báo cáo cuối hay video. Công cụ UI bên ngoài đã tải và tra cứu thử là nguồn tham khảo riêng, không được tính vào test sản phẩm. Không có commit/PR được tạo trong đợt chuẩn bị.

## Chờ người dùng

Đã ghi nhận: KidSafe; Jinja2 + HTMX; nhóm 3 người, còn 5 tuần; Windows 11 và quyền admin. Chưa có ngày nộp chính xác hoặc số máy. Máy trẻ phải có user thường.

Đã cập nhật B004/B005/B007/B008: server LAN riêng, N=3 ngày/fail-closed giữ policy cuối, quota chung theo trẻ, cảnh báo nhẹ nhàng/lưu bài/xin giờ.

Đã cập nhật B010/B011: chia trước ngân sách offline từng máy, tổng không vượt quota, điều chỉnh khi có mạng; mở khóa ngoài lịch cho ngoại lệ 15 phút, có audit rồi quay về lịch/quota.

Đã cập nhật B013/B009: Cộng 15 tăng quota chung không bỏ lịch; Mở khóa cho tối đa 15 phút dù ngoài lịch/quota hết, ghi phần giờ ngoại lệ; Khóa ngay hủy ngoại lệ; vẫn giữ app/domain rules. Sau BB ưu tiên NC DoH/chống đổi DNS.

Đợt 6 đã trả lời đủ: chỉ có DoAn01; ghi điểm chưa rõ để hỏi giảng viên; chuẩn bị theo 60 giây cuối trong quota (3 phút khóa ở phút 3), chưa được giảng viên xác nhận; để trống phân công, người dùng cung cấp thông tin sau.

Bổ sung mới: ảnh lớp dùng tham khảo bố cục/luồng, ảnh Pinterest dùng tham khảo màu/vibe trẻ em; hoàn thiện backend và mạng bắt buộc trước rồi mới thiết kế UI. Palette cụ thể trong brief là gợi ý, không phải quyết định đã được người dùng duyệt.

Phạm vi màu/style đã được cụ thể hóa bởi D026: **parent ưu tiên Design-PH.md**, child-view vẫn theo Pinterest. Theme sáng/tối cuối của parent chưa chốt vì nguồn có hai mô tả; không cần hỏi thêm ở đợt ghi nhận này, thống nhất khi bắt đầu phần thiết kế.

1. Người dùng rà soát bộ hồ sơ, không còn câu hỏi brainstorming đang chờ trả lời trong sáu đợt đã hỏi.
2. Chờ thông tin thành viên sau theo yêu cầu; không tự phân công hoặc bịa % đóng góp. Chi tiết kỹ thuật IPC/lifecycle/ordering/hạch toán được đề xuất có lý do trước bước liên quan.
3. Các câu hỏi trong QUESTIONS_FOR_INSTRUCTOR chờ phản hồi thật của giảng viên; không coi phương án tạm là đã được chấp nhận. Những điểm này đã được ghi rõ trong hồ sơ để người dùng kiểm tra.
4. **Duyệt tài liệu chưa phải lệnh làm phần mềm.** Chờ yêu cầu bắt đầu rõ ràng.

## Điều kiện đóng giai đoạn chuẩn bị

- [x] Đọc đề và phân biệt nguồn yêu cầu với gợi ý Gemini.
- [x] Có ma trận BB/NC/CTT và danh sách sản phẩm nộp.
- [x] Có phần thiếu/sai và phương án bổ sung.
- [x] Có sổ ghi quyết định, kế hoạch và lệnh ghi nhớ.
- [x] Có khung privacy/threat model/AI, kiểm chứng và báo cáo.
- [x] Có thông tin nhóm 3 người, còn 5 tuần, Windows 11/admin; LAN với server và máy trẻ riêng; ngày nộp chính xác còn chờ.
- [x] Chốt tên, dashboard, server, N=3 ngày/fail-closed, quota chung theo trẻ và lời nhắc nhẹ nhàng.
- [x] Chọn phân bổ trước ngân sách offline; mở khóa ngoài lịch 15 phút có audit.
- [x] Chốt bộ lệnh khi quota cạn/ngoài lịch và ưu tiên NC DoH/chống đổi DNS.
- [x] Ghi phương án ân hạn trong quota để xin xác nhận; phân công để trống theo D021.
- [x] Lập danh sách điểm mơ hồ nguồn, phương án tạm và file câu hỏi giảng viên; người dùng biết chưa có xác nhận.
- [x] Lưu sáu ảnh tham khảo, định hướng UI và cổng G-UI/thứ tự sau backend-mạng theo yêu cầu bổ sung.
- [ ] Người dùng kiểm tra hồ sơ chuẩn bị.
- [ ] Người dùng yêu cầu bắt đầu triển khai rõ ràng.

Phần tạo hồ sơ chuẩn bị đã hoàn thành bản 1. Việc giảng viên xác nhận, thông tin thành viên, rà soát của người dùng và lệnh bắt đầu là các mục còn lại; không đánh dấu chúng đã xong thay người dùng.

## Điểm tiếp tục cho lần sau

Đọc AGENTS → file này → BRAINSTORM_NOTES → REQUIREMENTS → IMPLEMENTATION_PLAN. Nếu người dùng vừa trả lời câu hỏi, cập nhật sổ trước; hỏi đợt tiếp theo 2–3 câu cần thiết. Nếu được yêu cầu bắt đầu, kiểm tra các quyết định đang chờ có ảnh hưởng đến hạng mục sắp làm rồi bắt đầu S1 theo kế hoạch; không làm lại việc đọc/đối chiếu đã xong trừ khi nguồn thay đổi.

## Kiểm tra bộ tài liệu ngày 2026-11-03

- Đã kiểm tra bộ hồ sơ sau bổ sung công cụ UI: 17 Markdown root/docs, 30 liên kết nội bộ hợp lệ, 66 ID yêu cầu và 25 ID quyết định không trùng; UTF-8/code fence/thứ tự G-UI trước S4 đúng, sáu PNG giữ nguyên. 76 file nguồn của bản tải khớp Git blob hash tại commit, SOURCE.json ghi metadata cục bộ; gitignore che đúng công cụ/đầu ra tạm. Chưa có kiểm thử UI KidSafe vì chưa triển khai.
- Ma trận có 66 dòng yêu cầu với 66 ID duy nhất; bao gồm bối cảnh, kiến trúc/giao thức, F1–F5, M1–M6 và sản phẩm nộp. Con số này là cách phân nhóm để truy vết, không phải số tiêu chí chính thức của giảng viên.
- Bản Gemini lưu lại giống từng byte với bản người dùng gửi; bản trích DoAn01 khớp mã băm đã ghi. Word không có tracked insert/delete hoặc hình vẽ trong phần document.
- `git diff --check` không báo lỗi khoảng trắng; đã rà tính nhất quán KidSafe/Jinja2 + HTMX/5 tuần. `.agents/` là dữ liệu có sẵn, không bị sửa.
- Đây là kiểm tra tài liệu. Không có test phần mềm hoặc đo hiệu năng được chạy và không có kết quả nghiệm thu sản phẩm.

## Giới hạn kiểm tra nguồn hiện tại

Kiểm tra bổ sung ngày 2026-11-04: 18 Markdown root/docs, 34 liên kết nội bộ hợp lệ, đủ 26 ID quyết định D001–D026 không trùng; ma trận vẫn 66 yêu cầu. SHA-256 Design-PH.md khớp lúc nhận, nguồn không bị sửa. UTF-8/code fence và diff whitespace không lỗi; đây là kiểm tra tài liệu, chưa chạy phần mềm/UI.

Đã trích và đọc văn bản XML đầy đủ; phần document không có đối tượng hình vẽ. Công cụ render Word đóng gói đã được thử nhưng không chạy vì máy không có `soffice.exe` trên PATH. Vì thế chưa kiểm tra bố cục trang bằng ảnh, không trích số trang và không khẳng định đã xem hình trang Word. Các locator Pxxx chỉ là số đoạn trong bản trích. Không cần sửa/cài ứng dụng để hoàn thành việc chuẩn bị văn bản này.

Bàn giao demo LAN 2026-11-20. Codex kiểm tra 158 test đạt, 31 thao tác trình duyệt đạt và smoke test cửa sổ native đạt với dữ liệu mẫu. Đối chiếu SHA-256 bộ cài. Bổ sung hướng dẫn docs/DEMO_HAI_MAY.md và sửa launcher hiển thị địa chỉ bind, đánh dấu dependency sau khi cài thành công. Nghiệm thu service, DNS và khóa máy trên máy con thật vẫn cần thực hiện.
