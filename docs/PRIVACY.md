# Quyền riêng tư và minh bạch dữ liệu KidSafe

## D050 — Giao diện trong app Windows

Service lưu snapshot `child_view` trong SQLite có ACL chỉ SYSTEM/Administrators: tên trẻ, ngày, top10 app/miền, tối đa10 câu audit thân thiện và trạng thái lời xin. Chỉ trả cho PID tray đã xác thực. Bearer/refresh vẫn ở kho service qua DPAPI, không chuyển vào cửa sổ UI. Hoạt động cũ/audit hết90 ngày được dọn cả khi offline, và lệnh xóa trẻ xóa cache này. Tên hồ sơ giữ để nhận diện thiết bị đến khi gỡ/xóa. Metadata `time_request` giữ trạng thái gửi bền vững; sự kiện xin thêm giờ vẫn đúng bảy trường, không ghi loại sự kiện mới. Cửa sổ chỉ đọc dữ liệu, không thu chat/phím/ảnh/URL đầy đủ.

Trong D040, với sự kiện `unlock_request`, `duration_sec` ghi số giây trẻ xin thêm. Số này phục vụ việc hiển thị và duyệt yêu cầu. Thời gian thực tế vẫn đọc từ bộ đếm sử dụng. Sự kiện tiếp tục dùng bảy trường và chín loại đã có.

## D036 — Danh sách và số giây theo nhóm

Phụ huynh chọn tệp để trình duyệt tính SHA-256 tại chỗ. Policy lưu tên tệp, mã băm, chế độ, lịch và lời nhắn. Tệp và đường dẫn trên máy phụ huynh không được gửi lên server. Heartbeat thêm tổng giây theo nhóm và ngày, giữ cùng dữ liệu usage trong 90 ngày, chỉ chia sẻ tổng đã báo với agent của cùng hồ sơ. Dữ liệu nhóm được xóa cùng cache và usage. Sự kiện giữ bảy trường và chín loại.

## D035 — Áp dụng quỹ giải trí

Heartbeat trả tổng số giây đã báo của các máy khác cùng hồ sơ và ngày, không trả danh sách máy hoặc hoạt động. Agent giữ ảnh chụp tổng gần nhất theo ngày để áp dụng khi mất mạng. Lệnh xóa dọn dữ liệu này cùng cache. Sự kiện đóng ứng dụng dùng `blocked_app` hiện có.

## Bổ sung D034 — nhóm giải trí

Phụ huynh chọn tên tệp ứng dụng `.exe` trong policy và hạn mức giải trí ngày. Agent chỉ cộng thời lượng foreground đang hoạt động của các tên đã chọn; không thu cửa sổ, đường dẫn tệp, phím bấm hoặc nội dung. Đây là nhóm theo tên do phụ huynh khai báo, không thay cơ chế SHA-256 của danh sách cho/chặn.

Counter tổng theo ngày lưu trong `state.entertainment_usage` của cache, giữ tối đa90 ngày và bị chặn ghi sau deletion_generation. Heartbeat thêm `entertainment_used_sec` (metadata counter, không thêm trường vào event). Server giữ aggregate `devices.usage[ngày].entertainment_sec` trong90 ngày như counter thường; khi xóa trẻ, usage được xóa cùng dữ liệu khác. Parent/child-view chỉ đọc đúng trẻ của mình; policy/audit giữ quyền và mã hóa đã có. Không suy thời lượng từ DNS.

Policy cũ được bổ sung cấu hình có version mới và audit hệ thống, không giả rằng người dùng đã chọn60phút. Các agent cũ chưa báo counter được UI ghi rõ đang chờ dữ liệu; không thay bằng số dùng giả.

Cập nhật 2026-11-04: có mã server, dashboard và agent. Bộ backend/HTML/đóng gói đã chạy **45 test đạt** trên Windows 11/Python 3.12; xem `server/README.md` và `API_CONTRACT.md`. Đây là test phần mềm/lab cục bộ, **chưa phải nghiệm thu máy trẻ user thường, Windows 10, số đo mạng hoặc chứng nhận pháp lý**. Thao tác Windows đặc quyền vẫn cần bằng chứng riêng.

