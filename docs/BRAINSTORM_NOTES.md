# Sổ brainstorming KidSafe

## D057 — 2026-11-09: cách phát hành bản demo

Người dùng giao chọn giữa Streamlit và Git để máy khác tải bộ cài và dùng với ít bước nhất. Chọn GitHub Pages cho trang tải công khai và máy chủ KidSafe hiện có trong LAN cho dashboard/ghép đôi. Bộ cài Windows kèm runtime. Máy con dùng tệp kết nối và mã ghép do phụ huynh cấp, cùng tài khoản Windows thường. Bản Streamlit giữ vai trò xem trước dữ liệu mẫu. [Hướng dẫn phát hành](GITHUB_PAGES_DEPLOY.md)

## D056 — 2026-11-07: Mesh drift trên menu/ba bước và rà web

Người dùng cung cấp prompt Mesh drift/GLSL và yêu cầu áp dụng màu/hiệu ứng cho menu cùng ba bước, giữ nền dịu và chữ dễ đọc, cân lại cỡ chữ menu, dùng các skill đã cài để kiểm tra và sửa toàn bộ phần đã làm. Phạm vi thực thi là toàn bộ giao diện web hiện có; không lấy đó làm lệnh khóa máy/cài service/DNS trên host. Shader và uniform giữ theo nguồn; Codex chọn lớp màu phủ, giới hạn pixel/frequency và nền tĩnh dự phòng để bảo vệ độ rõ và tài nguyên. Font menu 16px/650, brand giữ cấp riêng. Bổ sung nút Tạm dừng nền chỉ cho shader mới, không khôi phục nút dừng tin nhắn đã bỏ D049. Lỗi polling/menu D047, fallback GET auth và copy child-account cũ được sửa theo quyền chỉnh lỗi trực tiếp. R-A05/R-F4-02/R-F5-01/06; giữ Jinja2/HTMX và D050.

## D055 — 2026-11-07: đính chính D054 bằng ảnh mẫu

Người dùng nói muốn như ảnh mẫu cũ, giữ lượng chữ ngắn hiện tại và thêm lại “Đồng hành trong từng khoảnh khắc.”. Cách hiểu viền đen quanh chữ ở D054 không đúng ý. Codex áp dụng nền tối chuyển sắc ở đáy ảnh với mô tả trắng, không khôi phục tiêu đề phụ/số thứ tự/Xem ảnh hoặc dòng Chọn một ảnh để khám phá. Giữ phần giới thiệu gọn và nhãn pill đã chốt trước. Đối chiếu R-A05.

## D054 — 2026-11-07: chữ trắng viền đen

Người dùng muốn câu note “Đặt hạn mức mỗi ngày và lịch trong tuần để con có thời gian học, chơi và nghỉ ngơi.” trở lại trong ảnh, chữ trắng viền đen như trước. Áp dụng nhất quán cho cả bốn mô tả, thay vị trí dưới ảnh D053. Giữ ảnh sáng, nhãn chức năng và phần giới thiệu đã làm gọn. Đối chiếu R-A05.

## D053 — 2026-11-07: giảm chữ, ưu tiên ảnh

Người dùng muốn phần Cách hoạt động ít chữ, gần ảnh hơn; bỏ dòng Chọn một ảnh để khám phá và lời dẫn Ba mẹ quản lý trên web; phóng lớn tiêu đề Cách KidSafe hoạt động. Trong ảnh chỉ giữ nhãn chức năng với pill tối bo tròn như ảnh tham chiếu; bỏ số, tiêu đề phụ và Xem ảnh, giữ một câu mô tả mỗi ảnh. Ảnh không bị che mờ. Codex đặt mô tả bên dưới ảnh trên nền kem, giữ ảnh gốc, reveal theo dòng/hover mở rộng/dialog và rút đoạn pin. D053 thay cách dùng scrim/chữ phủ ảnh của D052; không đổi thứ tự ảnh, stack hoặc chức năng sản phẩm. Đối chiếu R-A05; dùng skill thiết kế/chuyển động và kiểm chứng sau sửa theo yêu cầu.

## D052 — 2026-11-07: giới thiệu theo dòng, ảnh mở rộng

Người dùng yêu cầu làm lại phần Cách hoạt động: chữ xuất hiện theo từng dòng khi cuộn, tiếp theo là gallery mở rộng khi hover và hiện thông tin chức năng, dùng bốn ảnh đúng thứ tự đính kèm **2.jpg → 1.jpg → 3.jpg → ảnh clipboard cuối**. Khối này thay hai góc nhìn D044/D051. Component React/Framer Motion được cung cấp làm tham chiếu tương tác, không thay lựa chọn Jinja2 + HTMX của dự án. Codex chọn CSS view timeline/WAAPI, native dialog có ảnh trước/sau/Esc và bố cục đọc được trên cảm ứng; đây là quyết định triển khai. Không thêm tính năng sản phẩm mới từ ảnh hoặc đổi luồng parent-web/child-Windows D050. Đối chiếu R-A05.

