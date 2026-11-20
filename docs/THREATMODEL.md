# Mô hình mối đe dọa và checklist kiểm chứng

Trạng thái 2026-11-04: đã có mã parent/child-view, server và agent. Bộ backend/HTML/đóng gói đã có 45 test đạt trên Windows 11/Python 3.12; các đợt bổ sung ghi ở bằng chứng dự án. **Chưa xác nhận đạt ASVS, chưa nghiệm thu user thường/Windows 10 hoặc hoàn tất số đo mạng.** Phạm vi gồm web, server, LAN, service/tray/IPC và cache.

Đã kiểm bằng test: scrypt, 5 lần sai/15 phút, cookie/CSRF/logout, ownership và child-view chỉ đọc, enroll một lần, refresh rotation/binding, Ed25519 tamper, AES-GCM nonce/tag, schema bảy trường/chín type và miền tối thiểu, retry không đếm trùng nhưng giữ event trùng nội dung hợp lệ, lệnh/sequence, một quỹ ngoại lệ theo trẻ, khóa phải ACK trước cấp ngoại lệ máy khác, ngân sách không thu hồi quyền offline, trả/chuyển có ACK hiệu lực ngày sau, xóa/ACK retry và refresh cleanup máy offline dài ngày. HTML cả tám view được thử auth/IDOR/escape. Source ZIP được thử loại secrets/runtime và xác minh manifest. Xem `server/README.md`, `API_CONTRACT.md`, `tests/server/`.

AES-GCM thực áp dụng tên trẻ/tên máy, audit IP/old/new và consent IP; không tuyên bố mã hóa cả DB. Credential device/session chỉ lưu verifier; agent giữ credentials DPAPI. Hash refresh hết hạn được giữ chỉ cho cleanup đến ACK để còn xóa máy offline lâu ngày; không cấp lại quyền thường. Security audit lệch giờ ở agent chỉ có drift/mốc thời gian, retention 90 ngày; không thêm activity type thứ mười. ACL/tray/SCM, kill/reboot, DNS thật, bypass và độ trễ cần test lab riêng; test API không chứng minh những mục này.

## Tài sản và giả định

Tài sản: thời gian/quota chính xác, policy nguyên vẹn, dữ liệu trẻ, phiên parent, token/khóa, quyền đồng ý/xóa/xem, khả năng nhìn thấy agent và phục hồi cấu hình mạng. Giả định đề: trẻ dùng Windows user thường; local admin, Safe Mode và boot USB là đường vòng phải phân tích, không giả định phần mềm bất khả xâm phạm.

## Bảng STRIDE

