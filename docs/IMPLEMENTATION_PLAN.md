# Kế hoạch thực hiện khi được yêu cầu bắt đầu

**Sau D028:** S1–S3 có code/migration/seed/TLS và kiểm thử; S5–S7 có runtime/installer/appmonitor/DNS/rollback nhưng Windows lab chưa nghiệm thu. S4 có parent/child Jinja2/HTMX nối API thật và19browserchecks. S8/S9 có92test tự động gồm WebSocket TLS, quota/replay/deletion; không thay phép đo Windows. G-UI giữ là cổng nghiệm thu nền. S10–S12 (số đo/capture/báo cáo/video/nghiệm thu máy sạch) còn thiếu bằng chứng thực; không gọi đồ án sẵn sàng nộp.

**Cập nhật 2026-11-04: đã nhận lệnh bắt đầu D027. S1–S3/S5–S7 đang triển khai; trạng thái chi tiết ở PROJECT_STATE và IMPLEMENTATION_LOG. Các dòng chưa bắt đầu bên dưới là mốc ban đầu, không còn là cổng chờ quyền.**

**Đây là kế hoạch, không phải lịch sử đã làm. Hiện chỉ S0 phần đọc/đối chiếu/lập hồ sơ đã thực hiện; các bước phần mềm chưa bắt đầu.**

Lệnh ghi nhớ: mọi bước phải đúng DoAn01 theo REQUIREMENTS.md; không bỏ yêu cầu bắt buộc, không tự nhận đạt khi chưa kiểm chứng. Người dùng phải yêu cầu bắt đầu rõ ràng trước S1. Đề ghi 6 tuần nhưng người dùng xác nhận **còn 5 tuần**, nhóm 3 người, Windows 11/admin, tên **KidSafe**, dashboard **Jinja2 + HTMX**. Kế hoạch dưới đây điều chỉnh theo 5 tuần còn lại; chưa suy ra ngày nộp chính xác.

Quyết định đã bổ sung: **LAN, máy server riêng; sau 3 ngày offline giữ quota/lịch cuối; quota chung theo trẻ, chia ngân sách offline trước từng máy và điều chỉnh khi có mạng; lời nhắc nhẹ nhàng/lưu bài/xin thêm giờ; mở khóa ngoài lịch có ngoại lệ 15 phút, audit và tự trở về lịch/quota**. Thiết kế chuyển ngân sách phải tránh cấp trùng khi máy cho đi chưa xác nhận trả.

Bộ lệnh D017 đã duyệt: Cộng 15 tăng quota chung không bỏ lịch; Mở khóa tối đa 15 phút dù ngoài lịch/quota hết, ghi giờ ngoại lệ; Khóa ngay hủy ngoại lệ; vẫn giữ chặn app/domain. D018: sau BB, ưu tiên NC DoH/chống đổi DNS; chưa cam kết các NC/CTT khác.

**Điều chỉnh mới D022–D024:** dùng ảnh chụp lớp làm tham khảo bố cục/luồng, screenshot Pinterest làm tham khảo màu sắc và cảm giác trẻ em; xem [UI_DESIGN_BRIEF](UI_DESIGN_BRIEF.md). **Hoàn thiện backend và mạng bắt buộc trước rồi mới thiết kế/dashboard S4.** Giữ mã bước để không phá truy vết; thứ tự thực hiện là **S1 → S2 → S3 → S5 → S6 → S7 → G-UI → S4 → S8 → S9 → S10 → S11 → S12**. Kiểm thử và ghi evidence thực hiện xuyên suốt, không chờ đến S9 mới thử.

## Phân bổ 5 tuần đã điều chỉnh

| Tuần còn lại | Trọng tâm và mốc |
| --- | --- |
| 1 | S0 đủ quyết định → S1/S2 và lõi S3; có enrollment/TLS/policy/event đi qua thật |
| 2 | Hoàn thiện S3/S5, bắt đầu S6; service/tray tối thiểu nhìn thấy, IPC/cache và thử luồng bằng API/test client |
| 3 | Hoàn thiện S6/S7, capture/phép đo mạng sớm; qua G-UI rồi mới bắt đầu S4 ở cuối tuần nếu đủ điều kiện |
| 4 | S4/S8/S9 và số đo S10; dashboard parent/child, tích hợp, sửa lỗi, ≥15 unit/5 integration, M1–M6/raw data |
| 5 | Hoàn thiện S10/S11/S12: báo cáo/video/máy sạch/vấn đáp; dành phần cuối tuần cho lỗi nghiệm thu |