## D038 — 2026-11-05: tinh chỉnh demo và mốc kết thúc ngoại lệ

Người dùng xác nhận Mở khóa tạm thời kết thúc khi phụ huynh bấm Khóa máy ngay hoặc sang ngày mới. Mốc này thay thời hạn 15 phút của D017 đối với lệnh mở khóa mới. Giờ ngoại lệ vẫn được ghi riêng. Hạn 15 phút vẫn áp dụng cho số giờ được cộng mỗi lệnh cộng giờ. Trang Thiết bị hiện mã ghép có đồng hồ và đặt lại mật khẩu tài khoản hiện có. Báo cáo có xuất CSV bảy ngày.

## D036 — 2026-11-05: năm nhóm ứng dụng có lịch và quỹ riêng

Người dùng yêu cầu năm nhóm với cấu hình ứng dụng theo tên và SHA-256, chế độ quỹ, khung giờ, khóa nhanh và lời nhắn. Quyết định triển khai: khung giờ riêng cùng ngày giới hạn thêm lịch chung, nhóm chặn tuyệt đối luôn khóa, và danh sách allowlist/blocklist cũ vẫn có thể chỉnh trong mục nâng cao. Định danh SHA-256 ưu tiên khi tính giờ để đổi tên tệp không đổi nhóm. Chặn xét các quy tắc khớp và luôn áp dụng nhóm chặn tuyệt đối. Tính quỹ theo ứng dụng chạy trên máy, nên một trình duyệt đã đưa vào nhóm được tính toàn bộ thời gian dùng.

## D035 — 2026-11-05: lịch tuần và chặn khi hết quỹ giải trí

Người dùng yêu cầu thực thi chặn với nhóm giải trí đã chọn ở D034, bắt buộc quỹ không vượt cả hai hạn mức ngày, và cập nhật lưới lịch, tổng ngày, cảnh báo, vị trí nút và chú thích. Cách triển khai của Codex: giữ ứng dụng học tập trong luồng quota thường, cộng số giây máy khác đã báo vào bộ đếm cục bộ để quyết định chặn, giữ phần chia offline ở trang Thiết bị. Quỹ nhóm chưa có cơ chế phân bổ offline riêng.

## D034 — 2026-11-05: trang điều khiển và quỹ giải trí

Người dùng yêu cầu bỏ quick actions khỏi Tổng quan, thêm /app/quick-control với chọn thiết bị/trạng thái và ba thẻ đều nhau; đổi thẻ bên phải thành Công cụ & Kiểm soát, hai thống kê app/domain và hai nút lịch/điều khiển. Nhãn Đang xem phải một dòng; form quota ba cột, thêm phút giải trí lưu policy; KPI giải trí dùng số liệu thật và ba chân KPI thẳng hàng.

Đã hỏi cách tính quỹ giải trí; người dùng chọn: **phụ huynh chọn ứng dụng thuộc nhóm giải trí, chỉ thời gian dùng các ứng dụng đó mới trừ quỹ**. Không tính toàn bộ thời gian máy hoặc suy thời lượng từ số truy vấn DNS. Lựa chọn triển khai của Codex: gợi ý60phút cho ô mới, không thay quota ngày thường/cuối tuần đang có; danh sách giải trí riêng trên trang Ứng dụng, counter dùng foreground/idle đã có và gửi aggregate heartbeat, giữ nguyên7trường/9loại sự kiện. Phạm vi lần này là cấu hình/bộ đếm/báo cáo dashboard; không tự nhận nghiệm thu đầy đủ NC enforcement/offline hoặc Windows native.

Đối chiếu R-F1-01/03/06, R-F3-01/02/03, R-F4-02/04 và D017. Đếm app và miền hiệu lực từ policy; giữ ACK/lịch/quota chung cho ba lệnh. Nguồn màu/type và Jinja2/HTMX/CSS local giữ nguyên.

## D033 — 2026-11-05: chữ dễ đọc và dashboard phụ huynh

Người dùng yêu cầu rà toàn bộ web về cỡ chữ, lệch hàng/xuống dòng và đọc file tinh chỉnh đính kèm. Nguồn giữ nguyên tại `sources/PARENT_UI_REFINEMENTS_2026-11-05.txt`: tài khoản một dòng/15–16px; gear chứa audit/xóa/logout; bảy icon sidebar và bỏ mục privacy; tăng breadcrumb/H1/card heading; bỏ các phụ đề/footer được chỉ định; ba KPI có icon/progress; quick actions; thẻ lịch và ba thống kê bên phải.

