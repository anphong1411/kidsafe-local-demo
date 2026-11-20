# Khai báo sử dụng AI cho đồ án KidSafe

## D057 — Kiểm tra và chuẩn bị gói phát hành

Codex dùng Taste/Emil để rà bố cục và thao tác, tái hiện và sửa race sidebar, làm rõ trạng thái báo cáo giải trí, cập nhật luồng cài trên web và hướng dẫn LAN. Đối chiếu tài liệu GitHub/Streamlit, chọn GitHub Pages cho tải bộ cài theo quyền tự quyết của người dùng. Build bộ cài bằng công cụ có sẵn, kiểm pytest, Chrome và cửa sổ native bằng dữ liệu thử. Không dùng dữ liệu thật để phát hành. [Bằng chứng](evidence/d057-download/README.md)

## D056 — Shader và kiểm tra toàn web

Codex tích hợp shader do người dùng cung cấp, viết WebGL lifecycle/fallback, chỉnh menu và phối hợp hai tác vụ phụ đọc mã để rà landing/dashboard. Một tác vụ phụ triển khai các lỗi dashboard/auth đã được xác nhận; Codex đọc lại và kiểm chứng bằng Chrome trên DB QA. Dùng Taste/Emil và các skill chuyển động phù hợp, kiểm tra ma trận 13 trang, shader lifecycle, bàn phím và auth fallback; chạy 54 test. Không sinh ảnh, cài thư viện, đổi DNS hay cài agent trên host. [Bằng chứng](evidence/d056-web-polish/README.md)

## D055 — Hiệu chỉnh theo ảnh mẫu

Codex nhận đính chính từ người dùng, thay cách hiểu viền chữ D054 bằng nền tối chuyển sắc, thêm heading và kiểm tra lại Chrome. Ảnh gốc, dependency và backend không đổi. [Bằng chứng](evidence/d055-gradient/README.md)

## D054 — Caption trắng trong ảnh

Codex sửa CSS vị trí/chữ và bỏ hàm đo caption không còn dùng; kiểm tra Chrome và xem ảnh desktop/mobile. Giữ nguyên bốn ảnh, không sinh tài nguyên hoặc thêm dependency. [Bằng chứng](evidence/d054-caption/README.md)

## D053 — Gallery gọn và ảnh rõ màu

Codex dùng Taste, Emil, animate và review-animations để sửa template/CSS/JS theo bốn ảnh phản hồi: giảm chữ và khoảng trắng, bỏ phủ tối ảnh, thêm pill chức năng, giữ một câu mô tả. Đo typography/khoảng cách/tương phản, kiểm tra chuyển động và khả năng truy cập bằng Chrome, dùng checker Taste. Không sinh/chỉnh ảnh hoặc thêm dependency. [Bằng chứng](evidence/d053-clear-gallery/README.md)

## D052 — Giới thiệu và gallery ảnh

Codex viết lại HTML/CSS/JS của phần Cách hoạt động từ yêu cầu và component tham khảo do người dùng dán, dùng Taste/Emil/animate và rà theo review-animations. Bốn ảnh do người dùng cung cấp được sao chép nguyên byte, không sinh hoặc chỉnh ảnh. Đo tương tác bằng Chrome CDP, chạy checker của Taste và kiểm thử download. Không thêm React/npm, không đổi backend hay bộ cài Windows. [Bằng chứng](evidence/d052-how-gallery/README.md)

## D051 — Căn bố cục và rà chữ

Codex dùng Taste/Emil, đo font và vị trí bằng Chrome, sửa HTML/CSS rồi kiểm tra ba trang ở tám kích thước, xem ảnh desktop/mobile. Giữ ảnh và hệ phông đã có, không sinh tài nguyên mới. [Bằng chứng](evidence/d051-auth-layout/README.md)

## D050 — Giao diện app Windows của con