| ID | Nhóm | Kịch bản | Biện pháp trong mã/thiết kế | Kiểm chứng và phần còn cần có |
| --- | --- | --- | --- | --- |
| T01 | S Giả mạo | Máy khác gửi event bằng device_id đoán được | Token ràng device/child, kiểm ownership, TLS | Sai device/token bị từ chối; không ghi event |
| T02 | T Sửa đổi | Trẻ sửa cache policy hoặc replay version cũ | ACL + Ed25519, version và chống rollback | Tamper có test; ACL/user thường và recovery cần lab |
| T03 | R Chối bỏ | Parent phủ nhận đã khóa/đổi lịch | Audit actor/time/IP/old/new, giao dịch cùng thay đổi | Parent và trẻ xem đúng bản ghi, không lộ secret |
| T04 | I Lộ dữ liệu | Đánh cắp DB hoặc nghe lén kết nối | TLS/pinning; AES-GCM trường nhạy cảm, key tách dữ liệu; hash secret | Sai pin thất bại; ciphertext/tag/nonce và ACL được kiểm |
| T05 | D Từ chối dịch vụ | Spam batch hoặc queue offline đầy | Rate limit/batch cap/queue cap/backoff và quy tắc overflow đã chốt | Tải bất thường không làm sập; loss nếu có được ghi rõ |
| T06 | E Nâng quyền | User thường ghi config/ra lệnh LocalSystem qua IPC | ACL ProgramData/pipe hoặc localhost token; validate command | User không ghi được; client IPC giả bị từ chối |
| T07 | T Trẻ là người tấn công | Lùi đồng hồ 3 giờ để tăng quota | Monotonic + đối chiếu server heartbeat + log | Quota không tăng, log đúng loại; M6 |
| T08 | I/E Lạm dụng stalkerware | Người lớn cài bí mật để theo dõi người lớn khác | Không chế độ ẩn, consent enrollment, tray hiện, mất khả năng hiện thì tự dừng; phạm vi hợp pháp trong tài liệu | Cài/chạy không có tray không thể âm thầm thu; không cờ ẩn |
| T09 | E/I IDOR | Parent A đổi child_id để xem/sửa trẻ của B | Ownership ngay trong truy vấn và mọi reports/audit/command/delete | Cross-family tests cho đọc/ghi/xóa/WebSocket |
| T10 | S/T Web giả | CSRF thay lịch, đánh cắp/giữ phiên sau logout | CSRF mọi ghi, cookie an toàn, session 12h/revoke; escape nội dung UI | POST thiếu CSRF bị từ chối; logout hủy; chuỗi HTML không chạy |
| T11 | T Replay lệnh | Gửi lại “cộng 15 phút” nhiều lần hoặc event retry | Command ID/expiry/ACK và idempotency bền vững | Chỉ cộng/đếm một lần khi retry/crash/reconnect |
| T12 | I/R Xóa không hết | Agent offline upload dữ liệu cũ sau khi xóa | Deletion marker/generation, ưu tiên lệnh xóa, ACK, trạng thái pending | Reconnect không làm dữ liệu con xuất hiện lại |
| T13 | S/I Ghép trái phép | Đoán mã ghép hoặc reuse mã đã dùng | Mã 8 ký tự/10 phút, rate limit IP, một lần dùng bằng giao dịch SQLite | Reuse/binding có test; độ bền vận hành/rate tải thật cần lab |
| T14 | D/T Né DNS | Đổi DNS, DoH/DoT, VPN, IP trực tiếp | Ghi giới hạn; biện pháp NC chọn theo lab; M3 thử thực tế | Không khẳng định chặn tuyệt đối; ghi từng đường vòng |
| T15 | D Vòng đời | Kill service/tray; SCM restart tạo vòng chạy không icon | Recovery phối hợp handshake tray, trạng thái dừng an toàn và restore DNS | Kill/boot/logoff thử thật, đo phục hồi, không chạy ẩn |
| T16 | T Gian lận quota nhiều máy | Hai máy offline cùng dùng toàn bộ quota của một trẻ, hoặc reconnect làm reset/cấp trùng ngân sách | Chia recurring allocation; giảm donor lưu bền vững rồi ACK, recipient chỉ tăng sau ACK; hiệu lực ngày sau, giữ phần ngày hiện tại. Revoke/offline không tự thu hồi quyền | Có test API tổng phần chia/ACK trùng/transfer chồng/không cấp lại hôm nay; hai máy Windows offline/reboot/crash cần đo thật |
| T17 | T Replay ngoại lệ lịch | Gửi lại Mở khóa để kéo dài vô hạn ngoại lệ 15 phút hoặc hồi sinh grant đã bị Khóa ngay hủy | Command ID/thời hạn/ordering bền vững, không tạo hạn mới khi replay; D017 giữ app/domain rules và audit | Retry/reboot/reconnect không gia hạn; quota cạn vẫn chỉ tối đa 15 phút; lệnh cũ không hủy hiệu lực Khóa ngay; nhiều máy không nhân grant |

## Checklist rà soát theo hướng ASVS

Đây là checklist nội bộ theo các chủ đề ASVS, chưa gắn số điều khoản hay phiên bản. Khi triển khai S9, tra nguồn OWASP chính thức, chọn phiên bản/phạm vi, bổ sung mapping chính xác và dẫn nguồn; không tự ghi đã tuân thủ tiêu chuẩn.

- [ ] Chọn phiên bản ASVS và phạm vi; mỗi mục có ID điều khoản, evidence, kết quả và lý do N/A nếu có.
- [ ] Password hash phù hợp; length ≥10; lockout 5/15 phút và rate limit IP có test.
- [ ] Session cookie đủ cờ, expiry 12 giờ và server-side revoke khi logout.
- [ ] CSRF cho mọi thao tác ghi; WebSocket auth/origin phù hợp thiết kế.
- [ ] Ownership ở query cho parent/child-view/admin, cả reports/audit/delete/command.
- [ ] Validate schema 7 trường/9 type, giới hạn input/batch, escape HTML và query parameterized.
- [ ] TLS ≥1.2 và pinning; key/secret không hardcode/không vào log hay gói nộp.
- [ ] AES-GCM đúng nonce/tag/key lifecycle, token/device secret lưu verifier phù hợp.
- [ ] Policy integrity/version; command replay/idempotency và token revoke có test.
- [ ] Audit actor/time/IP/old/new nhưng không lộ password/token; trẻ xem đúng phạm vi.
- [ ] Retention 90 ngày, xóa server/agent và chống tái nhập dữ liệu đã xóa.
- [ ] ACL/IPC/user thường, service recovery, tray bắt buộc, không cờ chạy ẩn.
- [ ] Dependency/version/config/migration/demo tách bí mật thật; hướng dẫn cài/gỡ/restore DNS được thử.

Mẫu evidence: `ID → file/chức năng → lệnh/kịch bản → ngày/môi trường → kết quả → ảnh/log → giới hạn`. Trước nộp, chuyển từng biện pháp từ “dự kiến” sang kết quả đã chứng minh hoặc lỗi chưa đạt.
