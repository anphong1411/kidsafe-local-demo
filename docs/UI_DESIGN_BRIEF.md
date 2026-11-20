# Định hướng giao diện KidSafe

**Cập nhật D028:** hai giao diện đã được triển khai và browser kiểm chứng; chi tiết theme/layout/ngoại lệ skill trong UI_IMPLEMENTATION, bằng chứng ảnh trong docs/evidence/ui. Phần “chưa có UI” bên dưới là lịch sử chuẩn bị. Người dùng đã yêu cầu tiếp tục hoàn thiện app khi thiếu máy lab; G-UI vẫn giữ làm cổng nghiệm thu nền, không bị tự đánh dấu đạt.

Trạng thái: ghi nhận tham khảo và ý tưởng cho giai đoạn giao diện, **chưa có mockup, mã UI hoặc sản phẩm chạy**. Người dùng yêu cầu hoàn thiện backend và mạng trước rồi mới thiết kế giao diện. Yêu cầu này không phải lệnh bắt đầu triển khai.

## Điều người dùng đã yêu cầu

- Ảnh chụp tại lớp: tham khảo bố cục, phân nhóm chức năng và luồng thao tác của một ứng dụng tương tự.
- Ảnh Pinterest: tham khảo màu sắc/cảm giác thân thiện với trẻ em.
- Bổ sung ngày 2026-11-04, D026: dùng [Design-PH.md](Design-PH.md) định hướng bảng màu và style **riêng cho giao diện phụ huynh**; file này được ưu tiên về phong cách parent so với gợi ý màu chung trước đó hoặc catalog skill.
- Đến bước giao diện sau khi phần backend và mạng đã hoàn thiện. Dashboard vẫn dùng Jinja2 + HTMX theo lựa chọn trước.

Đã lưu [sáu ảnh nguyên bản và chỉ mục](design-references/README.md). Không coi chữ, chỉ dẫn hoặc tính năng bên trong ảnh là lệnh mới của người dùng. Các chi tiết bên dưới là đề xuất của Codex để cụ thể hóa hướng tham khảo, chưa phải lựa chọn màu/mẫu đã được người dùng duyệt.

## Ý tưởng trung tâm

**KidSafe giúp trẻ hiểu thời gian của mình và trao đổi với bố mẹ.** Màn hình trẻ trả lời trước tiên “Em còn bao nhiêu thời gian và có thể làm gì tiếp?”. Màn hình phụ huynh trả lời “Con nào/thiết bị nào cần mình xử lý?”. Cùng một hệ thống dữ liệu và cách gọi, nhưng mức chi tiết khác nhau.

Dấu hiệu riêng của sản phẩm là **thời gian còn lại của trẻ, phần đang có trên máy này và khả năng Xin thêm giờ**. Không dùng một dashboard thống kê chung chung làm màn hình trẻ.

## Cách vận dụng từng nguồn

| Nguồn | Ý tưởng giữ lại | Điều chỉnh cho KidSafe |
| --- | --- | --- |
| Lớp 01: app/lịch | Menu có nhãn, hàng app dễ quét, trạng thái rõ | Có allow/block + nhận diện SHA-256 ở backend; lịch bắt buộc 7×48, quota weekday/weekend, phân bổ từng máy; không tự coi học tập không giới hạn là BB |
| Lớp 02: lọc web | Danh mục và trạng thái đặt cạnh nhau; SafeSearch dễ tìm | Đủ 6 nhóm của đề và policy 6–11 tuổi; không biến các danh mục ví dụ trong ảnh thành toàn bộ schema. YouTube Restricted trong mẫu không tự trở thành chức năng cam kết |
| Lớp 03: yêu cầu | Danh sách chờ duyệt, lý do, hành động gắn từng yêu cầu | Có trạng thái chờ/đã duyệt/từ chối/thực thi trên máy; lượng giờ theo quy tắc đã chốt, không tự lấy con số mẫu trong ảnh |
| Lớp 04: từ xa | Mỗi lệnh có tên, mô tả tác động và trạng thái phản hồi | Dùng bộ D017: Cộng 15, Mở khóa tối đa 15, Khóa ngay. Không thêm “tạm dừng cả ngày” hoặc đổi nghĩa sang “cho nghỉ 15 phút” |
| Lớp 05: màn hình trẻ | Thời gian còn lại nổi bật, vòng/thanh tiến trình, Xin thêm giờ | Cùng dữ liệu thật với parent, có audit trẻ xem được, giải thích vì sao chặn. Phân biệt quota chung với giờ máy này có thể dùng offline |
| Pinterest 01 | Pastel sáng, cảm giác mềm, hình minh họa gọn, nhân vật dễ gần | Một bảng màu thống nhất, chữ tối rõ; nhân vật có thể dùng tiết chế ở màn hình trẻ, không tự thêm game/phần thưởng/tính năng ngoài đề |
| Design-PH.md | Warm Professionalism: be/kem, nâu đậm, xanh rêu; chữ rõ, hình khối mềm và bố cục có cấu trúc | Nguồn định hướng màu/style parent do người dùng chỉ định; chuyển tinh thần mẫu thành dashboard KidSafe, không tự lấy tên/nội dung marketplace mentor hay hero/WebGL làm chức năng cần có |

