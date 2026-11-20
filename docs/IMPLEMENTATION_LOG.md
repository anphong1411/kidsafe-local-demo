# Nhật ký triển khai thực tế

## D063 — Giữ nút tài khoản và bỏ bước nhập địa chỉ trên Pages

Đối chiếu R-A05. Người dùng làm rõ cần giữ hai nút và mở thẳng trang tương ứng. Codex giữ liên kết trực tiếp, rút gọn mô tả bước 2 và tạo lại gói cập nhật giao diện. [Kiểm chứng](evidence/d063-direct-pages/pages-check.json)

## D062 — Bỏ bước nhập địa chỉ trước khi đăng ký hoặc đăng nhập

Đối chiếu R-A05 và R-F5-02. Codex bỏ hộp thoại khỏi trang tải và nối các nút trực tiếp với máy chủ KidSafe. Kiểm Chrome đi từ bản Pages đến cả hai biểu mẫu HTTPS, sáu bố cục, tải bộ cài và hiệu ứng. Kiểm cấu hình đóng gói địa chỉ LAN và từ chối URL không đúng định dạng. [Kiểm chứng](evidence/d062-direct-account/pages-check.json)

## D061 — Thêm Tạo tài khoản ở bước 2 trên GitHub Pages

Đối chiếu R-A05 và R-F5-02. Codex bổ sung nút Tạo tài khoản cạnh Đăng nhập, dùng kiểu nút sẵn có và điều hướng từ cùng hộp thoại HTTPS đến `/register` hoặc `/login`. Kiểm trên Chrome sáu kích thước, chuyển đến cả hai biểu mẫu của server thử và tải bộ cài. Đã dựng lại gói Pages. [Kiểm chứng](evidence/d061-pages-account-buttons/pages-check.json)

## D060 — Nối trang tải GitHub Pages với trang đăng nhập KidSafe

Đối chiếu R-A05 và R-F5-02. Codex khôi phục điểm vào đăng nhập công khai, dùng hộp thoại có nhãn và trả focus khi đóng. Kiểm Chrome sáu kích thước, menu mobile, URL sai, điều hướng đến trang đăng nhập thật của máy chủ thử và tải bộ cài. Trang công khai chỉ nhập địa chỉ máy chủ. [Kiểm chứng](evidence/d060-pages-login/pages-check.json)

## D059 — Sửa trang GitHub Pages hiện logo phóng to

Đối chiếu R-A05. Codex xác nhận trang công khai trả HTML 200 nhưng CSS, JavaScript và shader trả 404 vì thư mục `static` vắng trong repo. Gói Pages chuyển sang các tệp cùng cấp và có chế độ `--web-only` cho repo đã có bộ cài. Kiểm trên đường dẫn con bằng Chrome, giữ đường dẫn của FastAPI và bộ cài hiện tại. [Kiểm chứng](evidence/d059-pages-upload/pages-check.json)

## D058 — Bỏ nút Bật chuyển động nền

Đối chiếu R-A05. Codex bỏ nút và trạng thái tạm dừng riêng của shader theo yêu cầu. Kiểm tra Chrome trang local và gói GitHub Pages ở sáu kích thước, xác minh tùy chọn Giảm chuyển động dừng shader và SHA-256 bộ cài tải xuống khớp. [Kết quả](evidence/d058-remove-motion-button/pages-check.json)

## D057 — 2026-11-09: phát hành bộ cài và rà lại trước demo

Đối chiếu R-A05, R-P01–03, R-F3-02/03, R-F5-03/07/09. Tạo bản GitHub Pages từ template trang tải hiện có, giữ URL tương đối cho đường dẫn con, xây lại bộ cài từ dependency khóa và tách dữ liệu riêng khỏi gói upload. Làm rõ luồng cài/ghép bằng tài khoản Windows thường. Sửa race sidebar khi viewport đổi sang mobile, trạng thái quỹ giải trí thiếu đồng bộ và traceback launcher Windows khi trình duyệt ngắt kết nối tải. [Kiểm chứng và giới hạn](evidence/d057-download/README.md)