Không dùng lịch gấp để cắt phần BB. Các phần NC/CTT chỉ làm sau khi mốc BB liên quan ổn định. Báo cáo/evidence/AI_USAGE được cập nhật cùng tiến độ, không dồn mọi thứ đến cuối. **Theo D021, để trống phân công**, chờ người dùng cung cấp thông tin thành viên sau; không tự gán cả vai trò A/B/C hoặc % đóng góp.

## Quy tắc cho từng bước

1. Đọc quyết định mới nhất và chọn ID yêu cầu liên quan.
2. Giải thích ngắn mục tiêu, tự thao tác phần được giao; không đẩy lệnh có thể tự làm sang người mới.
3. Làm một lát chức năng nhỏ, chạy và kiểm tra trước khi nối thêm.
4. Ghi đầu ra, lệnh thực tế, kết quả thật, giới hạn/chưa đạt và bằng chứng; cập nhật README, PROJECT_STATE, AI_USAGE.
5. Khi có quyết định cần hỏi, đưa 2–3 câu ngắn và ghi trả lời vào BRAINSTORM_NOTES. Không hỏi lại phần đã được cho phép.

## S0 Hoàn thiện chuẩn bị — trước triển khai

- Đầu vào: đề gốc, bản Gemini, mong muốn của người dùng.
- Việc đã làm: ma trận yêu cầu, review thiếu sót, hồ sơ Markdown, sáu đợt brainstorming; lưu sáu ảnh tham khảo, định hướng UI và thứ tự backend/mạng trước UI theo yêu cầu bổ sung.
- Đã chốt: nhóm 3/còn 5 tuần/Windows 11/admin; KidSafe; Jinja2 + HTMX; server LAN riêng; 3 ngày offline giữ quota/lịch cuối; quota chung chia offline trước từng máy; bộ lệnh D017; lời nhắc nhẹ nhàng; ưu tiên NC D018. D020 là phương án tạm: 60 giây cuối trong quota, 3 phút khóa ở phút 3, chờ giảng viên xác nhận. D019: chỉ có DoAn01, câu hỏi nguồn lưu riêng. D021: để trống phân công. Số máy/ngày nộp cụ thể chưa cung cấp; tỷ lệ chia mặc định/lifecycle/ordering/hạch toán là chi tiết thiết kế cần đề xuất có lý do trước bước liên quan.
- Đầu ra: hồ sơ đã được người dùng rà soát; các quyết định ghi đúng nguồn; phần chưa thể hỏi giảng viên có giả định rõ và người dùng biết.
- Hồ sơ bản 1 đã đủ để người dùng rà soát. Điều kiện sang triển khai: lệnh bắt đầu rõ ràng và kiểm tra các giả định ảnh hưởng bước sắp làm; các điểm chờ giảng viên vẫn phải được giữ trạng thái chưa xác nhận. Không tự chuyển vì người dùng chỉ trả lời brainstorming hoặc duyệt hồ sơ.

## S1 Chuẩn bị công cụ và khung kho — tuần 1

- Kiểm tra Windows x64, Python ≥3.11, môi trường ảo và quyền lab; chọn bản dependency tương thích tại thời điểm làm, khai báo manifest và lockfile phù hợp.
- Tạo `/agent`, `/server`, `/dashboard`, `/tests`, `/demo`; cấu hình ignore cho venv/cache/runtime DB, khóa, cert riêng, kết quả sinh. Không sửa nội dung `.agents` có sẵn.
- Tách cấu hình ví dụ với bí mật thật; soạn script chạy/dừng lab, mô tả môi trường và hướng hoàn nguyên.
- Đầu ra: khung import/chạy tối thiểu và hướng dẫn tái tạo; chưa gọi đó là sản phẩm đủ chức năng.
- Kiểm chứng: cài dependency theo manifest/lockfile trong môi trường sạch, khởi động/dừng được; ghi lệnh thực vào README/AGENTS.
- Yêu cầu: R-A01, R-D01/02/03/09.

## S2 Thiết kế dữ liệu và giao thức — tuần 1