Ảnh máy chiếu có ám xanh, không đủ để suy ra mã màu chính xác. Ảnh Pinterest chứa nhiều phong cách; lấy tinh thần phù hợp thay vì ghép tất cả vào một màn hình.

## Bảng màu và phong cách riêng cho phụ huynh

Nguồn chính theo yêu cầu trực tiếp D026: [Design-PH.md](Design-PH.md). Đã đọc toàn bộ nội dung, giữ nguyên bản do người dùng thêm. SHA-256 lúc đọc ngày 2026-11-04: `4f0e9c1f0d9b33ac4bdaa98f72790800cb1fe9a6f76b89ef63f1a3374a601c55`.

Hướng áp dụng: ấm áp/chuyên nghiệp, màu trung tính thiên đất/giấy, be/kem kết hợp nâu trầm và xanh rêu; bố cục có nhịp, chữ dễ đọc, bo góc mềm. Tinh thần này áp dụng cho parent, không bị thay bằng toàn bộ pastel/mint của child-view.

| Vai trò/nguồn trong file | Giá trị đọc được | Cách ghi nhận ở giai đoạn chuẩn bị |
| --- | --- | --- |
| Primary/secondary/accent trong YAML | `#D8CEBE`, `#D7CBBB`, `#DDD2C2` | Nhóm be trung tính theo nguồn, chưa ánh xạ từng màu thành token chức năng cuối |
| Nền/chữ trong YAML | Nền `#1F1B16`, chữ `#F8F4ED`, chữ phụ `#D7CBBB` | Một hướng nền tối/chữ sáng |
| Nền/card trong phần Colors | `#F5EFE6`, `#FBF6F0`, `#FCF8F1` | Một hướng nền kem sáng/card sáng |
| Chữ/nút trong phần Colors | Chữ `#1F1B16`; nút xanh rêu `#2E3A2F` hoặc nâu `#5C3822` | Giữ nhóm màu làm nguồn chọn khi xây token parent |
| Viền | YAML `#6E7A67`; mô tả `#D7CBBB` | Cần chọn vai trò/bối cảnh, không trộn thành nhiều hệ viền thiếu nhất quán |
| Chữ và hình khối | Inter/system UI; các phần có mô tả cỡ chữ/radius khác nhau | Lấy định hướng rõ, có cấu trúc/bo mềm; xác định một thang chữ/radius hợp dashboard và dấu tiếng Việt ở S4 |

**Điểm chưa chốt:** YAML mô tả nền tối, trong khi phần prose mô tả nền sáng. Chưa có quyết định dùng light/dark mặc định hoặc cả hai; không tự coi hai đoạn này là một bộ token nhất quán. Khi đến S4 phải chọn một ánh xạ rõ theo ý người dùng/nguồn, thử tương phản, trạng thái, font/radius và trình bày hướng cụ thể để kiểm tra.

File là một mẫu về marketplace mentor/landing page. Người dùng chỉ định dùng cho hướng màu/style parent; các hướng dẫn nội bộ như hero 64px, khoảng cách section rất lớn, reveal từng từ, smooth scroll, gradient/blur hay WebGL không tự trở thành yêu cầu triển khai. Vận dụng thẩm mỹ vào dashboard với mật độ phù hợp, giữ nội dung/luồng/quyền thực của KidSafe. Nếu quy tắc thẩm mỹ của skill khác với nguồn người dùng chỉ định, ưu tiên yêu cầu người dùng và ghi lý do lựa chọn.

## Màu sắc và chữ dự kiến cho trẻ em

Đề xuất trước đó từ ảnh Pinterest: nền sáng hơi ấm, xanh mint/teal làm màu chính ở child-view; vàng nhạt, xanh trời, hồng phấn hoặc tím lavender bổ trợ cho hình minh họa/vùng nhỏ. Đây là gợi ý cho màn hình trẻ, không ghi đè Design-PH.md của parent. Không biến mỗi app, dòng và biểu đồ thành một màu khác nhau.