## Phạm vi

KidSafe quản lý thiết bị trẻ với sự đồng ý của cha mẹ tại bước ghép máy. Server nằm trên máy riêng trong LAN. Agent được thiết kế có tray nhìn thấy được và dừng khi không xác nhận được tray; không có chế độ ẩn. Không dùng để theo dõi bí mật người lớn hoặc máy không được phép quản lý.

Không thu nội dung chat, ảnh màn hình, âm thanh, nội dung phím bấm, URL đầy đủ hoặc tiêu đề cửa sổ. Idle chỉ dùng thời điểm tương tác cuối, không ghi ký tự. DNS không đọc nội dung HTTPS.

## Bảy trường sự kiện

| Trường | Mục đích | Thời hạn | Ai xem |
| --- | --- | --- | --- |
| ts | Thời điểm, thống kê ngày/tuần | 90 ngày theo timestamp | Parent/child-view đúng trẻ; admin |
| device_id | Gắn đúng thiết bị | 90 ngày trong event | Như trên |
| child_id | Gắn đúng trẻ, ownership | 90 ngày trong event | Như trên |
| type | Loại hoạt động/chặn/cảnh báo/yêu cầu | 90 ngày | Như trên |
| subject | Tên executable hoặc miền đăng ký tối thiểu; sự kiện hệ thống dùng nhãn ngắn theo mục đích | 90 ngày | Như trên |
| duration_sec | Thời lượng ứng dụng, không cộng lại vào tổng từ heartbeat | 90 ngày | Như trên |
| policy_id | Giải thích phiên bản policy của chính trẻ | 90 ngày | Như trên |

Chỉ có `app_start`, `app_stop`, `domain_query`, `blocked_app`, `blocked_domain`, `quota_warning`, `locked`, `unlock_request`, `override_granted`. API từ chối trường thứ tám, type khác, URL/path và domain subject còn subdomain. Miền dùng PSL đóng gói của tldextract, không tra Internet để chuẩn hóa; xử lý hậu tố nhiều phần như `edu.vn`. Event server có bảy cột, SQLite rowid nội bộ giữ được hai event giống nội dung. Idempotency ở bảng lô riêng.

## Dữ liệu chức năng thật

D049 bổ sung `accounts.display_name_enc`: tên phụ huynh dùng để hiển thị tên tài khoản, mã hóa AES-GCM; API chỉ trả tên cho chính chủ tài khoản. Giữ cùng vòng đời tài khoản, không áp retention sự kiện 90 ngày. Người vận hành máy chủ giữ trách nhiệm với bản sao lưu. Đăng ký không tự tạo hồ sơ trẻ hoặc cấp quyền quản trị; mật khẩu chỉ lưu scrypt, không ghi vào audit.