Codex triển khai UI Win32 native, nối tray/service và API đọc theo thiết bị, thêm kiểm thử request/ownership/cache và sửa hướng dẫn theo lựa chọn app-only của người dùng. Dùng GDI/Pillow có sẵn, không sinh ảnh hay cài thư viện UI mới. Đã mở cửa sổ mẫu và thử lại với runtime đóng gói; ảnh bằng chứng dùng dữ liệu mẫu và chỉ chụp cửa sổ kiểm tra. [Bằng chứng](evidence/d050-child-native/README.md)

## D049 — Đăng ký phụ huynh và sửa luồng trang tải

Codex triển khai API/form đăng ký, migration tên mã hóa, sửa hướng dẫn và viết 5 câu FAQ theo yêu cầu. Dùng Taste/Emil cho giao diện, giữ ảnh hiện có; không tạo ảnh mới. Kiểm thử server, lưu tài khoản qua khởi động lại, phiên chưa đăng nhập/đăng xuất và thao tác Chrome trên dữ liệu QA. [Bằng chứng](evidence/d049-registration/README.md)

## D048 — Chuyển động dựa trên video người dùng

Codex trích khung hình video cục bộ, đối chiếu mẫu Linea, chỉnh CSS view timeline và viết JavaScript đo bố cục/quản lý dừng tin nhắn. Dùng Taste Skill, animate và Emil; rà sau sửa theo review-animations. Ảnh AI cũ được tái sử dụng, không sinh ảnh mới. [Kiểm chứng](evidence/d048-video-motion/README.md)

## D047 — Đánh giá giao diện và animation

Codex dùng các skill Taste/Emil và hai tác vụ phụ đọc mã để rà dashboard, trang tải, preview và tray. Codex kiểm tra lại các phát hiện bằng Chrome và loại hai giả thuyết không tái hiện. [Báo cáo](../plans/UI_ANIMATION_AUDIT_2026-11-07.md)

## D046 — Bộ skill Emil

Codex đọc các tệp được gửi, xác nhận nguồn bằng mã băm, tải tài liệu phụ trợ và cài 9 skill vào dự án. Quy tắc phối hợp với Taste Skill được ghi trong AGENTS. [Kiểm chứng](evidence/d046-emil-skills/README.md)

## D045 — Cài Taste Skill 2.5.0

Codex đọc tệp người dùng, đối chiếu mã băm với nguồn chính thức, cài bộ tài nguyên theo commit và kiểm tra script. Cấu hình áp dụng cho công việc giao diện toàn dự án được ghi trong AGENTS. [Kiểm chứng](evidence/d045-taste-skill/README.md)

## D044 — Hiệu ứng cuộn và luồng cài đặt

Codex đối chiếu nguồn Linea, dùng CSS view timeline để dựng hiệu ứng cho nội dung KidSafe và viết lời kết mới. Đã kiểm tra bằng Chrome và thử cấp tài khoản trong cơ sở dữ liệu riêng. [Kiểm chứng](evidence/d044-download-motion/README.md)

## D043 — Giao diện trang tải lấy cảm hứng từ Linea

Codex phân tích mẫu Linea, dựng lại bố cục bằng Jinja và CSS, tạo ảnh hero bằng ImageGen và kiểm tra trên Chrome. [Ảnh và prompt](evidence/d043-linea-download/README.md)

## D042 — Trang tải và bộ cài Windows

Codex đóng gói runtime Python bằng Inno Setup, tái dùng script đăng ký service/tray, viết cửa sổ ghép đôi và triển khai trang tải Jinja. Codex dùng design-taste-frontend với hướng One motif, minh họa hai nửa mã ghép bằng SVG và kiểm tra trên Chrome. Kiểm tra runtime dùng hồ sơ QA. Chưa nghiệm thu Windows sạch.

## Preview phụ huynh trên Streamlit

Codex đóng gói template và tài nguyên KidSafe có sẵn, viết luồng đăng nhập demo qua Streamlit Secrets, tạo dữ liệu minh họa và kiểm tra gói chỉ chứa các tệp preview. Tài khoản để chia sẻ do người deploy đặt.

Codex bổ sung gói tệp rời và chạy lại luồng trên Chrome để hỗ trợ tải tệp qua trình duyệt.