- Chốt quan hệ parent→children→devices, sessions/tokens, policy/version, event 7 trường, audit, request/command/consent và bảng metadata idempotency.
- Định nghĩa payload enrollment/heartbeat/policy/event batch/WebSocket, auth và error; thời hạn, ACK, retry/backoff, command ID chống lặp, ordering và giới hạn batch.
- Thiết kế ledger ngân sách theo trẻ/ngày/thiết bị và giao dịch trả/cấp lại có ACK; tổng đã dùng + quyền dùng còn lại không vượt ngân sách đã được parent cấp. Không thu hồi phần máy offline còn có thể dùng chỉ bằng việc máy khác đang online. Đặc tả ngoại lệ lịch 15 phút và các tương tác lệnh đã chốt trước khi code.
- Chốt canonical serialization/HMAC hoặc chữ ký, key lifecycle; chọn trường AES-GCM, cách giữ khóa env/DPAPI và băm device secret phù hợp.
- Tạo migration có version và seed lặp được: demo parent/child/device và bảng ≥200 mục/6 nhóm; tách bộ DNS an toàn 50, giáo dục 20 và vướng mắc phụ lục 60.
- Đầu ra: data dictionary, API contract, migration/seed thật và file dữ liệu có nguồn, tuổi phù hợp và expected outcomes.
- Kiểm chứng: database rỗng migrate/seed thành công, constraints/ownership đúng; extra event field/type bị từ chối; nonce/key không hardcode; dataset đúng count/không miền cấm.
- Yêu cầu: R-F3-01, R-F4-01, R-F5-05, R-D02, R-F2-04/09.

## S3 Backend và bảo mật — tuần 1–2

- Triển khai auth, rate limit IP, khóa tạm 5 lần/15 phút, mật khẩu ≥10; phiên 12 giờ, cookie, logout server-side, CSRF; query ownership parent/child-view/admin.
- Enrollment mã 8 ký tự/10 phút + fingerprint + consent; access 15 phút, refresh, thu hồi device; tránh dùng demo secret trong lab thực.
- Heartbeat 60 giây, GET policy theo version/integrity, event batch idempotent, reports/audit có phân trang; thiết kế endpoint cụ thể từ API contract chứ không đoán rằng sơ đồ đã quy định mọi HTTP method.
- Hàng lệnh bền vững, WebSocket có auth/ACK/chống lặp, fallback nhận lệnh trong heartbeat; tác vụ retention 90 ngày và xóa dữ liệu có trạng thái.
- TLS ≥1.2, CA lab và hướng dẫn pin; giới hạn request, logging không rò token/URL.
- Đầu ra: backend chạy qua TLS, migration/seed/demo, tài liệu auth/API/retention.
- Kiểm chứng: unit/integration ở VALIDATION_PLAN, ownership giữa 2 gia đình, CSRF, token hết hạn/thu hồi, logout, 5 lần sai, policy giả, event retry, deletion/retention.
- Yêu cầu: R-A04, R-P01/02/03, R-F3/4/5 liên quan.

## S5 Agent nền tảng, tray và offline — tuần 2

- Xây service LocalSystem và tray phiên user, IPC có auth/ACL; không thao tác UI trực tiếp từ Session 0.
- Lifecycle có handshake hiển thị icon: dừng khi không thể hiện icon; thử login/logoff/restart/tray crash; SCM recovery không được tạo vòng lặp cưỡng bức chạy vô hình.
- ProgramData SQLite ACL; cache policy xác minh integrity; hàng đợi có giới hạn, retry/backoff, idempotency khi reconnect; sau 3 ngày offline vẫn giữ quota/lịch cuối, không tự mở chặn hay reset quota. Chỉ dùng phần ngân sách đã được cấp cho máy, lưu usage và quyền còn lại bền vững qua reboot; trả/cấp lại theo giao thức ACK đã thiết kế.
- TLS pin sai từ chối; token device/refresh/revoke; không ghi bí mật rõ vào log.
- Cài/gỡ service trong lab với script có hướng dẫn hoàn nguyên; chưa thêm chức năng gỡ bằng password nếu chưa chọn phần NC.
- Kiểm chứng: Windows user thường, ACL read/write, IPC giả mạo, mất mạng/server dừng, policy hỏng, pin sai, icon mất và phục hồi.
- Đầu ra: bộ cài/chạy/dừng lab, agent/tray nhìn thấy, đồng bộ thực qua TLS.
- Yêu cầu: R-A02/03/06, R-P04/05, R-F5-03/04/07/09, M5.

## S6 Thời gian và kiểm soát ứng dụng — tuần 2–3