Đã áp dụng trong Jinja2/HTMX/CSS local. Phân biệt yêu cầu trực tiếp với ví dụ: các số 1g45p/2g/15p/60p và khung 19:30–21:00 không phải dữ liệu hoặc quota đã chốt. Backend chưa có hạn mức giải trí NC R-F1-06, nên card hiển thị chưa có hạn mức riêng; trạng thái lịch hiện tại thay cho giờ cao điểm là phương án file đã cho phép. Không đổi D017, thêm schema sự kiện, Tailwind/CDN/build npm, hoặc ghi nhận người dùng đã chốt một quota giải trí.

Kiểm chứng/giới hạn trong `evidence/parent-refinement-2026-11-05/README.md`. Không phát sinh quyết định cần hỏi lại trước phần chỉnh UI này.

## D032 — 2026-11-05: dùng ảnh gia đình người dùng cung cấp

Người dùng yêu cầu thay minh họa đang có ở login bằng ảnh đính kèm và thêm dấu chấm cuối H1. Đã thay SVG bằng PNG gốc, giữ nguyên nội dung/byte ảnh, điều chỉnh kích thước bằng CSS (desktop tối đa420px, mobile320px, chiều cao tự động). H1 là “Một chút cân bằng, nhiều hơn kết nối.”. Không thêm lại các đoạn mô tả/slogan đã bỏ. D031 về SVG cũ là lịch sử, ảnh mới theo yêu cầu trực tiếp thay thế minh họa đó.

## D031 — Bớt chữ ở login, minh họa không chứa chữ/số

Người dùng yêu cầu bỏ hai đoạn mô tả/slogan được chỉ định, nối H1 thành một câu, thay khối K bằng SVG đồng hành phụ huynh/trẻ/máy tính/đồng hồ/khiên/vòng kết nối. SVG dùng đúng xanh rêu #4A5D4E, be #E6DEC8 và kem hiện có, cao140–160px. Đã áp dụng; không thêm slogan mới vì người dùng yêu cầu bớt câu chữ. Phần nhắc slogan ở cuối yêu cầu được hiểu là cân đối bố cục, không khôi phục câu đã chỉ định bỏ. Evidence trong docs/evidence/login-connection; D030 giữ làm lịch sử.

## D030 — Tỷ lệ chữ và căn chỉnh trang đăng nhập

Người dùng yêu cầu giữ bảng màu kem/xanh rêu, chuẩn hóa typography cột trái, tăng phân cấp chữ/form cột phải, căn giữa hai cột, thu minh họa20–25% và gom slogan. Đã áp dụng riêng /login: H1 desktop40px, logo24px, eyebrow14.5px, body16px, cardheading24px, input46px; nhóm figure+slogan và shrink25%. Chi tiết code/ảnh/browserchecks trong UI_IMPLEMENTATION và docs/evidence/login-refinement. Không đổi quy tắc sản phẩm/auth.

## D029 — Chỉ có một máy vật lý

Người dùng xác nhận hiện chỉ có thể chạy trên máy của mình và cần hướng dẫn từng bước cho người mới. Thay phương án lab hai máy vật lý bằng host chạy server/web + một WindowsVM chạy agent dưới user thường. Đây là topology kiểm thử mới thay D011 ở điều kiện lab hiện tại, không bỏ yêu cầu Windows/thành phần/khả năng chạyLAN. Chưa cài VM hoặc kết luận native tests đã đạt. Hướng dẫn ONE_PC_SETUP; đề xuất NAT default10.0.2.2 với localhostreachable, profile riêng .runtime/vm, localhost8446 chohost và10.0.2.2:8446 choguest. MộtVM chưa đủ bằngchứng hai thiếtbịtrẻ dùngquota chung.

## D028 — Tiếp tục hoàn thiện toàn bộ ứng dụng

Người dùng yêu cầu chỉ ngừng khi xong app và trao toàn quyền tự làm, không hỏi thêm. Theo chỉ đạo mới nhất, tiếp tục hoàn thiện UI/luồng app khi chưa có máy lab; G-UI vẫn là cổng **nghiệm thu**, không coi việc dựng UI là bằng chứng Windows đã đạt. Không lấy thiếu lab làm lý do ngừng các phần có thể tự triển khai/kiểm tra.