## D056 — 2026-11-07: nền shader và hoàn thiện tương tác web

Đối chiếu R-A05, R-F4-02, R-F5-01/06; giữ D050 parent-web/child-Windows và style D026. Trích nguyên chương trình GLSL/packed uniforms từ tệp người dùng, dựng bốn canvas WebGL1 và scheduler chung; lớp màu giữ chữ đọc được. Chuẩn hóa font/touch target menu, thêm menu compact đủ liên kết và quản lý focus ở breakpoint. Khảo sát read-only theo improve-animations tìm lại hai lỗi D047, sau đó triển khai theo yêu cầu sửa trực tiếp: bảo vệ focus khi polling, sidebar inert/keyboard/resize/HTMX, method POST cho auth và copy native-child. Chrome 78 bố cục và các ca tương tác đạt; 54 test đạt. Checker tổng quát/hiệu năng và ngoại lệ được khai báo riêng. [Bằng chứng](evidence/d056-web-polish/README.md)

## D055 — 2026-11-07: sửa theo ảnh đính chính

Đối chiếu R-A05. Bỏ text-stroke của D054; thêm scrim chuyển sắc ở đáy ảnh, đặt nhãn/caption trên lớp scrim và khôi phục heading gallery. Giữ lượng chữ ngắn, không khôi phục slogan/CTA đã bỏ. Chrome kiểm tra năm kích thước, hover, dialog và reduced motion đạt; đã xem desktop/mobile. [Kết quả](evidence/d055-gradient/README.md)

## D054 — 2026-11-07: đặt lại mô tả trong ảnh

Đối chiếu R-A05; sửa CSS đặt caption bên trong ảnh với chữ trắng/viền đen theo yêu cầu, bỏ mã dành chiều cao caption bên dưới của D053. Kiểm tra năm viewport, hover, dialog, reduced motion và JavaScript; không thay backend/tài nguyên ảnh. [Kết quả](evidence/d054-caption/README.md)

## D053 — 2026-11-07: làm gọn Cách hoạt động

Đối chiếu R-A05. Theo ảnh/yêu cầu mới, bỏ overlay ảnh và chữ thừa, chuyển mô tả ra dưới ảnh, giữ nhãn pill có tương phản tối thiểu 10,57:1 trên nền ảnh trắng. Tăng H2 từ nhãn nhỏ thành tiêu đề 48,96px ở 1440, giảm phần ba dòng còn 36px, đo khoảng cách đến ảnh 30,23px. Giữ reveal theo dòng, FLIP và dialog, ổn định chiều cao caption khi hover, rút pin xuống 160px. Tám viewport/tương tác đạt, hai test download đạt; checker Taste tổng quát có ngoại lệ được khai báo. [Bằng chứng](evidence/d053-clear-gallery/README.md)

## D052 — 2026-11-07: gallery cho phần Cách hoạt động

Đối chiếu R-A05; nội dung giới thiệu bám R-F1, R-F2, R-F3 và D050. Dùng Taste/Emil/animate; ánh xạ component React tham khảo sang Jinja2, CSS view timeline, FLIP/WAAPI và native dialog. Sao chép nguyên byte bốn ảnh theo thứ tự đính kèm. Kiểm tra tám kích thước, hover nhanh, bàn phím/focus, cảm ứng, reduced motion và no-JS; hai test tải Windows đạt. Kiểm tra Taste tổng quát và giới hạn được ghi riêng, không tuyên bố tất cả bộ kiểm tra đều xanh. [Kết quả](evidence/d052-how-gallery/README.md)

## D051 — 2026-11-07: bố cục và typography auth/landing

Đối chiếu R-A05. Dùng Taste/Emil, kiểm phông thực tế qua Chrome, xác nhận lệch tiêu đề do căn giữa hai chiều cao nội dung khác nhau. Bỏ hai dòng dưới auth, căn đầu hai cột và tăng nhãn/subtitle. Đo 24 bố cục và các mốc cuộn thay vì suy đoán qua ảnh. [Kết quả](evidence/d051-auth-layout/README.md)