## D041 — Tinh chỉnh trang trẻ

Codex thêm thanh giải trí, vẽ mèo ngủ và hộp thư bằng SVG, phân loại biểu tượng nhật ký và kiểm tra bố cục trong Chrome với dữ liệu QA.

## D040 — Trang trẻ và xin thêm giờ

Codex chỉnh giao diện Jinja/CSS/JS, vẽ lại gấu bằng SVG và nối số phút xin thêm đến lệnh đã duyệt. Chọn 5/10/15 phút trong phạm vi một lượt cộng theo D017/D038. Kiểm thử trên hồ sơ QA với thiết bị giả lập.

## D039 — Nhật ký dễ đọc

Codex tạo hàm tóm tắt, API 10 mục và bố cục danh sách chung cho phụ huynh và trẻ. Kiểm chứng bằng Pytest và Chrome trên dữ liệu QA. Xem [bằng chứng](evidence/d039-audit/README.md).

## D038 — Thiết bị, Điều khiển nhanh và Báo cáo

Codex kiểm tra giao diện bằng design-taste-frontend và Chrome, triển khai đồng hồ ghép đôi, đặt lại mật khẩu, xuất CSV và mốc hết hạn mới. Quyết định mốc hết hạn do người dùng xác nhận. Kiểm thử Windows dùng bộ đếm và tiến trình giả lập. Xem [bằng chứng](evidence/d038-demo/README.md).

## D037 — Lọc website

Codex triển khai công tắc, danh sách thẻ và xử lý dán URL trong JS/CSS. Dùng thư viện hậu tố đã có để chuẩn hóa phía server, bổ sung kiểm thử hồi quy và kiểm tra bằng Chrome với hồ sơ QA riêng. Xem [bằng chứng](evidence/d037-web/README.md).

## D036 — Năm nhóm ứng dụng

Codex triển khai giao diện Jinja2/CSS/JS và băm tệp qua Web Crypto. Cập nhật mô hình policy, heartbeat và quy trình chặn của agent. Dùng design-taste-frontend kiểm tra bố cục, Chrome và Pytest kiểm tra hành vi. Tiến trình Windows dùng trong test là giả lập. Xem [kiểm chứng](evidence/d036-app-groups/README.md).

## D035 — Lịch tuần và hạn mức giải trí

Codex sửa giao diện và kiểm tra dữ liệu, tích hợp bộ đếm giải trí vào chặn ứng dụng có thông báo, bổ sung kiểm thử hồi quy. Dữ liệu trình duyệt và tiến trình trong test là giả lập. Kết quả và giới hạn tại `evidence/d035-time/README.md`.

## D034 — 2026-11-05: trang điều khiển và giải trí theo ứng dụng

Codex hỏi định nghĩa nhóm giải trí, ghi câu trả lời user rồi triển khai Jinja/HTMX/CSS local, policy/stats/aggregate heartbeat và bộ đếm foreground durable. SVG icon code-native, giữ palette/type Design-PH, không tạo ảnh/thêm dependency. Chọn default gợi ý60phút cho field mới là quyết định triển khai, không giả người dùng đã chốt một quota; giữ quota thường/cuối tuần.

108testduynhất đạt theo105core+3TLS,18browserchecks,66layoutchecks; đã xem33ảnh. Log fullsuite từng lỗi socketWindows được giữ/ghi rõ; test mạng chạy lại theo nhóm đạt. Backup/nạp lại/smoke hai profile có CA đạt; chỉ hồ sơ QA tổng hợp được tạo/xóa. Quỹ mới chỉ theo dõi, chưa tự chặn hoặc phân bổ offline theo nhóm; chưa nghiệm thu Windows native. Xem `evidence/d034-controls/README.md`.

## D033 — 2026-11-05: rà chữ và tinh chỉnh parent dashboard