- Counter dùng monotonic; nhận biết lock/unlock và idle >5 phút đúng phiên user; đối chiếu server mỗi heartbeat, ngưỡng lệch và log theo quyết định.
- Quota weekday/weekend **chung theo trẻ trên các thiết bị**, lịch 7×48, biên ngày/múi giờ; không tăng quota khi đổi giờ/restart hoặc do online/offline nhiều máy. Không tự cấp quota đầy đủ cho mỗi máy.
- Máy trạng thái cảnh báo 10/5/1 nhẹ nhàng, thời gian còn lại/lưu bài/xin giờ. Theo D020 tạm: 60 giây lưu bài nằm ở cuối quota; quota 3 phút thì nhắc còn 1 phút và khóa tại phút 3, không cộng thành phút 4. Phải đối chiếu câu trả lời giảng viên trước khi chốt nghiệm thu; ngoài lịch vẫn giữ ngưỡng khóa ≤5 giây.
- Kiểm soát allowlist/blocklist tên + SHA-256, cache hash an toàn khi file thay đổi; kết thúc app thử an toàn và cửa sổ giải thích.
- Kiểm chứng: quota 3 phút, ngoài lịch ≤5 giây, đủ 1 giờ sai số ≤±30 giây, idle/lock, lùi 3 giờ, đổi tên executable, retry lệnh không cộng giờ hai lần.
- Đầu ra: F1/F2-app chạy thực và bằng chứng, phần M6 có dữ liệu.

## S7 DNS proxy và SafeSearch — tuần 3

- Bind 127.0.0.1:53, xác minh UDP/TCP theo thiết kế và upstream không vòng lặp; kiểm tra xung đột cổng, cache, TTL, DNS lỗi và tên miền con/IDN/suffix.
- Tích hợp cấu hình DNS Windows trên lab, xử lý IPv6/phạm vi hỗ trợ; lưu cấu hình gốc để hoàn nguyên khi dừng/gỡ/lỗi. Không thay DNS máy sử dụng hằng ngày ngoài phạm vi lab.
- Lọc policy/default tuổi, chuẩn hóa subject tối thiểu; SafeSearch kiểm nslookup và trình duyệt.
- Chạy bộ an toàn, đo tỷ lệ đúng denominator đã làm rõ, 0 false positive/20 giáo dục. Ghi dữ liệu mong đợi/thực tế và capture Wireshark cho M1.
- Phần NC đã được chọn ưu tiên D018: DoH endpoint/canary/browser policy và chống đổi DNS thủ công; làm sau phần BB, kiểm 8.8.8.8 và rollback trong lab; báo giới hạn trung thực, không hứa DNS proxy chặn mọi VPN/HTTPS.
- Đầu ra: DNS proxy hoạt động thực, script kiểm nhanh, dataset nộp kèm, bằng chứng M1 và F2.

## G-UI Điều kiện chuyển từ backend và mạng sang giao diện

Trước S4, kiểm backend/agent/mạng bằng API/test client và công cụ lab, chưa cần dashboard hoàn chỉnh:

- Backend auth/ownership/CSRF, migration/seed, enrollment, heartbeat, policy integrity, batch/idempotency và command/ACK có kiểm chứng liên quan.
- Service/tray tối thiểu có biểu tượng nhìn thấy, IPC/ACL/cache/offline và phần thời gian/app bắt buộc hoạt động; không hoãn tray đến sau web khiến agent chạy vô hình.
- DNS proxy được Windows thật sự dùng, có lọc exact/subdomain, SafeSearch; bộ test an toàn/kết quả/giới hạn mẫu số chưa được xác nhận được ghi rõ; có bằng chứng gói tin M1 và khả năng restore DNS.
- Đã thử mất mạng/server down và phục hồi; quota chung/phần chia, ngoại lệ D017 không cấp trùng khi retry; không chỉ có endpoint giả hay log “thành công”.
- Các lỗi còn lại/giả định nguồn được ghi trong PROJECT_STATE; không gắn nhãn “xong backend/mạng” cho phần bắt buộc đang hỏng. Nếu chưa qua G-UI, tiếp tục sửa phần nền và cập nhật lịch thay vì chuyển sang trang trí giao diện.

Đây là cổng kiểm chức năng nền, không thay nghiệm thu toàn đồ án. Phép đo dashboard→agent và kiểm UX chỉ hoàn tất sau khi có UI ở S4/S8. Nhánh NC DoH/chống đổi DNS vẫn theo D018: ưu tiên sau khi BB đạt, không tự biến thành điều kiện bắt buộc mới để qua G-UI.

## S4 Dashboard phụ huynh và trẻ — cuối tuần 3 đến tuần 4, sau G-UI