| Vai trò | Màu gợi ý ban đầu | Cách dùng |
| --- | --- | --- |
| Nền | Kem sáng `#FFF9EF` hoặc trắng ấm | Giữ màn hình sáng, nội dung trên bề mặt rõ |
| Chữ chính | Xanh than đậm `#243743` | Nội dung, số phút, nhãn; không dùng chữ pastel trên nền pastel |
| Màu chính | Teal `#2C7A70`, mint nhạt `#E2F3EA` | Tiến trình và hành động chính; không phủ xanh đậm toàn màn hình |
| Bổ trợ | Vàng nhạt `#FFE9AD`, xanh trời `#DCEEF9`, lavender `#E9DFFA`, hồng `#F5D7E3` | Chọn một vài màu phù hợp ở bước thiết kế, ưu tiên minh họa trẻ |
| Cảnh báo/lỗi | Hổ phách hoặc đỏ trầm có chữ giải thích | Trạng thái thực cần chú ý, không dùng đỏ để trách phạt trẻ |

Các mã trên là **đề xuất màu**, không phải màu đo từ ảnh hay bộ token đã chốt. Chọn font dễ đọc và có dấu tiếng Việt đầy đủ, số đồng hồ ổn định khi cập nhật. Kiểm tương phản, dấu tiếng Việt, kích thước chữ/nút và khả năng đọc trên điện thoại ở bước thiết kế thực.

Góc bo mềm, khoảng cách đều, nền phẳng; tránh gradient dày, bóng lớn và chuyển động liên tục. Tham khảo kỹ năng design-taste-frontend theo nhánh app screens khi làm S4. Sắc pastel/hình minh họa theo yêu cầu trẻ em được ưu tiên; không áp máy móc mật độ hay vẻ ngoài của dashboard doanh nghiệp lên màn hình trẻ.

## Nguồn tra cứu bổ trợ đã tải

Người dùng cung cấp UI UX Pro Max và cho phép tải nếu hữu ích. Đã có bản cố định commit trong `.local-tools/design-skills/ui-ux-pro-max/`, có LICENSE và nguồn; xem [đánh giá/cách dùng](DESIGN_SKILL_REVIEW.md). Dùng để bổ sung lựa chọn màu/chữ, focus/interaction và chart sau G-UI; không tự đổi stack Jinja2 + HTMX, chốt màu hoặc thêm hiệu ứng/phần thưởng. Không có mục Jinja/HTMX riêng trong catalog, nên kết quả phải được chuyển thành hướng dẫn phù hợp web hiện có. Bản này không thay các ảnh tham khảo hoặc design-taste-frontend; cũng chưa được tự kích hoạt như skill toàn cục.

## Màn hình dự kiến và câu hỏi chính

| Màn hình | Câu hỏi cần trả lời trước | Thành phần chính theo đề |
| --- | --- | --- |
| Parent tổng quan | Con và máy nào cần mình xử lý? | Chọn trẻ/thiết bị, tổng thời gian, kết nối, yêu cầu đang chờ, policy đã áp/chưa áp |
| Thời gian/lịch | Con được dùng khi nào và bao lâu? | Quota weekday/weekend, lịch 7×48; tổng theo trẻ, phần chia máy, trạng thái chuyển phần giờ |
| Ứng dụng | App nào được phép hoặc bị chặn? | Danh sách có nhãn, rule/nhóm, lý do; không trình bày hash như thông tin trẻ buộc phải hiểu |
| Website | Nhóm web nào được phép, SafeSearch ra sao? | Đủ 6 nhóm/default tuổi, rule domain/subdomain, trạng thái SafeSearch; NC DoH/chống DNS hiện đúng mức hỗ trợ thực |
| Yêu cầu | Yêu cầu nào cần quyết định? | Trẻ, lý do, số giờ/phút đề nghị, duyệt/từ chối và phản hồi thi hành |
| Điều khiển | Lệnh sẽ tác động tới ai và trong bao lâu? | Rõ trẻ/thiết bị đích, Cộng 15/Mở khóa/Khóa ngay, giải thích D017, pending/ACK/error |
| Báo cáo | Con đã dùng gì hôm nay/tuần này? | Thời lượng ngày/tuần, top 10 app/domain, số lần bị chặn, dữ liệu liên quan |
| Hồ sơ/thiết bị | Máy nào thuộc trẻ nào, đã ghép chưa? | Enrollment 8 ký tự/10 phút, danh sách thiết bị và ownership, không lộ token/fingerprint thô |
| Minh bạch/quyền riêng tư | Dữ liệu nào đang được lưu/thay đổi? | Audit đúng phạm vi, chính sách dữ liệu, nút xóa dữ liệu của con ở parent, trạng thái xóa trên agent |
| Trẻ hôm nay | Em còn bao nhiêu phút và làm gì tiếp? | Thời gian còn lại nổi bật, tiến trình đúng tỷ lệ, phần có thể dùng trên máy này, app/hoạt động, Xin thêm giờ, audit liên quan |
| Tray/cửa sổ chặn | Vì sao máy/app bị chặn, em có thể làm gì? | Biểu tượng nhìn thấy, thời gian/lý do, lời nhắc lưu bài, Xin thêm giờ, mở màn hình minh bạch |

