# Kiến trúc nháp để thảo luận

Trạng thái: **đề xuất chuẩn bị, chưa triển khai**. Tên KidSafe và dashboard Jinja2 + HTMX đã được người dùng chọn; nhóm 3 người còn 5 tuần, lab Windows 11/admin. Stack và thành phần bắt buộc theo REQUIREMENTS; các lựa chọn còn mở dưới đây phải được cập nhật khi có trả lời. Không có quyền tự cài service hoặc đổi DNS từ tài liệu này.

Thứ tự mới D024: hoàn thiện backend/agent/mạng bắt buộc trước, qua G-UI trong IMPLEMENTATION_PLAN rồi mới thiết kế dashboard. Tray tối thiểu vẫn có từ S5. Định hướng bố cục/màu sắc từ sáu ảnh do người dùng cung cấp được lưu trong [UI_DESIGN_BRIEF](UI_DESIGN_BRIEF.md); không thay đổi stack/API/quyền hoặc bộ lệnh D017.

Đã chốt tiếp: server LAN trên máy riêng; sau 3 ngày offline vẫn áp quota/lịch cuối (fail-closed); quota dùng chung theo trẻ giữa thiết bị, chia ngân sách offline trước và điều chỉnh khi có mạng; cảnh báo nhẹ nhàng với thời gian còn lại, lưu bài và xin thêm giờ. Mở khóa ngoài lịch tạo ngoại lệ 15 phút có audit rồi quay về lịch/quota.

## Thành phần

```text
Máy Windows của trẻ (user thường)           Server LAN trên máy riêng
  Tray UI nhìn thấy được                    Dashboard parent / child-view
       | IPC xác thực + quyền cục bộ             | HTTPS + session + CSRF
  Service LocalSystem <--- TLS 1.2+ ------> FastAPI
   - Policy/version/integrity   heartbeat 60s     - Auth/enrollment/token
   - Counter monotonic          batch events     - Policy/command/audit/reports
   - App name + SHA-256          WebSocket       - Retention/deletion
   - DNS 127.0.0.1:53                             |
   - SQLite cache/queue + ACL                SQLite WAL + SQLAlchemy
```

Service và tray là hai tiến trình có trách nhiệm khác nhau. Không đưa cửa sổ trẻ vào Session 0 của LocalSystem. Tray nhìn thấy được là điều kiện vận hành, không phải tính năng trang trí có thể tắt.

## Ranh giới tin cậy

- Trình duyệt/đầu vào client không đáng tin; backend kiểm schema, auth, CSRF và ownership ở truy vấn.
- Windows user thường không được ghi policy/config/database của service. IPC phải ngăn giả tray, đọc token hoặc ra lệnh đặc quyền trái phép.
- Mạng có thể gián đoạn/giả mạo: TLS pinning và token ràng device; policy toàn vẹn và version; không chấp nhận policy hỏng để “giữ chạy”.
- Local admin/boot USB/VPN không thể bị DNS proxy đơn thuần kiểm soát tuyệt đối; ghi phạm vi và kết quả thực trong M3.

## Luồng giao thức dự kiến

1. Parent đăng nhập và tạo mã ghép 8 ký tự/10 phút. Agent gửi mã + fingerprint tối thiểu qua TLS. Server ghi consent, trả device_id/access 15 phút/refresh. Mã dùng lại/hết hạn phải bị từ chối; một lần dùng là đề xuất bảo vệ cần ghi trong contract.
2. Agent heartbeat mỗi 60 giây: trạng thái, quota dùng, policy_version; server trả version hiện tại và pending commands. Khác version thì GET policy, xác minh integrity trước khi lưu/áp.
3. Event đúng 7 trường được gửi theo batch; idempotency key nằm ngoài schema event. Server kiểm device/child ownership; retry batch không tăng thống kê lần hai.
4. Lệnh qua WebSocket: ID lệnh, thiết bị đích, thời hạn và ACK là metadata giao thức dự kiến; mỗi lệnh chỉ có tác dụng một lần. Đo đến khi khóa/mở/cộng thực, không chỉ khi server nhận request.
5. Offline dùng policy cache đã xác minh và counter liên tục. Đã chọn N=3 ngày, sau ngưỡng vẫn giữ quota/lịch cuối (fail-closed), không tự mở chặn. Không phải khóa vô điều kiện nếu lịch còn cho phép và ngân sách còn. Đề xuất đo ngưỡng bằng 72 giờ từ lần liên lạc xác thực cuối; persistence qua reboot và chống sửa giờ cần thiết kế/kiểm chứng. Queue có giới hạn, không âm thầm xóa tùy ý: quy tắc dung lượng/loss phải được thiết kế và thông báo.
6. Khi online, đồng bộ có thứ tự và xử lý deletion trước dữ liệu cũ. Không để event bị xóa được upload lại sau reconnect.