- **D026:** đọc `docs/Design-PH.md` trước khi chọn màu/style parent; dùng làm nguồn định hướng chính cho phụ huynh, ưu tiên hơn gợi ý mint/pastel chung/catalog skill. Thống nhất điểm YAML tối/prose sáng trong nguồn khi ánh xạ token; không tự coi đã chốt theme. Child-view tiếp tục theo hướng trẻ em/Pinterest; giữ KidSafe, không nhập tên/nội dung marketplace của mẫu.
- Đọc UI_DESIGN_BRIEF và ảnh trong `docs/design-references/`; dùng nhánh app screens của design-taste-frontend khi thiết kế thực. Ảnh lớp cho bố cục/luồng, Pinterest cho palette/vibe child-view; parent theo Design-PH.md ở dòng trên. Giữ KidSafe, Jinja2 + HTMX và yêu cầu gốc.
- Đọc DESIGN_SKILL_REVIEW và bản UI UX Pro Max đã tải nếu cần tra màu/chữ/UX/chart; kiểm kết quả đúng chủ đề trước khi dùng, không tự thêm stack/dependency hoặc ghi đè brief. Chỉ dùng ở khâu UI sau G-UI; không tự bắt đầu sinh design system hoặc giao diện do đã tải công cụ.
- Làm theo framework đã chốt; phụ huynh quản lý trẻ/thiết bị, ghép đôi, quota weekday/weekend, lịch 7×48, allowlist/blocklist, phân loại/default 6–11.
- Danh sách yêu cầu thêm giờ, bộ lệnh D017, báo cáo ngày/tuần/top 10/bị chặn, trạng thái device/offline/policy ACK và xóa dữ liệu.
- Màn hình trẻ: thời gian còn lại là trọng tâm, tiến trình đúng số thật, lời nhắc nhẹ nhàng, Xin thêm giờ, hình minh họa phù hợp và audit đúng quyền; phân biệt quota chung với phần máy này dùng được offline.
- Chọn hướng pastel sáng và chữ dễ đọc theo brief, không sao chép chi tiết làm lệch yêu cầu (danh mục thiếu, tạm dừng cả ngày, lệnh sai nghĩa, nhãn thành công khi chưa ACK).
- Kiểm chứng bằng browser desktop/tablet/mobile: CSRF/ownership thực, số liệu đồng nhất, contrast/focus/tiếng Việt, pending/offline/error/0 và xóa chờ ACK; chụp, xem, sửa lỗi ở các cỡ màn hình.
- Đầu ra: luồng web nối backend thật, ảnh kiểm chứng và hướng dẫn demo; chỉ gọi UI đạt khi thao tác và trạng thái phản ánh đúng agent.
- Yêu cầu: R-A05, R-F3-02/03/04, R-F4-04 và D022–D024.

## S8 Tích hợp đầu cuối — tuần 4

- Parent đổi policy → agent áp dụng → có ACK/audit → báo cáo phản ánh đúng; đo end-to-end ≤60 giây.
- WebSocket khóa/mở/cộng 15 → tác động thật <5 giây, có auth/expiry/ACK và chống lặp; fallback heartbeat không được gọi là đạt ngưỡng lệnh khẩn nếu chậm hơn.
- Áp D017: Mở khóa cho tối đa 15 phút dù ngoài lịch/quota hết, có audit và ghi giờ ngoại lệ; hết hạn quay về lịch/quota. Cộng 15 chỉ tăng quota chung; Khóa ngay hủy ngoại lệ; app/domain rules vẫn giữ. Kiểm retry/reconnect/reboot không kéo dài ngoại lệ, lệnh cũ đến muộn không hồi sinh grant bị hủy; nhiều máy không nhân giờ ngoại lệ. Hai máy offline hoặc đổi phần chia lúc mất ACK/crash không làm tăng tổng ngân sách.
- Trẻ xin giờ → parent duyệt → counter cập nhật → trẻ xem audit đúng phạm vi.
- Xóa con: server và mọi agent/cache; offline có trạng thái pending, tombstone/generation hoặc cơ chế tương đương để dữ liệu cũ không quay lại. Thử retention 90 ngày bằng đồng hồ kiểm thử độc lập với quota production.
- Kiểm chứng reports không double-count khi retry/reconnect, dữ liệu parent và child nhất quán.
- Đầu ra: các luồng hoàn chỉnh có evidence; không thay bằng mock trong nghiệm thu sản phẩm.