Chi tiết do Codex tự chọn trong phạm vi D028: parent theme sáng theo phần Colors của Design-PH; khung framed-sheet/tokens ghi UI_IMPLEMENTATION. Audit bảo mật chỉnh giờ ở bảng riêng tối thiểu, giữ nguyên 7 trường/9 loại event; đây là giải pháp kỹ thuật đề xuất trước đó, không phải xác nhận giảng viên cho điểm mơ hồ nguồn. D020/D021 vẫn giữ.

## D027 — 2026-11-04: bắt đầu triển khai tự chủ

Người dùng yêu cầu bắt đầu mọi việc theo plan, trao quyền tự thực hiện khi vắng mặt, không hỏi thêm và kiểm tra bug sau mỗi phần. Đã mở cổng triển khai; các dòng chưa có lệnh bắt đầu phía dưới là lịch sử trước D027. Codex tự chọn chi tiết kỹ thuật và ghi lý do; D019/D020/D021 vẫn giữ. Theo trao đổi ngay trước đó, điều phối Sol High triển khai, Astra Low rà soát độc lập. Không thay model của phiên chính.

## Cách ghi nhớ

Mỗi câu trả lời được ghi bằng ngày, mã câu hỏi, nội dung người dùng, quyết định và tác động đến yêu cầu/thiết kế/kiểm thử. Gợi ý của AI không phải quyết định của người dùng. Không xóa lịch sử khi đổi ý: ghi quyết định mới thay thế quyết định cũ.

Trạng thái quyết định: **Chờ trả lời / Đề xuất / Đã chốt / Đã thay thế**. Mỗi đợt chỉ hỏi 2–3 câu có ích cho bước kế tiếp; chưa có câu trả lời thì tiếp tục phần chuẩn bị độc lập, giữ nguyên những điểm chưa chốt.

## 2026-11-03 — Yêu cầu ban đầu

### Những điều đã xác nhận trực tiếp

| ID | Quyết định | Nguồn | Tác động |
| --- | --- | --- | --- |
| D001 | Đọc kỹ DoAn01 trước khi lập kế hoạch | Yêu cầu người dùng | REQUIREMENTS là chuẩn đối chiếu |
| D002 | So sánh bản Gemini, bổ sung thiếu sót, trình bày để người dùng kiểm tra | Yêu cầu người dùng | GEMINI_REVIEW và kế hoạch bổ sung |
| D003 | Chủ động hỏi ý tưởng, ghi vào file brainstorming | Yêu cầu người dùng | Duy trì chính file này |
| D004 | Chuẩn bị file lưu từng bước để tiếp tục khi được gọi làm | Yêu cầu người dùng | IMPLEMENTATION_PLAN và PROJECT_STATE |
| D005 | Chưa bắt đầu phần mềm; chỉ bắt đầu khi người dùng yêu cầu | Yêu cầu người dùng | Không viết mã/cài gói/sửa hệ thống hiện tại |
| D006 | Có lệnh ghi nhớ phải đúng yêu cầu đồ án | Yêu cầu người dùng | Quy tắc bắt buộc trong AGENTS.md |

### Đợt 1 — Đã trả lời

| ID | Câu hỏi | Gợi ý, chưa phải quyết định | Trả lời/trạng thái |
| --- | --- | --- | --- |
| B001 | Nhóm mấy người, hạn nộp ngày nào, có máy Windows nào/quyền admin nào để thử? | Đề quy định nhóm 3, 6 tuần; cần biết điều kiện thực | “nhóm 3 người hạn còn 5 tuần dùng win 11 hết và có quyền quản trị hết”; đã chốt điều kiện này, chưa có ngày nộp chính xác/số máy |
| B002 | Chọn dashboard Jinja2 + HTMX, React nhẹ hay cần xem phác trước? | Ít thành phần, thuận lợi cho người mới và cài máy sạch | Người dùng chọn Jinja2 + HTMX; đã chốt |
| B003 | Tên ứng dụng và ý tưởng trải nghiệm trẻ/phụ huynh? | Có thể giữ OGK; lời nhắc tích cực, dễ hiểu | “KidSafe đi”; đã chốt tên KidSafe, chưa chốt chi tiết phong cách/lời nhắc |

### Quyết định bổ sung từ đợt 1

| ID | Quyết định | Tác động |
| --- | --- | --- |
| D007 | Tên KidSafe, giữ OGK làm tên tham chiếu đề | Đổi tên hồ sơ chuẩn bị, không đổi yêu cầu gốc |
| D008 | Jinja2 + HTMX | Không lên kế hoạch học/thiết lập React; giảm số thành phần |
| D009 | Nhóm 3 người, còn 5 tuần | Lịch nén 5 tuần, ưu tiên BB, chưa bịa ngày nộp/phân công |
| D010 | Lab Windows 11, người cài có quyền admin | Dùng user thường riêng cho trẻ; chưa tuyên bố đã test Windows 10 |