Codex đọc yêu cầu đính kèm, giữ nguyên nguồn; dùng design-taste-frontend nhánh app screens và Design-PH để rà typography/layout. Sửa Jinja/CSS/JS, thêm báo cáo trạng thái pending/sent/ACK và hai test hành vi. Không thêm thư viện runtime, đổi stack, bịa quota giải trí hoặc giờ cao điểm. SVG icon được viết trực tiếp, không tạo ảnh bằng AI.

Chrome thật đo10trang×6width, đã xem30ảnh cuối; 15 tương tác browser, 46test backend và một ca TLS/WebSocket pin thật đạt. Dữ liệu QA tổng hợp/profiletạm; xóa chỉ trên hồ sơ thử. Không nghiệm thu Windows native. Bằng chứng và ngoại lệ skill: `evidence/parent-refinement-2026-11-05/README.md`.

## D032 — 2026-11-05: ảnh đính kèm ở login

Codex dùng trực tiếp ảnh người dùng cung cấp, copy byte-identical vào tài nguyên local, không dùng imagegen/không chỉnh nội dung ảnh. Điều chỉnh CSS để giữ tỷ lệ và cân cột, thêm dấu chấm H1. Chrome kiểm8viewport, lỗi/đúng đăng nhập và đăng xuất; đã xem ảnh desktop/mobile, evidence login-family-image. Không suy ra kiểm chứng agentWindows từ thay đổi UI.

## D031 — SVG code-native và giản lược login

Codex vẽ SVG trực tiếp trong HTML theo yêu cầu người dùng, không dùng imagegen hay ảnh bên ngoài; không chèn chữ/số hiển thị, metadata truy cập nằm ngoài SVG. Bỏ mô tả/slogan và nối H1; giữ chức năng đăng nhập. Chrome đo8viewport, kiểm màu/chiều cao/zero-text/overflow và thử login sai/đúng/logout; đã xem ảnh desktop/mobile trong docs/evidence/login-connection. Chưa có thay đổi hoặc phép đo mới đối với agent Windows.

## D030 — UI đăng nhập

Codex dùng design-taste-frontend nhánh app screens và yêu cầu typography cụ thể của người dùng để sửa login.html/login.css; không tạo ảnh AI hoặc đổi palette. Tự đo và chụp8viewport bằng Chrome, xem ảnhdesktop/mobile, thử đăng nhập sai/đúng/logout, kiểm hồi quy auth liên quan. Evidence trong docs/evidence/login-refinement. Không chạy lại toàn bộ bộ92test cho thay đổi riêng template/CSS; không suy ra tính đúng của agent từ kiểm tra UI.

## D028 — bản app hoàn thiện mã và UI

Codex tiếp tục hoàn thiện hai giao diện Jinja2/HTMX, service/tray/appmonitor/DNS/installer/rollback, childaccount/request và các trường hợp ACK/cleanup. Parent theme sáng từ Design-PH là lựa chọn kỹ thuật được ủy quyền, không đổi nguồn người dùng. Bản cuối kiểm92test đạt, Chrome19bước đạt và ảnh1440/768/390; xem docs/evidence/README. Cài lại47dependency vào venv mới/import thành công. SourceZIP có manifest và loại bí mật/runtime.

Đã sửa lỗi phát hiện bởi chạy thật: HTMX giữ bodydataset cũ, giờ cộng chưaACK và giờ ngoại lệ bị cộng sai vào remaining, HTTP410 contract sauxóa, retryrefreshcleanup dài ngày, policyallocation pending. Agent tựrà bổ sung pystrayOSiconACK, venvredirector peeridentity và native lockobserver. Rà soát độc lập ở cuối gặp giới hạn sử dụng, không coi toàn bộ thay đổi đã được reviewer độc lập kiểm hết. Không điền thành quả sinh viên hoặc phần trăm đóng góp.

Không có test service/ACL/DNS/lock thật trên máy trẻ và không có đủ phụ lục mạng/báo cáo/video. Các lời khẳng định đạt bên trên chỉ giới hạn đúng test/bằng chứng đã chạy.

## Triển khai bắt đầu 2026-11-04