## Dữ liệu dự kiến

Event giữ nguyên R-F3-01. Account, child, device, consent, policy/version, session, token verifier, pending command, request, audit và idempotency/deletion metadata là các bảng có chức năng riêng. Mỗi trường bổ sung phải có mục đích trong privacy; không dùng metadata làm nơi giấu dữ liệu theo dõi.

Policy cần mô tả quota weekday/weekend, lịch 7×48, timezone, tuổi/default, app/domain rules, precedence, version và integrity. Người dùng đã chốt quota chung theo trẻ giữa các thiết bị (ví dụ tổng 90 phút, không phải mỗi máy 90 phút) và chia ngân sách offline trước. Phải chống race và cấp trùng cả khi offline; không giả định đồng bộ hoàn hảo khi mất mạng.

### Thiết kế dự kiến cho ngân sách đã chọn

- Sổ ngân sách theo trẻ/ngày/thiết bị, có phần đã dùng và phần đã cấp nhưng còn có thể dùng. Tổng đã dùng + tổng phần còn được quyền dùng không vượt quota ngày + khoản tăng giờ được phụ huynh cấp rõ ràng.
- Ví dụ quota 90 phút chia máy A 60, B 30. Nếu A đang offline và vẫn giữ quyền dùng 60, không được cấp thêm 60 ấy cho B chỉ vì server chưa thấy A dùng.
- Chuyển phần chưa dùng: máy cho đi phải lưu việc giảm quyền dùng và ACK trước khi server cấp phần đã trả cho máy nhận; ID giao dịch/chống lặp và transaction DB ngăn crash/retry cấp hai lần. Chỉ máy nhận online là chưa đủ để thu hồi quyền của máy đang offline.
- Phần chưa trả của máy offline tiếp tục được giữ chỗ. Đánh đổi: giờ còn ở máy mất liên lạc có thể tạm chưa chuyển được sang máy khác; giao diện phải giải thích trạng thái chờ.
- Mỗi ngân sách ràng device, ngày, version và integrity; qua ngày dùng phần phân bổ của ngày mới trong policy cache đã xác minh, không cấp lại toàn quota cho từng máy. Chi tiết persistence/reboot/chống sửa giờ cần được đặc tả ở S2/S5/S6.
- Metadata ngân sách/giao dịch có lược đồ riêng và phải vào bảng privacy; không thêm trường vào event bảy trường. Đây là thiết kế đề xuất để đạt D015, chưa có cơ chế nào được triển khai hoặc thử.

### Ngoại lệ mở khóa đã chọn

Người dùng đã duyệt bộ quy tắc D017:

| Lệnh | Tác dụng đã chốt | Ràng buộc |
| --- | --- | --- |
| Cộng 15 phút | Tăng quota chung của trẻ 15 phút | Không bỏ lịch; chỉ cộng một lần cho mỗi ID lệnh, không cộng riêng 15 phút/máy |
| Mở khóa | Ngoại lệ tối đa 15 phút dù ngoài lịch hoặc quota cạn | Ghi giờ ngoại lệ và audit; hết hạn đánh giá lại lịch/quota; không gia hạn khi retry/reconnect/reboot |
| Khóa ngay | Khóa và hủy ngoại lệ đang chạy | Lệnh cũ đến muộn không được làm sống lại ngoại lệ đã hủy; ordering/version phải được đặc tả |