### Đợt 2 — Đã trả lời, B006 được bổ sung ở đợt 6

| ID | Câu hỏi đã gửi | Phương án gợi ý | Trạng thái |
| --- | --- | --- | --- |
| B004 | Server đặt LAN/VPS hay chỉ có một máy cần lab riêng? | LAN một máy server, máy khác là máy trẻ, điện thoại cùng Wi-Fi | Người dùng chọn LAN: một máy server, máy khác đóng vai máy trẻ; đã chốt |
| B005 | Mất kết nối quá N ngày thì giữ chặn hay tạm ngừng? | Mốc 3 ngày và fail-mode đã đưa ra thảo luận | “Sau 3 ngày vẫn giữ hạn mức và lịch cuối cùng đã nhận (fail-closed)”; đã chốt |
| B006 | Có bản đề bổ sung D1/NT5/các mục vắng không? Có thể hỏi giảng viên về 50/60 miền và ân hạn không? | Giữ trạng thái chưa xác nhận nếu chưa có nguồn | Đợt 6: người dùng xác nhận chỉ có DoAn01 đã gửi, ghi điểm chưa rõ để hỏi giảng viên; chưa có trả lời giảng viên |

### Đợt 3 — Đã trả lời

| ID | Câu hỏi | Trả lời/trạng thái |
| --- | --- | --- |
| B007 | Hình thức nhắc trẻ khi gần hết giờ? | “Nhẹ nhàng: báo thời gian còn lại, nhắc lưu bài, nút xin thêm giờ”; đã chốt; vẫn giữ mốc 10/5/1 và grace 60 giây theo đề |
| B008 | Một trẻ có hai máy thì quota tính chung hay riêng? | Người dùng chọn dùng chung 90 phút cho cả hai máy trong ví dụ; đã chốt **quota theo trẻ, dùng chung giữa thiết bị**, không chốt quota cố định 90 phút cho mọi trẻ |

### Quyết định bổ sung từ đợt 2–3

| ID | Quyết định | Tác động/kiểm chứng |
| --- | --- | --- |
| D011 | Server trong LAN, máy server riêng với máy trẻ | Thiết kế/hướng dẫn TLS/pinning và test mobile trong LAN; không lên kế hoạch triển khai VPS hay mở Internet |
| D012 | Sau 3 ngày offline vẫn giữ quota/lịch policy cuối (fail-closed) | Kiểm trước/đúng/sau ngưỡng và sau reconnect/restart; không tự cấp thêm quota do mất mạng. Không hiểu là khóa máy vô điều kiện từ ngày thứ 3: vẫn tuân theo lịch/quota cuối hợp lệ |
| D013 | Quota theo trẻ, tổng dùng chung giữa các thiết bị | Ví dụ 90 phút chỉ để minh họa. Cơ chế offline được chốt tiếp ở D015, không cấp đủ quota cho từng máy |
| D014 | Cảnh báo nhẹ nhàng, thời gian còn lại + lưu bài + xin thêm giờ | Cập nhật flow tray/dashboard; không đổi các mốc bắt buộc hoặc âm thầm thêm grace |

### Đợt 4 — Đã trả lời, B012 được bổ sung ở đợt 6

| ID | Câu hỏi đã gửi | Gợi ý, chưa phải quyết định | Trạng thái |
| --- | --- | --- | --- |
| B010 | Chia quota offline giữa thiết bị thế nào? | Chia trước phần ngân sách, tổng không vượt quota; điều chỉnh khi có mạng. Phương án khác: chỉ một máy được dùng offline | Người dùng chọn chia trước ngân sách offline từng máy, tổng không vượt quota; đổi phần chia khi có mạng. Đã chốt |
| B011 | Nút Mở khóa khi ngoài lịch được làm gì? | Ngoại lệ 15 phút có audit rồi trở về lịch/quota; phương án khác là phải sửa lịch | Người dùng chọn ngoại lệ 15 phút, ghi audit, hết thời gian quay về lịch/quota. Đã chốt; phần quota cạn/lệnh khác được chốt tiếp ở B013/D017 |
| B012 | Tên, kỹ năng và giờ/tuần của ba thành viên? | Dùng để phân công thực tế; chưa tự điền tên hoặc % đóng góp | Đợt 6: người dùng chọn để trống phân công, cung cấp thông tin thành viên sau; không tự gán vai trò A/B/C |

### Quyết định bổ sung từ đợt 4