## D050 — 2026-11-07: cửa sổ app cho trẻ

Đối chiếu R-A01/03, R-F1-04, R-F3-01/03/04, R-F4-04 và R-F5-06/09. Thêm native Win32/Pillow UI trong PID tray, read-only device child-view API, trạng thái IPC cục bộ và request phút chính xác, bền vững qua queue. Giữ xác thực peer/visible lease hiện hành; không chạy service trên host. Sửa luồng parent/cài app, giữ web-child cho báo cáo/legacy. Gỡ phụ thuộc MFC của UI, bổ sung websockets vào bundle, chạy kiểm tra UI từ runtime đóng gói và tạo bộ cài1.0.1. [Bằng chứng và giới hạn](evidence/d050-child-native/README.md)

## D049 — 2026-11-07: tạo tài khoản trên web

Đối chiếu R-A05, R-F5-01/02/05/06 và R-P01. Thêm đăng ký parent công khai với CSRF trước đăng nhập, kiểm tra đầu vào/username trùng và rate limit riêng; mã hóa tên, băm mật khẩu, migration giữ dữ liệu cũ. Thay hướng dẫn trang tải/FAQ và bỏ nút dừng theo yêu cầu trực tiếp. Đã sao lưu nhất quán SQLite, cập nhật server 8446 bằng cùng cấu hình/khóa, kiểm tra thông tin xác thực cũ không đổi. Toàn bộ 93 test server và luồng Chrome QA đạt. [Bằng chứng](evidence/d049-registration/README.md)

## D048 — 2026-11-07: khớp chuyển động với video tham chiếu

Đối chiếu R-A05, R-P01, R-F5-01/02/06, R-D09. Đọc video người dùng bằng Chrome cục bộ, chỉnh template/CSS và thêm script đo timeline/điều khiển dừng vòng lặp. Kiểm tra chuyển động bằng ma trận thực trước/sau cuộn, 7 viewport, reduced motion, thao tác chạm và các link công khai; 2 test download đạt. [Bằng chứng và giới hạn](evidence/d048-video-motion/README.md)

## D047 — 2026-11-07: rà giao diện và chuyển động

Đối chiếu R-A05, R-F3-02/03, R-F4-02/04. Kiểm tra bố cục và tương tác bằng Chrome trên hồ sơ QA, rà animation CSS/JS và phạm vi preview/tray. Ghi ba phát hiện đã xác nhận và các giả thuyết đã loại trong [báo cáo](../plans/UI_ANIMATION_AUDIT_2026-11-07.md).

## D046 — 2026-11-07: cài bộ skill Emil

Đối chiếu cả 9 tệp với nguồn chính thức ở commit cố định, cài nguyên vẹn SKILL.md và tài liệu được tham chiếu. Kiểm tra mã băm, tên skill duy nhất và liên kết Markdown tương đối. Ghi hướng dẫn chọn skill phù hợp trong AGENTS. [Kiểm chứng](evidence/d046-emil-skills/README.md)

## D045 — 2026-11-07: cài skill và cấu hình hướng dẫn dự án

Tệp Taste-SKILL.md khớp SHA-256 với bản chính thức 2.5.0. Cài bộ tài nguyên ở commit cố định vào `.agents/skills/design-taste-frontend`, lưu bản v2 và giữ helper tương thích QA. Cập nhật hướng dẫn mặc định ở AGENTS. [Kiểm chứng](evidence/d045-taste-skill/README.md)

## D044 — 2026-11-07: hội thoại, hiệu ứng cuộn và luồng bắt đầu