| Bảng/trường | Mục đích/bảo vệ | Thời hạn | Ai tiếp cận |
| --- | --- | --- | --- |
| accounts: id, username, password, role, child_id, failures, locked_until | Đăng nhập/ownership/khóa sai 5 lần trong 15 phút; password là scrypt salt riêng | Đến xóa tài khoản; child-view bị xóa khi xóa trẻ | Auth; account xem tên/vai trò; parent tạo account con; admin |
| children: id, parent_id, name_enc, policy, version, deleted | Hồ sơ, policy hiện tại, dấu xóa; tên AES-GCM; không thu ngày sinh | Đến xóa. Sau xóa chỉ ID/liên kết parent/dấu xóa phục vụ ACK và chống nhập lại | Parent/child-view đúng trẻ, admin; agent nhận policy riêng |
| sessions: token_hash, account_id, csrf_hash, expires | Phiên và CSRF, chỉ lưu SHA-256 verifier | 12 giờ; logout xóa; tác vụ dọn hết hạn | Auth, không hiển thị bí mật |
| enrollments: code_hash, child_id, expires, consent_at, consent_ip | Mã 8 ký tự một lần/10 phút, đồng ý cha mẹ; IP AES-GCM | Dùng xong xóa, hết hạn tác vụ dọn; audit consent tối đa 90 ngày | Parent thấy mã tạm; auth kiểm verifier |
| devices: id, child_id, fingerprint_hash, name_enc, revoked, deleted_ack | Ghép, thu hồi, trạng thái xóa; fingerprint SHA-256, tên AES-GCM | Đến gỡ/xóa; fingerprint thay tombstone không chứa fingerprint sau ACK. ID/dấu xóa tối thiểu còn để chống nhập lại | Parent/child-view đúng trẻ thấy tên/trạng thái, không thấy verifier; admin/auth |
| devices: weekday_sec, weekend_sec, allocation_effective_date, previous_weekday_sec, previous_weekend_sec, sequence | Quyền offline đã chia, thứ tự lệnh, tránh cấp trùng | Trạng thái hiệu lực qua reboot; sau ACK gỡ máy vẫn giữ phần ngày hiện tại để không cấp lại giờ đã dùng; ngày sau về 0 | Parent/child-view đúng trẻ, agent của máy |
| devices: last_seen, reported_policy_version, status, usage | Lần báo/phiên bản thực báo, normal/exception theo ngày; max chống retry đếm lại | Bộ đếm 90 ngày dạng ngày, tác vụ dọn; xóa trẻ làm rỗng và bỏ lần báo ngay | Parent/child-view đúng trẻ; admin |
| device_tokens: token_hash, device_id, kind, expires | Access 15 phút, refresh 30 ngày, ràng máy, chỉ hash; thu hồi chặn truy cập thường | Access hết hạn dọn. Refresh hết hạn không vào chức năng thường; verifier giữ đến ACK xóa để máy offline dài ngày còn nhận lệnh xóa. Sau ACK không refresh, hash hết hạn dọn | Auth/agent; không dashboard/log |
| commands: id, device_id, child_id, key, payload, ack, created | Lệnh/thứ tự/hạn/idempotency/ACK; cộng giờ một thiết bị/ngày, không nhân ngoại lệ | 90 ngày; delete_data/reduce_budget chưa ACK giữ bền vững | Parent/child-view đúng trẻ; agent của máy |
| transfers: id, child_id, donor_id, recipient_id, weekday_sec, weekend_sec, effective_date, applied | Chuyển/trả phần chia sau donor lưu giảm và ACK, hiệu lực ngày sau | Chờ hoàn tất; đã áp xóa khi lệnh liên quan hết retention | Hệ thống; parent xem allocation/lệnh |
| batches: id, device_id, key, body_hash, created | Chống lô retry đếm trùng, không chứa nội dung event | 90 ngày, xóa ngay khi xóa trẻ | Hệ thống |
| audit: id, child_id, actor, ts, ip, action, old, new | Ai/lúc/IP/giá trị trước-sau; IP và old/new AES-GCM; không ghi password/token/key | 90 ngày, xóa liên quan khi xóa trẻ | Parent/child-view đúng trẻ; admin |
| agent state/usage/events/batches/applied_commands | Cache policy ký, quỹ/quota, lô offline, idempotency; credentials DPAPI, ACL ProgramData theo thiết kế lab | Queue tối đa 100.000; event 90 ngày, lô ACK dọn; chống replay cần qua reboot. delete_data xóa policy/usage/queue/audit, chỉ giữ cleanup/ACK tối thiểu đến xác nhận | Service; tray qua IPC xác thực; user thường không được ghi cấu hình |
| agent security_audit: id, ts, category, details | Lệch đồng hồ với drift_sec cho M6; không tạo activity type thứ mười | 90 ngày, xóa khi delete_data | LocalSystem/admin lab; chưa đồng bộ thành activity event server |
| schema_versions: version, applied_at | Theo dõi migration, không dữ liệu trẻ | Tuổi thọ DB | Vận hành |