| ID | Quyết định của người dùng | Tác động/kiểm chứng |
| --- | --- | --- |
| D015 | Chia trước ngân sách offline từng máy, tổng không vượt quota; đổi phần chia khi có mạng | Thiết kế sổ ngân sách theo trẻ/ngày/thiết bị và chống cấp trùng. Máy cho đi phải xác nhận trả phần chưa dùng trước khi phần đó được cấp lại; không lấy việc máy offline làm bằng chứng giờ đã được trả. Đây là ràng buộc kỹ thuật đề xuất để thực hiện đúng lựa chọn, chưa có code |
| D016 | Mở khóa ngoài lịch cho ngoại lệ 15 phút, ghi audit, hết hạn trở về lịch/quota | Kiểm thời hạn/ACK/retry/reboot/thu hồi, không tự gia hạn. Tương tác quota cạn và các lệnh được bổ sung tại D017 |

### Đợt 5 — Đã trả lời

| ID | Câu hỏi đã gửi | Các phương án đã hỏi | Trạng thái |
| --- | --- | --- | --- |
| B013 | Quy tắc Cộng giờ/Mở khóa/Khóa ngay, khi quota cạn và phạm vi chặn app/domain? | Cộng 15 tăng quota chung không bỏ lịch; Mở khóa cho tối đa 15 phút dù ngoài lịch/hết quota, ghi giờ ngoại lệ; Khóa ngay hủy ngoại lệ; vẫn giữ app/domain rules. Lựa chọn khác: Mở khóa chỉ vượt lịch nếu còn quota | Người dùng chọn “Đồng ý bộ quy tắc này”; đã chốt bộ quy tắc đầy đủ |
| B009 | Ưu tiên phần NÊN CÓ sau BB? | DoH + chống đổi DNS, hoặc gỡ hợp pháp + CSV, hoặc hoãn chọn để tập trung BB | Người dùng chọn DoH và chống đổi DNS, phù hợp trọng tâm mạng; đã chốt ưu tiên sau BB |

### Quyết định bổ sung từ đợt 5

| ID | Quyết định của người dùng | Tác động/kiểm chứng |
| --- | --- | --- |
| D017 | Cộng 15 phút tăng quota chung, không bỏ lịch; Mở khóa cho tối đa 15 phút dù ngoài lịch hoặc quota hết, ghi giờ ngoại lệ; Khóa ngay hủy ngoại lệ; mọi lệnh giữ app/domain rules | Ghi rõ quota gốc, tăng quota và ngoại lệ riêng. Chống replay, giới hạn 15 phút, hủy ngoại lệ khi khóa, hết hạn quay về policy; không nhân giờ ngoại lệ cho từng máy. Bộ này bổ sung chi tiết D016, không thay đổi yêu cầu gốc |
| D018 | Sau khi BB đạt, ưu tiên DoH và chống đổi DNS | S7/S9/M3 có nhánh NC rõ; gỡ bằng mật khẩu, CSV/PDF, quota nhóm và điểm thưởng chưa được cam kết triển khai |

Các điểm kỹ thuật còn phải mô tả trước bước liên quan: hết ngoại lệ có grace không, tỷ lệ chia offline mặc định, timezone/rollover, IPC/lifecycle tray; không tự gán lựa chọn chưa trả lời thành quyết định của nhóm.

### Đợt 6 — Đã trả lời

Đã đưa B006/B012 về dạng lựa chọn ngắn và nhận các câu trả lời dưới đây.

| ID | Câu hỏi/điểm cần chốt | Phương án đã đưa ra | Trạng thái |
| --- | --- | --- | --- |
| B006 (hỏi lại) | Nguồn cho D1/NT5 và mâu thuẫn DNS 50/60 | Chỉ có DoAn01 và sẽ hỏi giảng viên; có nội dung bổ sung sẽ cung cấp sau; hoặc chưa biết | “Chỉ có DoAn01 đã gửi; ghi các điểm chưa rõ để hỏi giảng viên”; đã ghi D019 |
| B014 | Ân hạn 60 giây tính trong hay sau quota? | Đề xuất để xin xác nhận: 60 giây cuối nằm trong quota (quota 3 phút khóa ở phút 3); hoặc thêm 60 giây sau quota (khóa phút 4); hoặc chờ giảng viên. Chưa coi lựa chọn nhóm là xác nhận của giảng viên | Người dùng chọn 60 giây cuối nằm trong quota, quota 3 phút khóa ở phút 3. D020 là phương án chuẩn bị, đang chờ giảng viên xác nhận |
| B012 (hỏi lại) | Phân công khi chưa có tên/kỹ năng | Vai trò tạm A server/bảo mật, B agent/Windows, C web/DNS; cả ba test/report; hoặc chờ thông tin/tự chia khác. Không tự điền % đóng góp thật | “Để trống phân công, tôi sẽ cung cấp thông tin thành viên sau”; đã chốt D021 |