Theo D027, Codex tạo backend, lõi agent/adapter Windows, script TLS/lab, schema/data mẫu và bộ kiểm thử. Sol High xử lý backend/agent, Astra Low rà soát các lỗi bảo mật/replay/quota; agent phụ gặp giới hạn sử dụng, phiên chính tiếp tục hoàn thiện và kiểm tra. Không có đóng góp sinh viên hoặc % đóng góp được tự điền.

Đã kiểm: 54 test đạt theo docs/evidence/pytest-2026-11-04.xml, gồm real TLS và DNS loopback; script backend thật khởi động và smoke auth đạt. Các lỗi được sửa có retention/idempotency, policy version, PSL, serialized writes, deletion ACK retry và suspend counting. Chưa kiểm Windows service/user thường/ACL/tray/DNS adapter hoặc toàn bộ hệ thống; không gọi đây là kiểm chứng sinh viên đã làm. Dataset 234 dòng/sáu nhóm vẫn provisional_manual, không phải chứng nhận an toàn website. Các phần dự kiến phía dưới cần đối chiếu lại khi tới nghiệm thu.

Trạng thái: nhật ký chuẩn bị, chưa phải khai báo đã hoàn thành phần mềm. Khi nộp phải cập nhật theo công cụ/phần việc và kiểm chứng thực tế. Không ghi kết quả tự kiểm của AI thành kiểm tra của thành viên nếu chưa xảy ra.

## Nhật ký hiện có

| Ngày | Công cụ | Phạm vi hỗ trợ | Đầu ra | Kiểm chứng đã làm | Giới hạn/cần người kiểm tra |
| --- | --- | --- | --- | --- | --- |
| Trước 2026-11-03, chưa rõ ngày | Gemini, chưa rõ phiên bản | Gợi ý quy trình 6 bước/prompt, mẫu privacy/threat model và brainstorming | Pasted text người dùng cung cấp, giữ tại sources/GEMINI_ORIGINAL.txt | Codex đối chiếu nội dung nhận được với đề gốc | Bản nhận được bị cắt T8; không có nguồn cho [cite: 1]; chưa có code/test |
| 2026-11-03 | Codex trong ứng dụng desktop, không ghi phiên bản model khi chưa có thông tin xác nhận | Đọc Word, phân tích gap, tạo hồ sơ chuẩn bị và hỏi ý tưởng | AGENTS/README và bộ Markdown trong docs | Đọc toàn văn OOXML gồm bảng; đối chiếu yêu cầu/hash/locator; kiểm 13 Markdown, liên kết nội bộ, 66 ID duy nhất và diff whitespace; bản Gemini lưu byte-identical | Chưa render Word được vì thiếu soffice; chưa kiểm chứng sản phẩm; người dùng còn rà soát |

## Vai trò con người