Gói source không có dữ liệu runtime hoặc credentials. `scripts/package_release.py` loại runtime, database, key/pem, cache, dependency và git; manifest chỉ tên/độ dài/SHA-256 nguồn. Browser QA nội bộ `scripts/browser_check.mjs` phụ thuộc skill trên máy phát triển, không thuộc gói phát hành.

## Bảo vệ và xóa

- SQLite WAL; AES-GCM đúng các trường nêu trên, nonce ngẫu nhiên mỗi lần, key 32 byte từ cấu hình môi trường riêng. Không mã hóa toàn bộ SQLite. Backup phải bảo vệ cả DB và khóa; mất khóa không khôi phục được tên/audit.
- Scrypt, cookie HttpOnly/Secure/SameSite=Lax, CSRF và ownership. Launcher TLS 1.2+; agent xác minh CA/pin trước credentials, policy/lệnh Ed25519. Có test API/tamper/TLS cục bộ, chưa suy ra mọi triển khai LAN đều an toàn.
- Server dọn mỗi giờ; agent prune queue/security audit. Queue đầy báo lỗi, dừng thu và hiển thị cảnh báo theo runtime. ACL/user thường/tray phải thử thực trên máy nghiệm thu.
- Xóa server bỏ event/audit/tên/policy/usage ngay, lưu lệnh bền vững và trạng thái **chờ máy xác nhận**. Agent xóa cache trước ACK; batch cũ bị từ chối. Parent xem `/api/children/{id}/deletion-status`; không tuyên bố xóa mọi nơi trước ACK.
- Thu hồi chặn policy/event/thu mới ngay; cleanup chỉ nhận/xác nhận xóa, kể cả refresh đã hết hạn thường. Hash cleanup trong hạn còn để retry ACK bị mất phản hồi; không mở lại truy cập thường. Không lấy phần giờ offline để cấp trùng; giảm/chuyển phần chia cần ACK, hiệu lực ngày sau.
- Xóa logic không đảm bảo xóa mọi sector SSD, backup ngoài ứng dụng hay ảnh do người vận hành đã lưu. Người giữ các bản đó phải xử lý riêng.

## Bản dành cho trẻ

- **KidSafe xem gì?** Tên ứng dụng, tên trang web tối thiểu và thời gian dùng để em và bố mẹ sắp xếp học/chơi/nghỉ. Không đọc chat, nghe âm thanh, chụp màn hình hoặc ghi chữ em gõ.
- **Em biết đang chạy thế nào?** Có biểu tượng và lời giải thích khi chặn. Không hiện được biểu tượng thì agent phải dừng; điều này còn cần được thử trên máy nghiệm thu.
- **Em xem được không?** Tài khoản của em xem “Hôm nay em đã dùng gì”, thời lượng/app/miền và các thay đổi liên quan; có thể xin thêm giờ, không sửa quy tắc hoặc xem trẻ khác.
- **Lưu đâu, bao lâu?** Server mạng nhà/lab và bộ nhớ chờ máy em. Hoạt động tối đa 90 ngày. Bố mẹ có thể xóa sớm; máy mất mạng phải kết nối và xác nhận trước khi nói đã xóa xong.
- **Mất mạng thì sao?** Giữ lịch và phần giờ đã chia, kể cả sau 3 ngày; không tự thêm giờ. Chuyển phần giờ cần máy trả xác nhận và có hiệu lực ngày sau để tránh cấp trùng.
- **Mở khóa khác cộng giờ thế nào?** Mở khóa tối đa 15 phút dù ngoài lịch/hết quota; giờ ngoại lệ ghi riêng, hết hạn về quy tắc cũ. Khóa ngay hủy ngoại lệ. Cộng 15 tăng quỹ chung và giữ lịch. App/website đang chặn vẫn chặn. Gần hết giờ có lời nhắc lưu bài và nút xin thêm giờ.