### Quyết định bổ sung từ đợt 6

| ID | Quyết định của người dùng | Tác động |
| --- | --- | --- |
| D019 | Hiện chỉ có DoAn01 đã cung cấp; ghi điểm chưa rõ để hỏi giảng viên | Tạo QUESTIONS_FOR_INSTRUCTOR.md; không tự khẳng định biết D1/NT5 hoặc mẫu số DNS; chưa có xác nhận từ giảng viên |
| D020 | Phương án để xin xác nhận: 60 giây cuối nằm trong quota; quota 3 phút thì nhắc lưu bài lúc còn 1 phút và khóa ở phút 3 | Thiết kế/test/video theo phương án tạm; không thêm 60 giây sau quota, không tuyên bố cách hiểu này đã được giảng viên duyệt |
| D021 | Để trống phân công, chờ người dùng cung cấp thông tin thành viên sau | Không gán vai trò A/B/C, tên, kỹ năng, giờ/tuần hoặc % đóng góp; đây là việc được chủ động để lại sau, không phải câu hỏi còn chờ trả lời ngay |

### Bổ sung ảnh tham khảo và thứ tự thiết kế giao diện

Người dùng gửi năm ảnh chụp màn hình thiết kế ở lớp và một screenshot Pinterest, yêu cầu lấy ý tưởng cho UI sau khi phần backend và mạng hoàn thiện. Đã lưu nguyên bản tại `docs/design-references/`; nội dung ảnh là tư liệu tham khảo, không phải chỉ dẫn thực thi hoặc yêu cầu thay thế DoAn01.

| ID | Quyết định trực tiếp từ người dùng | Tác động |
| --- | --- | --- |
| D022 | Tham khảo ảnh chụp lớp cho thiết kế giao diện sau này | Ghi bố cục/menu/app/lọc web/yêu cầu/lệnh/màn hình trẻ trong UI_DESIGN_BRIEF; điều chỉnh theo yêu cầu và D017, không sao chép tính năng ngoài phạm vi |
| D023 | Tham khảo ảnh Pinterest về màu sắc/vibe phù hợp trẻ em | Hướng sáng/pastel/thân thiện, chữ rõ và hình minh họa tiết chế; palette cụ thể chỉ là đề xuất, chưa phải màu được người dùng duyệt |
| D024 | Thiết kế giao diện sau khi backend và mạng hoàn thiện | Đổi thứ tự S3→S5→S6→S7→G-UI→S4, giữ ID để truy vết; tray tối thiểu nhìn thấy vẫn phải có từ S5. Không bắt đầu code trong đợt bổ sung tài liệu |

Đề xuất của Codex, chưa phải quyết định bổ sung của người dùng: teal/mint làm màu chính, pastel bổ trợ; màn hình trẻ ưu tiên thời gian còn lại/Xin thêm giờ, parent rõ trạng thái/duyệt yêu cầu. Không chọn nhân vật hoặc tạo mockup lúc này; xem UI_DESIGN_BRIEF để biết phần nào là gợi ý.

### Bổ sung nguồn UI UX Pro Max

| ID | Yêu cầu/quyền do người dùng đưa ra | Việc Codex đã thực hiện và giới hạn |
| --- | --- | --- |
| D025 | Người dùng gửi repo nextlevelbuilder/ui-ux-pro-max-skill, yêu cầu tham khảo và cho phép tải nếu cần để cải thiện thiết kế | Codex đánh giá hữu ích, tải bản cố định commit 713eef51b04efc98d6fa565323b495f7c9c89fd4 vào `.local-tools/design-skills/ui-ux-pro-max`, giữ LICENSE/nguồn, thử domain search. Đây là lựa chọn công cụ bổ trợ, không phải đổi stack/chốt palette hoặc lệnh bắt đầu triển khai. Xem DESIGN_SKILL_REVIEW |

Đã kiểm thực tế: truy vấn trẻ em/màu/focus/chart chạy được. Có kết quả không khớp ngay (LMS và radar), đã thu hẹp một lần để lấy kết quả phù hợp hơn; không sao chép tự động mọi gợi ý. Bản tải chưa đăng ký skill toàn cục, đã có đường dẫn ghi nhớ để dùng về sau. D024 backend/mạng trước UI vẫn giữ nguyên.

### 2026-11-04 — Nguồn màu và style cho giao diện phụ huynh