## S9 Kiểm thử, bảo mật và khả năng chịu lỗi — tuần 4

- Hoàn thành ít nhất 15 unit + 5 integration; kiểm tra kỳ vọng, đầu vào sai và biên; giữ output/ảnh thật.
- Thử 9 đường vòng đề liệt kê trong lab, ít nhất 7 được ghi đầy đủ; không tự sửa các máy/dịch vụ ngoài phạm vi lab.
- Mất mạng, server dừng, kill agent: hành vi dự kiến/thực tế/thời gian hồi phục; thử Service Recovery và mất icon cùng nhau.
- Rà STRIDE và checklist ASVS theo phiên bản/điều khoản được chọn lúc làm; đánh dấu đạt/chưa đạt/không áp dụng kèm evidence. Không tự nhận chứng nhận ASVS.
- Sửa lỗi bắt buộc trước khi thêm điểm thưởng; chạy lại kiểm tra có liên quan khi sửa.
- Đầu ra: test/evidence index, threat model và privacy cập nhật đúng sản phẩm.

## S10 Phép đo và phụ lục kỹ thuật mạng — tuần 4–5

- M1 capture, M2 bảng so sánh, M3 kết quả thử thật, M4 raw sample/biểu đồ, M5 phục hồi, M6 clock/threshold.
- M4: ≥30 mẫu cho từng điều kiện CPU/RAM idle/peak, DNS có/không agent, policy latency; ghi OS/CPU/RAM/version/load/cách tính p50/p95 và thời điểm đo.
- Không suy ra M1/M2/M3/M5/M6 chỉ từ một benchmark.py. Không điền số giả khi máy không hỗ trợ thử.
- Đầu ra: phụ lục có đủ 6 mục, file thô và bằng chứng có đường dẫn, giới hạn rõ.

## S11 Hồ sơ nộp, video và hướng dẫn — tuần 5

- Viết BaoCao.docx 20–30 trang theo REPORT_PLAN, phân công và tự đánh giá % có xác nhận thành viên; xuất BaoCaoKyThuatMang.pdf.
- Render và kiểm tra từng trang Word/PDF; bảng/ảnh không cắt chữ, số đo khớp raw samples; thay phần dự kiến bằng kết quả thật.
- AI_USAGE: từng phần, công cụ, kiểm chứng; không tự điền đóng góp hay hiểu biết của sinh viên.
- Video.mp4 5–7 phút, tiếng Việt; quay luồng đủ trọng tâm và không lộ bí mật/dữ liệu thật.
- README từ Windows sạch: dependency/CA/config, migration/seed/demo, cài service/tray, chạy web, dùng thử, dừng/gỡ/restore DNS; đo tổng ≤15 phút, sửa quy trình nếu vượt.
- Đầu ra: đủ đường dẫn R-D01–R-D09, ảnh kết quả test, dataset và báo cáo; không đóng gói venv/khóa riêng/runtime database.

## S12 Kiểm tra cuối và tập vấn đáp — tuần 5

- Đi từng ID BB: nối file thực + test + evidence, không có ô đạt trống chứng cứ. Các NC/CTT ghi đúng mức hoàn thành/giới hạn.
- Thử lại cài từ gói nộp trên máy sạch; kiểm tài khoản demo, video duration, số trang báo cáo và việc mở mọi file.
- Mỗi thành viên giải thích phần mình, protocol, lựa chọn DNS, threat model, fail-open/closed và các đường vòng chấp nhận rủi ro.
- Báo người dùng kết quả, lỗi chưa đạt và rủi ro thực; chỉ gọi “sẵn sàng nộp” khi phần bắt buộc đủ hoặc đã có cách xử lý được xác nhận.

## Sổ tiến độ để dùng về sau

| Bước | Trạng thái hiện tại | Đầu ra/bằng chứng thực tế |
| --- | --- | --- |
| S0 | Hồ sơ chuẩn bị bản 1 có bổ sung tham khảo UI, chờ người dùng rà soát | D001–D024; sáu ảnh và brief UI, G-UI/thứ tự mới; câu hỏi giảng viên/ân hạn tạm/phân công để trống; chưa có lệnh bắt đầu |
| S1–S12 | Chưa bắt đầu | Chưa có |

Khi làm, tách dòng theo từng S và ghi ngày, file thay đổi, lệnh kiểm chứng, kết quả, ID còn thiếu và bước tiếp theo. Không đánh dấu xong cả bước chỉ vì có thư mục hoặc tài liệu khung.