Đối chiếu R-A05, R-P01, R-F5-01/02/06 và R-D09. Dùng CSS view timeline và sticky trong Jinja, hỗ trợ giảm chuyển động. Tài khoản phụ huynh vẫn do người quản trị máy chủ cấp. Lệnh `server.seed --config` dùng đúng cấu hình máy chủ. Bộ cài chờ tệp kết nối và mã ghép ở bước cuối. Xem [kiểm chứng](evidence/d044-download-motion/README.md).

## D043 — 2026-11-07: làm mới giao diện trang tải Windows

Đối chiếu R-A05, R-P01 và R-D09. Dựng giao diện Jinja/CSS theo tham chiếu Linea. Dùng disclosure HTML cho hướng dẫn và FAQ, hỗ trợ giảm chuyển động. Kiểm tra tải đúng EXE và xem trước ở sáu kích thước bằng Chrome. Xem [kiểm chứng](evidence/d043-linea-download/README.md).

## D042 — 2026-11-07: trang tải và bộ cài Windows

Đối chiếu R-A01/02/03/04/06, R-P01, R-F5-07 và R-D09. Gói Windows x64 dùng runtime Python cô lập, thư viện đã khóa và quy trình service/tray hiện có. Wizard kiểm tra TLS trước khi ghép, giữ trạng thái chưa kích hoạt trong lần chạy service để ghép đôi. Thêm route tải file và xuất tệp kết nối có phân quyền. Xem [kiểm chứng](evidence/d042-windows-setup/README.md).

## 2026-11-05 — Đóng gói preview Streamlit

Đối chiếu R-F3-02, R-D03 và phạm vi R-F5-01/02. Tái dùng template, bố cục và bộ dựng trang phụ huynh. Bản preview dùng tài khoản demo riêng và nguồn dữ liệu chỉ đọc. ZIP độc lập được kiểm tra trên Chrome với hai kích thước màn hình. Xem [kiểm chứng](evidence/streamlit-preview/README.md).

Thêm tùy chọn `--flat` và đọc trực tiếp từ `dashboard-assets.zip` để tải tệp bằng hộp chọn tệp GitHub. Kiểm tra ZIP và luồng Chrome từ bản giải nén đạt.

## D041 — 2026-11-05: tinh chỉnh trang trẻ

Đối chiếu R-F1-06, R-F3-03/05 và R-F4-04. Dùng bộ đếm giải trí hiện có và suy biểu tượng nhật ký từ thay đổi cài đặt. Cập nhật thẻ giờ, nút xin thêm và hai trạng thái trống. Xem [kiểm chứng](evidence/d041-child-polish/README.md).

## D040 — 2026-11-05: màn hình minh bạch cho trẻ

Đối chiếu R-F1-01/02, R-F3-01/02/03/05 và R-F4-02/03/04. Giữ dữ liệu thời gian, hoạt động và nhật ký. Thêm gửi/duyệt số phút đã chọn, phân biệt chờ xác nhận và đã nhận lệnh. Xem [kiểm chứng](evidence/d040-child/README.md).

## D039 — 2026-11-05: nhật ký phụ huynh và trẻ

Đối chiếu R-F3-03/05 và R-F4-04. So sánh hai bản cài đặt để mô tả đúng phần thay đổi. Hộp thoại và trang trẻ dùng chung danh sách 10 mục. API tóm tắt giữ phạm vi hồ sơ. Bản ghi kiểm toán tiếp tục được lưu theo chính sách hiện có. Xem [kiểm chứng](evidence/d039-audit/README.md).

## D038 — 2026-11-05: tinh chỉnh demo

Đối chiếu R-P01, R-F3-06, R-F4-02/03/04 và R-F5-01/02. Thêm đếm ngược mã ghép, đặt mật khẩu mới có hủy phiên và audit, CSV có phân quyền và bảo vệ giá trị công thức bảng tính. Lệnh mở khóa ký mốc hết hạn tuyệt đối đến nửa đêm theo lựa chọn của người dùng. Xem [bằng chứng](evidence/d038-demo/README.md).

## D037 — 2026-11-05: thiết kế lại Lọc website