- Người dùng quyết định tên KidSafe, Jinja2 + HTMX; xác nhận nhóm 3 người, còn 5 tuần, Windows 11 và quyền admin.
- Các đề xuất chưa được trả lời vẫn là đề xuất, không phải quyết định nhóm.
- Đã chọn bổ sung: server LAN riêng với máy trẻ; sau 3 ngày offline giữ quota/lịch cuối; quota chung theo trẻ; nhắc nhẹ nhàng/lưu bài/xin giờ. Codex cập nhật hồ sơ và bổ sung kịch bản kiểm thử nhiều máy/offline; chưa có triển khai hay kết quả test. B006 được trả lời bổ sung tại đợt 6 bên dưới.
- Người dùng chốt B010/B011: chia trước ngân sách offline từng máy, đổi khi có mạng; mở khóa ngoài lịch 15 phút có audit rồi trở về lịch/quota. Codex đề xuất ledger/giao dịch ACK để tránh cấp trùng, bổ sung privacy/threat/test tương ứng. Chưa có code/test; B012 được trả lời tại đợt 6 là chủ động để trống phân công.
- Người dùng chốt B013/B009: bộ lệnh D017 (cộng quota chung/ngoại lệ tối đa 15 phút khi ngoài lịch hoặc quota hết/khóa hủy ngoại lệ, giữ app/domain rules); ưu tiên NC DoH/chống đổi DNS sau BB. Codex đồng bộ kế hoạch/thiết kế/kiểm chứng và ghi rõ quota/grant/ngoại lệ; chưa có code/test.
- Đợt 6: người dùng xác nhận chỉ có DoAn01, chọn phương án ân hạn trong quota để xin giảng viên xác nhận, yêu cầu để trống phân công. Codex ghi D019–D021, tạo danh sách câu hỏi giảng viên và hoàn thiện hồ sơ chuẩn bị bản 1 gồm 14 Markdown; không thay lời giảng viên, không điền đóng góp và không triển khai sản phẩm.
- Kiểm tra bàn giao bản 1: 14 Markdown/15 liên kết nội bộ hợp lệ, 66 ID yêu cầu và 21 ID quyết định không trùng; SHA-256 đề vẫn khớp, bản Gemini vẫn byte-identical; diff whitespace không lỗi. Đây là kiểm tra hồ sơ, không phải kiểm thử phần mềm.
- Bổ sung ảnh UI: Codex đọc năm ảnh chụp lớp/một screenshot Pinterest do người dùng cung cấp; lưu sáu ảnh nguyên bản, đối chiếu hash; dùng design-taste-frontend nhánh app screens để ghi UI_DESIGN_BRIEF. Ghi D022–D024, chuyển kế hoạch backend/mạng→G-UI→UI; palette cụ thể chỉ là gợi ý của AI. Không duyệt Pinterest trên web, không tạo mockup/asset/code hoặc chạy kiểm thử UI trong đợt này. Bộ hồ sơ tăng lên 16 Markdown/24 quyết định, ma trận vẫn 66 yêu cầu.
- D025: dùng skill-installer tải repo UI UX Pro Max do người dùng cung cấp ở commit cố định vào thư mục công cụ cục bộ, giữ LICENSE và nguồn; đọc script/skill, chạy sáu domain search bằng Python có sẵn. Codex kiểm độ khớp (loại kết quả radar cho thời gian, thu hẹp lại query), viết DESIGN_SKILL_REVIEW và cập nhật hồ sơ. Đây là đánh giá công cụ, không phải sinh UI, test KidSafe, đổi stack hoặc xác nhận đạt tiêu chuẩn. Bộ root/docs tăng lên 17 Markdown/25 quyết định, ma trận vẫn 66 yêu cầu.
- Ngày 2026-11-04, D026: người dùng chỉ định Design-PH.md cho bảng màu/style parent. Codex đọc toàn bộ file, ghi hash và điểm YAML nền tối/prose nền sáng; cập nhật hướng dẫn ghi nhớ/brief/kế hoạch, phân biệt parent với child-view. Không sửa nguồn, không coi các chỉ dẫn landing/WebGL trong tài liệu là lệnh triển khai. Bộ root/docs hiện có 18 Markdown kể cả file người dùng thêm, 26 quyết định; chưa có UI hoặc code sản phẩm.
- Thành viên phải kiểm lại yêu cầu, hiểu và tự giải thích giải pháp khi vấn đáp; không lấy phần AI tạo làm bằng chứng hiểu biết cá nhân.

## Nhật ký cần duy trì khi triển khai

| Ngày | Thành viên | Công cụ/phiên bản nếu biết | Yêu cầu/ID | File/phần được hỗ trợ | Con người sửa gì | Test/evidence thật | Kết luận/giới hạn |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Chưa có | — | — | — | — | — | Chưa chạy | Chưa triển khai |

Ghi cả code, test, thiết kế, nội dung báo cáo, biểu đồ và hỗ trợ sửa lỗi nếu có dùng AI. Không bịa citation hoặc số liệu. Nếu thông tin AI sai, ghi cách phát hiện và sửa khi có ảnh hưởng đến sản phẩm. Không gửi dữ liệu trẻ thật, mật khẩu, token hoặc khóa riêng vào prompt.