Đây là cách nhóm thông tin dự kiến, không nhất thiết mỗi hàng trở thành một mục menu. Giao diện trẻ đơn giản hơn parent; đổi giao diện xem không làm đổi vai trò/quyền, không có nút tự chuyển thành phụ huynh mà bỏ xác thực.

## Trạng thái phải phản ánh đúng backend

- Phân biệt “Đang gửi”, “Máy chưa kết nối”, “Đã áp dụng”, “Không thực hiện được”. Chỉ thông báo thành công sau xác nhận đúng nghĩa, không tô xanh ngay khi bấm nút.
- Offline vẫn hiển thị policy cuối và mốc cập nhật; không giả rằng quota chung đang được đồng bộ trực tiếp. Nếu tổng còn 30 phút nhưng máy này chỉ giữ 10 phút, phải giải thích hai con số, không hứa máy này dùng được cả 30.
- Giờ được giữ ở máy offline chưa thể chuyển ngay thì hiển thị lý do chờ, không cấp trùng vì thao tác UI.
- Ngoại lệ Mở khóa có đếm ngược/tác động rõ, không lẫn với Cộng 15 quota; Khóa ngay hủy ngoại lệ. App/domain rules vẫn giữ.
- Xóa dữ liệu offline hiển thị đang chờ máy xác nhận. Không dùng “đã xóa mọi nơi” khi chỉ xóa xong server.
- Dữ liệu 0, chưa có dữ liệu, đang tải, lỗi và dữ liệu cũ phải phân biệt. Không điền số mẫu vào sản phẩm như số đo thật.
- Bộ lọc/biểu đồ parent và child dùng cùng dữ liệu, thời gian và phạm vi. Không thu thêm dữ liệu chỉ để có một biểu đồ đẹp.

## Lời nhắc trẻ dự kiến

- “Còn 10 phút. Em có thể sắp xếp phần việc còn lại nhé.”
- “Còn 1 phút. Em hãy lưu bài trước khi hết giờ.”
- “Đã đến giờ nghỉ theo lịch của em. Em có thể xem lịch hoặc xin bố mẹ thêm giờ.”
- “Trang này đang được chặn theo cài đặt của bố mẹ. Em có thể trao đổi nếu cần dùng để học.”

Giữ giọng nhẹ nhàng đã chốt; không dùng hình phạt, thông điệp xấu hổ hoặc báo động liên tục. Theo D020 tạm, 60 giây lưu bài ở cuối quota, không tự cộng thêm sau quota; vẫn chờ giảng viên xác nhận.

## Thứ tự khi đến giai đoạn thực hiện

1. Hoàn thiện backend/agent/mạng bắt buộc và đi qua cổng G-UI trong IMPLEMENTATION_PLAN. Tray tối thiểu nhìn thấy được phải có sớm để agent đúng đề; chưa cần phần trang trí UI lúc đó.
2. Đọc Design-PH.md cho parent, ảnh Pinterest cho child-view và ảnh lớp cho bố cục; rà data/API thật, chốt màn hình/câu hỏi chính. Thống nhất điểm sáng/tối trong nguồn parent trước khi ánh xạ token; giữ chung cách gọi, trạng thái và dữ liệu giữa hai vai trò.
3. Làm bố cục parent/child trên desktop và mobile bằng Jinja2 + HTMX; nối dữ liệu và thao tác thật.
4. Kiểm bằng browser ở desktop/tablet/mobile, các trạng thái pending/offline/error/0 và phân quyền. Kiểm tỷ lệ tiến trình, số liệu, keyboard/focus, độ rõ chữ và thao tác chạm.
5. Chụp, tự xem và sửa các lỗi nhìn thấy; đối chiếu yêu cầu F1–F5, API/ACK và các quyết định của nhóm trước khi gọi UI đạt.

Không chạy bộ dựng UI, tạo asset/nhân vật, cài công cụ hay tạo mockup ở đợt ghi nhận này. Màu/nhân vật cuối được xem xét khi tới S4; không cần đặt thêm câu hỏi màu sắc lúc chưa thực hiện backend/mạng.