Đối chiếu R-F2-03/04/05, R-F3-01, R-F4-02/03/04. Thay checkbox/textarea bằng công tắc và thẻ. Thêm thao tác cập nhật từng quy tắc với kiểm tra quyền, CSRF, version và audit. Dùng hostname từ trình duyệt và Public Suffix List cục bộ để chuẩn hóa. Kiểm thử DNS loopback, không thay DNS hệ điều hành. Xem [bằng chứng](evidence/d037-web/README.md).

## D036 — 2026-11-05: cấu hình và áp dụng nhóm ứng dụng

Đối chiếu R-F1-01/03/06, R-F2-01/02, R-F3-01/04/05, R-F4-02/03/04. Thêm policy nhóm có kiểm tra đầu vào, nâng version/audit, bộ đếm nhóm và giới hạn theo khung giờ. Cửa sổ giải thích phải hiển thị trước khi đóng tiến trình. Kiểm thử dùng thiết bị và tiến trình giả lập. Xem [kiểm chứng và phạm vi](evidence/d036-app-groups/README.md).

## D035 — Lịch tuần và thực thi hạn mức giải trí

R-F1-01/03/06, R-F2-01, R-F3-01/03, R-F4-02/04. Kiểm tra quỹ giải trí ở form và API, nâng policy cũ có audit, gắn kiểm tra hết quỹ vào AppMonitor và giữ xác nhận hiển thị trước khi đóng tiến trình. Tách bản nháp lịch và hạn mức, căn thước giờ chung với lưới và hiển thị tổng ngày/cảnh báo. Kết quả và giới hạn đồng bộ trong `evidence/d035-time/README.md`.

## D034 — 2026-11-05: tách điều khiển, cấu hình và đếm giải trí

Đối chiếu R-F1-01/03/06, R-F3-01/02/03/04, R-F4-02/04, D017. Người dùng chọn nhóm ứng dụng do parent xác định, không tính toàn bộ thời gian máy. Thêm route/template icon/CSS Grid, renderer quick-control/tools/quota ba cột/group form, signed policy defaults/version migration/audit, stats hiệu lực và report aggregate. Agent monitor callback nối EntertainmentCounter; idle/locked/stall không cộng, state giữ qua reboot, ngăn ghi sau deletion_generation.

105core đạt46.14s và nhóm3TLS+1corelặp đạt40.37s =108testduynhất. Giữ bằng chứng hai fullsuite từng lỗi socket Windows; không skip/nới tiêu chí mạng. 18browserchecks,66layoutchecks và inspector4trang×3width đều đạt; đã xem33ảnh cuối và trạng thái số liệu/Online/empty. Chưa chạy native agent hoặc xác minh tự chặn theo quỹ giải trí; phần này chưa được triển khai/không coi NC đầy đủ.

Backup runtime SQLite riêng trước nạp lại đúng server8443/8446, smokeTLS có CA/login/read/logout đạt; không thay DNS/service/truststore hoặc hồ sơ thật ngoài migration additive được audit. Bằng chứng/lệnh/giới hạn: `docs/evidence/d034-controls/README.md`.

## D033 — 2026-11-05: typography và dashboard phụ huynh

Đối chiếu R-F3-02/03/04, R-F4-02/04, R-F5-02/06, D017; ghi R-F1-06 là NC chưa có budget giải trí. Đã đọc và lưu nguyên file tinh chỉnh, áp dụng style nguồn Design-PH thay cho việc đổi stack. Sửa parent.html/app.css/app.js/login.css; reports thêm trạng thái request và đếm pending/tổng tuần đúng phạm vi. Chỉ dữ liệu thử riêng được tạo/xóa trong browser QA.

Trước: 4/60 tổ hợp tràn trang, 1058 lần xuất hiện text dưới14px. Sau: 0/60, 0; KPI bằng chiều cao, heading dashboard≤2dòng, không JSexception. Đã xem 30 screenshot cuối cùng và ảnh menu/dialog. 46 backend tests đạt35.57s; thêm một ca WebSocket TLS pin thật và chạy lại hai test report đạt11.61s; 15 browser interaction checks đạt. Inspector app0finding với hai ngoại lệ theo yêu cầu; source lint0FAIL/11WARN có lý do trong evidence.