Mọi lệnh vẫn giữ allow/block app và domain. Audit có actor/time/IP/old/new đã lọc bí mật và trẻ xem đúng phạm vi. Thiết kế dự kiến: tách ngân sách quota gốc, grant cộng giờ và grant ngoại lệ; phần ngoại lệ có thiết bị đích/cửa sổ thời gian/quyền dùng hữu hạn, không phát lại toàn phần giờ cho mọi máy. Usage vẫn được ghi đúng event schema; báo cáo phân biệt phần ngoại lệ mà không cộng thời lượng hai lần. Chi tiết cách trừ quota còn lại khi đang ngoại lệ phải nhất quán trong S2/S6; không mặc định một lần dùng bị trừ hai quỹ.

### Ưu tiên phần nên có

Đã chọn DoH và chống đổi DNS thủ công sau khi BB đạt. Đặc tả/kiểm thử endpoint DoH, NXDOMAIN canary, chính sách trình duyệt lab, thử 8.8.8.8 và rollback phải dựa trên môi trường thực khi làm. Đây vẫn là NC; M3 là BB và phải báo kết quả/giới hạn dù một biện pháp NC chưa hoàn thành. Không mở rộng thành cam kết chặn mọi VPN/DoT/boot USB.

### Timeline ân hạn tạm để xin xác nhận

Theo D020, 60 giây lưu bài nằm trong quota. Ví dụ quota 3 phút: t=0 bắt đầu, t=2 phút cảnh báo còn 1 phút và nhắc lưu bài, t=3 phút khóa. Không cộng thêm 60 giây sau quota. Các mốc 10/5 phút chỉ xuất hiện khi quota/phiên còn đủ dài; phải đặc tả hành vi khi quota ngắn để không tạo cảnh báo sai. Đây là phương án chuẩn bị được người dùng chọn, chưa được giảng viên xác nhận; không thay yêu cầu khóa ngoài lịch trong 5 giây.

## Bảo mật dự kiến

- Chọn Argon2id hoặc scrypt, chưa khóa lựa chọn. Session parent khác device token; parent session 12 giờ, access device 15 phút; logout/revoke thật ở server.
- HMAC policy hoặc chữ ký theo đề. Chốt serialization, chống replay/version rollback và nơi giữ khóa. Nếu dùng HMAC: phân biệt khóa ký policy (cần bảo vệ bằng env/DPAPI hoặc mã hóa) với token/bí mật xác thực cần lưu dạng băm. Không thiết kế “chỉ lưu hash rồi dùng lại secret đã mất để tính HMAC”.
- AES-GCM cho trường nhạy cảm: chọn phạm vi cụ thể trước code, nonce không tái sử dụng theo khóa, quản lý key/version/env/DPAPI và backup; không tự nhận đã có mã hóa toàn bộ SQLite.
- Audit chứa actor/time/IP/old/new đúng đề, nhưng loại bỏ password/token/key khỏi old/new. Trẻ xem audit liên quan đến mình; không phải log công khai trên Internet.

## Vận hành DNS dự kiến

DNS proxy phải là resolver mà Windows thực sự dùng; chỉ bind port không chứng minh trình duyệt đi qua proxy. Kiểm tra port 53, upstream cố định tránh loop, UDP/TCP, IPv4/IPv6, cache, TTL, response/error, cấu hình adapter và hoàn nguyên. Các thay đổi có quyền admin thực hiện trong lab khi sang triển khai.

Tên miền rule có thể đầy đủ để lọc subdomain nhưng event subject chỉ là miền tối thiểu theo định nghĩa đã chốt. Chặn `example.com` cần khớp chính xác hoặc hậu tố `.example.com`, không chặn nhầm `notexample.com`. DoH/DoT/VPN/IP trực tiếp là giới hạn phải thử, không khẳng định proxy tự xử lý hết.

## Những quyết định còn mở

Chi tiết hình thức cảnh báo; IPC named pipe hay localhost token; timezone/đổi ngày/idle retrospective; tỷ lệ chia offline mặc định; cách hạch toán quota/ngoại lệ và ordering kỹ thuật; chống replay/rollback; ý nghĩa icon lúc logoff; khái niệm miền cấp hai và việc xóa offline. Các lựa chọn kỹ thuật này được đề xuất có lý do trước bước liên quan. D020 đã chọn timeline ân hạn tạm trong quota; xác nhận của giảng viên vẫn chờ trong QUESTIONS_FOR_INSTRUCTOR. Phân công để trống theo D021.