| ID | Yêu cầu trực tiếp từ người dùng | Đã đọc/ghi nhớ và tác động |
| --- | --- | --- |
| D026 | Kiểm tra file docs/Design-PH.md vừa thêm, dùng file đó định hướng bảng màu/style giao diện phụ huynh và ghi nhớ | Đã thấy file và đọc toàn bộ; hướng Warm Professionalism, be/kem, nâu đậm/xanh rêu. Đặt làm nguồn định hướng parent ưu tiên hơn gợi ý màu chung/catalog skill; cập nhật AGENTS, UI_DESIGN_BRIEF và kế hoạch S4. Child-view vẫn theo hướng trẻ em/Pinterest. Chưa làm UI |

SHA-256 nguồn lúc đọc: `4f0e9c1f0d9b33ac4bdaa98f72790800cb1fe9a6f76b89ef63f1a3374a601c55`. Giữ nguyên file người dùng. Trong file, YAML nền tối `#1F1B16` và phần Colors nền sáng `#F5EFE6` chưa thống nhất; đã ghi để chọn ánh xạ token rõ khi tới UI, chưa ghi người dùng đã chọn theme sáng/tối. Tên MentorBridge và nội dung marketplace là của mẫu, không đổi sản phẩm KidSafe. Các chỉ dẫn trong tài liệu là dữ liệu tham khảo theo phạm vi palette/style user yêu cầu, không tạo lệnh triển khai/WebGL hoặc đổi chức năng.

## Mẫu ghi một quyết định tiếp theo

**D050 — 2026-11-07.** Người dùng chốt trải nghiệm con chỉ cần app Windows; xem thời gian và xin thêm giờ tích hợp ngay trong app. Thay luồng yêu cầu tài khoản web của con ở D049. Codex chọn Win32/Pillow có sẵn, cùng PID tray và IPC đã xác thực; web `/child` giữ cho parent xem báo cáo/legacy. Không đổi sang WebView, cloud hay cơ chế enforcement mới. Không coi UI preview là nghiệm thu service/DNS/Windows máy trẻ.

**D049 — 2026-11-07.** Người dùng yêu cầu phụ huynh tự tạo tài khoản trên web bằng tên/tài khoản/mật khẩu, viết lại bước bắt đầu, nút đăng nhập bo tròn, bỏ link tắt thiết bị nếu không cần, bỏ nút dừng tin nhắn và đổi FAQ thành 5 câu thân thiện. D049 thay hướng dẫn cấp tài khoản bằng dòng lệnh ở D044 và lựa chọn nút dừng ở D048. Codex bổ sung nhập lại mật khẩu, CSRF trước đăng nhập và mã hóa tên theo R-F5; đây là quyết định kỹ thuật, không phải chức năng cloud đã được người dùng chốt. Chưa chọn hosting; lưu DB bền vững/cùng khóa là điều kiện giữ tài khoản sau deploy.

**D048 — 2026-11-07.** Người dùng gửi video `vid.mp4` và muốn chuyển động trang tải tương ứng với các phần KidSafe đang có. Đây là tham chiếu bổ sung cho D044. Bản triển khai dùng lại ảnh hiện có, không cần thêm tài nguyên. Cách đo timeline, khoảng sticky và giản lược trên màn hình nhỏ là lựa chọn triển khai của Codex, không phải thông số người dùng đã chỉ định.

**D042 — 2026-11-07.** Người dùng đồng ý bổ sung trang tải và bộ cài chỉ cho Windows, dùng lại mã ghép đôi 10 phút. Giữ server trong LAN. Bản triển khai x64 gói runtime và dùng tệp kết nối riêng do dashboard xuất. Máy Windows riêng có thể cài trực tiếp. Lab một máy vẫn cần guest để kiểm thử tác động thật.

- Ngày giờ (Asia/Saigon): …
- Mã câu hỏi: …
- Người dùng trả lời: …
- Quyết định đã chốt: …
- Lý do/giới hạn: …
- Thay thế quyết định nào, nếu có: …
- ID yêu cầu bị ảnh hưởng: …
- File đã cập nhật: …
- Cách kiểm chứng sau này: …

## Những điều chưa được quyết định

Đã có câu trả lời B001–B014, D022–D025 cho ảnh/công cụ UI và D026 chỉ định Design-PH.md cho parent. Không có câu hỏi brainstorming đang chờ người dùng; theme sáng/tối/token cuối của parent để thống nhất khi tới S4, child-view vẫn hướng Pinterest. Thành viên/phân công chủ động để trống D021; ngày nộp cụ thể chưa cung cấp. Nguồn D1/NT5, mẫu số DNS và ân hạn chờ giảng viên; D020 là phương án tạm. Chưa có lệnh bắt đầu triển khai.