Lệnh và chứng cứ chi tiết: `docs/evidence/parent-refinement-2026-11-05/README.md`, XML và JSON kèm theo. Đã nạp lại đúng hai serverdemo8443/VM8446, kiểm TLS có CA/login/read/logout đều đạt, giữ database. Dừng server thử riêng8447 sau QA. Không đụng enforcement/DNS/truststore, không gọi đây là nghiệm thu Windows hoặc sourceZIP phát hành mới.

## D032 — 2026-11-05: ảnh login do người dùng gửi

Copy PNG gốc vào static/images/login-family.png, thay SVG ở login.html, thêm dấu chấm cuối H1. CSS ảnh420px desktop/320px mobile, tự giữ tỷ lệ và cân giữa hai cột. Chrome kiểm8viewport, ảnh tải đúng1024×572, không tràn/méo; xem ảnh1440/390; login sai/đúng/logout PASS, khôngJSexception. Không chỉnh bitmap, không thay auth. Evidence login-family-image; dựng lại sourceZIP và bản transfer cho hướng dẫnVM.

## D031 — login ít chữ và minh họa đồng hành

Sửa login.html/login.css: xóa mô tả/slogan/khốiK, H1 một câu có dấu phẩy; SVG geometric không chữ/số, đúng ba màu, desktop150px/mobile140px. Giữ form/auth. Đo8viewport bằng Chrome và kiểm cấu trúc SVG, nội dung bỏ, màu/chiều cao, overflow, tâm hai cột; thử login sai/đúng/logout đều PASS, không JSexception. Xem ảnh1440/390 và lưu results.json trong docs/evidence/login-connection. Không viết unit test mô phỏng CSS; không chạy lại bộ agent cho chỉnh nội dung/minh họa.

## D030 — tinh chỉnh tỷ lệ chữ/layout trang login

Thêm CSS riêng cho login và sắp lại markup figure/slogan/label; giữ màu và luồng auth. Đo Chromium8viewports đạt: desktop hai cột cùng tâm, không tràn ngang, input46px, scale theo yêu cầu. Xem ảnh1440/390; thử login sai/đúng/logout thành công, không exceptionJS. Dùng server8446 đã chạy sẵn sau khi lần khởi động thử báo trùngcổng; không dừng server người dùng. Rà thiết kế khôngFAIL; WARN h1/eyebrow là ngoại lệ theo yêu cầu trực tiếp. Kiểm cookie/CSRF/logout và HTMLredirect riêng; không viết unit test chỉ để kiểm CSS.

## Hướng dẫn một máy cho người mới — D029

Người dùng chỉ có một máy vật lý. Đã kiểm tra các vị trí cài VirtualBox thông dụng chưa thấy và chưa tìm thấy ISO/VM ở thư mục download đã kiểm. Lưu ONE_PC_SETUP với chặng web trước, WindowsVM/NAT sau; không đổi yêu cầu agent/service/user thường. Xác minh bằng tài liệu Oracle NAT10.0.2.2 và localhostreachable; WindowsISO đánh giá từ Microsoft.

Đã tạo profile `.runtime/vm` và chạy launcher loopback8446, CA-verified TLS/login/logout PASS; dừng server sau kiểm tra để người dùng khởi động bằng cửa sổ của mình. Xuất CA/public key và chuẩn bị thư mục transfer chỉ chứa nguồnZIP và dữ liệu công khai. Không cài VirtualBox, không sửa firewall/truststore/DNS của host và không chạy enforcement. Các bướcVM/agent vẫn chưa được thực hiện, không gọi hướng dẫn là bằng chứng nghiệm thu.

## Hướng dẫn hai máy

Đã bổ sung docs/TWO_PC_SETUP.md theo yêu cầu người dùng. Phát hiện launcher trước đó không thể cấp certIP cho profilelocalhost đã có; thêm RuntimeDirectory, seed/export --config và kiểm hostkhớp trướcchạy. Kiểm5test profiles/TLS đạt2.36s, StartPS parseđạt. Chạy launcher profiletạm riêng qua CA-verifiedTLS8445 và login/logout đúngprofile đạt; dừng saukiểmtra. Không thực hiện mởfirewall, importCA trust hoặc càiagent/đổiDNS trênhost. Gói nguồn dựnglại để máyB nhậncùngbảnscriptmới.

## Đợt hoàn thiện app theo D028

Kết quả chốt:92test passed75.46s; Chrome19checks passed, ảnh1440/768/390, inspectorapp khôngfinding. Gói nguồn đã giải nén vào thư mục mới và45test backend/HTML/package chạy đạt34.42s bằng venv mới. Phát hiện/sửa thiếu thư mục tạm khi kiểm gói; không thay dữ liệu production. File nguồnDesign-PH giữ nguyênSHA256. Archive cuối và manifest kiểm bằng scripts.verify_release; runtime/privatekeys không nằm trong gói.

Người dùng yêu cầu làm xong app rồi mới dừng. Đã tiếp tục dựng UI khi thiếu lab, giữ G-UI là cổng nghiệm thu. Các ghi chú chưa dựng UI/chưa nối runtime ở đợt trước bên dưới là lịch sử.

- Parent8 trang + login và child-view Jinja2/HTMX nối API, layout desktop/tablet/mobile. Theme sáng theo Design-PH, ghi UI_IMPLEMENTATION. HTMX local2.0.4 kèm MIT, CSP không unsafe-inline/eval, menu/keyboard/focus, zero/error/pending/offline và phân quyền thật.
- API thêm tài khoản trẻ, childrequest idempotent, commandACK list, deletionstatus, rotationCSRF, reports normal/exception và giờ cộng chỉ sau ACK; pendinggrant hiển thị riêng. Audit IP/old/new và consentIP AES-GCM, migration từ build ban đầu; giữ refresh verifier cleanup-only cho máy offline dài ngày đến ACK.
- Agent appmonitor scoped child, foreground appdurations bỏ idle/khóa, giải thích qua cửa sổ Windows rồi ACK trước terminate; service/tray/peerPID/user/session kiểm tra, iconOS acknowledgment. DNS UDP/TCP IPv4/IPv6, snapshot/restore và installer/uninstaller/SCM recovery. Clock drift audit riêng90day, không tạo eventtype thứ10; atomicusage/command/ACK và deletionfence.
- Lỗi HTMX dùng body dataset cũ sau đổi trang đã sửa và browser regression đạt. Lỗi hiển thị giờ cộng/ngoại lệ đã tách. Đợt test toàn bộ90pass; kết quả cuối sau chốt mọi thay đổi nằm pytest-app-complete.xml. Luồng TLS WS thật nhận lệnh và chữ ký đạt; chỉ là localhost protocol, không giả thành Windows locklatency.
- Chrome14 bước qua login/createchild/forms/HTMX/childaccount/request/403; ảnh1440/768/390 đã chụp và xem. Inspector app không có FAIL; tăng chữ mobile theo tinytextWARN. Eyebrow child/login giữ vì giọng sản phẩm; enum unlock bị lint marketingWARN là nhận diện nhầm mã giao thức.
- Cài47dependency từ lock vào venv mới trong .tmp, import backend/agent đạt; không coi là test Windows sạch≤15 phút. Có Start-KidSafe.ps1 và public CA/key export; source ZIP có manifestSHA256, loại runtime/khóa/privateconfig/dependencies.

Phạm vi chưa kiểm thực: máy trẻ user thường, SCM/ACL/Tray/native dialog/DNS adapter/rollback/bypass/benchmark. Chưa có captureWireshark, báo cáoWord/PDF hoặc video nộp cuối. Không báo hoàn tất các mục này bằng test mô phỏng.

## 2026-11-04 — Bắt đầu theo quyền người dùng

Người dùng yêu cầu bắt đầu toàn bộ kế hoạch, tự quyết chi tiết và kiểm tra/sửa lỗi sau từng phần, không cần hỏi thêm khi họ vắng mặt. Điều này mở cổng triển khai D005; các giả định giảng viên chưa xác nhận vẫn giữ nguyên.

- D027: bắt đầu triển khai; quyết định kỹ thuật chưa chốt do Codex lựa chọn và ghi rõ, không giả danh quyết định giảng viên.
- Điều phối Sol High cho backend/agent; Astra Low rà soát độc lập theo trao đổi ngay trước lệnh bắt đầu. Không thay model của phiên chính.
- Python mặc định WindowsApps không chạy. Dùng Python 3.12.14 được đóng gói sẵn để tạo `.venv`; ensurepip lỗi, khắc phục bằng uv pip vào đúng venv.
- Đã resolve và cài 45 dependency từ PyPI, phiên bản lưu trong `requirements.lock`. Không cài toàn cục.
- Các thử nghiệm tự động chỉ dùng dữ liệu tạm/loopback; chưa có máy trẻ hoặc VM đã được xác minh. Không thay DNS/khóa máy làm việc hiện tại.
- UI vẫn chờ G-UI; không đánh dấu đủ nghiệm thu chỉ từ unit test.

Nguồn kỹ thuật kiểm tra: [FastAPI HTTPS](https://fastapi.tiangolo.com/deployment/https/), [SQLite foreign keys](https://sqlite.org/foreignkeys.html), [SQLite WAL](https://sqlite.org/wal.html).

## Kết quả và điểm tiếp tục

- Dependency cuối hiện có 47 gói khóa trong requirements.lock; bổ sung tzdata cho Windows, dnslib để phân tích gói DNS độc lập.
- Backend đã có auth scrypt/session/CSRF/ownership, enroll/refresh, Ed25519 policy, command/ACK/WebSocket, quota allocation/transfer, event 7 trường/idempotency, retention/xóa và reports/audit. Đã sửa policy cùng version đổi nội dung, giao dịch ghi serialize, PSL offline, sự kiện payload giống nhau vẫn được giữ và revoke cleanup.
- Agent có cache SQLite/DPAPI adapter, monotonic enforcer, app SHA256, DNS TCP/UDP, SafeSearch/hạn chế HTTPS hints, sync TLS pin/WS, tray IPC mặc định từ chối peer chưa xác minh, runtime/service entry. Đã sửa retention replay, suspend charging, clock/reboot override, deletion heartbeat/fetch/upload và cleanup ACK retry.
- Kết quả cuối đợt: **54 test đạt**, log XML ở docs/evidence. Khởi động backend qua scripts.run_server và smoke scripts.check_lab đạt; server đã dừng sau kiểm tra. Không có Windows trust/DNS/firewall/service host bị đổi.
- Các agent phụ gặp giới hạn sử dụng giữa đợt; agent chính tiếp tục sửa/nối code và chạy kiểm thử. Không coi rà soát độc lập là chứng nhận an toàn toàn bộ code.
- G-UI chưa đạt: chưa có máy trẻ/VM được xác minh, không có Wireshark; runtime/service và peer verification chưa được thử thực dưới user thường. App monitor + cửa sổ giải thích/start-stop reports chưa nối đủ. Chưa có bộ cài hoàn chỉnh, DNS snapshot/rollback hoặc SCM recovery được thử. Không chuyển sang dashboard để vượt cổng người dùng đã chốt.
- Cần tiếp tục: hoàn thiện các điểm runtime phía trên, bổ sung regression tests; sau đó nghiệm thu Windows lab cho S5–S7 và G-UI rồi S4/S8. M1/M3/M4/M5/M6, báo cáo và video còn thiếu bằng chứng thật; D019/D020/D021 vẫn chờ như trước.
