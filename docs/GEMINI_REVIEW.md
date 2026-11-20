# Đối chiếu quy trình Gemini với DoAn01

## Kết luận

Quy trình 6 bước là khung kỹ thuật hữu ích, nhưng **chưa đủ để nộp đúng đề và chưa đủ hướng dẫn cho người mới**. Nó bao phủ phần lớn chức năng F1–F5 ở mức mô tả, nhưng thiếu một số ràng buộc, kiểm chứng hệ thống/mạng và sản phẩm nộp. Các prompt không thể chạy nối tiếp nguyên xi mà coi đồ án đã hoàn thành.

Nguồn: REQUIREMENTS.md dẫn toàn bộ yêu cầu gốc. Bản Gemini được giữ nguyên tại `sources/GEMINI_ORIGINAL.txt`; đoạn T8 bị cắt ở “Người lớn dùng phần mềm để the”. Chưa có phần còn lại nếu Gemini đã từng trả lời thêm. `[cite: 1]` không có nguồn kèm theo để xác minh.

## Đã có hướng phù hợp

- Tách service/tray/server/dashboard, cache offline, DNS proxy và WebSocket.
- Có quota, lịch 7×48, nhận diện SHA-256, schema event tối giản, phân quyền, privacy và threat model.
- Nhắc ≥15 unit + 5 integration, benchmark và README máy sạch.
- Có sổ brainstorming để tránh mất quyết định giữa các buổi làm.

## Những gì còn thiếu hoặc chưa đủ cụ thể

| Nhóm | Gemini còn thiếu/chưa rõ | Cần bổ sung theo đề |
| --- | --- | --- |
| Sản phẩm nộp | Không có bước tạo báo cáo chính, phụ lục và video thật | BaoCao.docx 20–30 trang, phân công + tự đánh giá %, BaoCaoKyThuatMang.pdf, video.mp4 5–7 phút tiếng Việt; R-D05/06/08 |
| Báo cáo mạng | Gộp M1–M6 vào benchmark; benchmark không thay được 6 mục | M1 sơ đồ + capture; M2 bảng 4 phương án ×5 tiêu chí; M3 thử ≥7 đường vòng; M4 đo đủ; M5 3 lỗi; M6 đồng bộ thời gian |
| Đo hiệu năng | Thiếu idle/peak, baseline DNS không agent, phương pháp từng phép đo | ≥30 mẫu cho MỖI phép đo, p50/p95, đo policy từ thao tác đến áp dụng; giữ raw samples và điều kiện máy |
| Lifecycle token | Chỉ nói access/refresh chung | Access 15 phút, ràng device_id, thu hồi khi gỡ; enrollment phải gửi fingerprint và ghi consent |
| Phiên parent | Thiếu thời hạn và hủy phiên | 12 giờ, logout hủy phía server; CSRF cho mọi thao tác ghi |
| Heartbeat | Bước server nói /events, /policy nhưng chưa mô tả đủ vòng đời | Mỗi 60 giây gửi trạng thái/quota/version, nhận version mới + lệnh chờ; chỉ GET /policy khi cần |
| Offline | Hỏi sau khi code backend sẽ quá muộn cho quyết định kiến trúc | Chốt N ngày, fail-open/fail-closed, cache, replay/idempotency, khôi phục và lý do vấn đáp trước code |
| Lược đồ | Nêu 7 trường nhưng chưa chốt 9 event types và log ngoại lệ | R-F3-01; phân biệt event với audit/auth; giải quyết log chỉnh giờ/gỡ mà không tự thêm event type |
| Mã hóa lưu trữ | Chỉ có câu AES-GCM trong mẫu privacy | Chọn trường nhạy cảm, quản lý khóa env/DPAPI, băm bí mật thiết bị, nonce và vòng đời khóa; không hardcode |
| API dữ liệu | Thiếu migration, phân trang, giới hạn dữ liệu đầu vào | Nộp migration, seed lặp được, query ownership và API pagination/rate limit |
| F1 nghiệm thu | Không nêu sai số và các mốc thử cụ thể | ±30 giây/giờ; quota 3 phút; ngoài lịch ≤5 giây; lùi 3 giờ không tăng quota và có log |
| Service và IPC | Chưa mô tả đầy đủ token/ACL IPC, recovery và vòng đời icon | Tray phiên user; IPC an toàn; SCM recovery; dừng khi không hiện icon, thử boot/logoff/mất tray |
| F2 ứng dụng | Chỉ nhắc danh sách chặn | Cả allowlist/blocklist; quy tắc ưu tiên; giải thích chặn và kiểm nhận diện executable đổi tên |
| Phân loại | Seed 200 mục nhưng chưa đủ quy tắc dùng | Đúng 6 nhóm, default 6–11 tuổi, bảng phân loại nộp kèm, tách dữ liệu mẫu khỏi bộ test |
| DNS | Chưa có vận hành Windows và rollback | Xử lý port 53, upstream không loop, DNS card mạng, IPv6, cache, startup/shutdown và hoàn nguyên; đây là công việc thiết kế để đạt proxy chạy thực |
| SafeSearch | nslookup thôi chưa đủ | Thử cả trình duyệt và lưu bằng chứng |
| Xóa dữ liệu | Mẫu nói xóa ngay mọi nơi mà chưa xử lý offline | Server + mọi agent liên quan; ACK xóa; chống dữ liệu cũ quay lại; thông báo trung thực khi chưa thể liên lạc |
| Kiểm thử | Đạt số test chưa đồng nghĩa đạt nghiệm thu | Ảnh chụp test, kiểm tích hợp Windows thực, pin sai, CSRF/IDOR, ACL, tray, thông số thời gian và bằng chứng M1–M6 |
| Tổ chức đồ án | Không có lịch 6 tuần/nhóm 3 và chuẩn bị vấn đáp | Thu thập thông tin nhóm, phân công, % thực tế, mỗi người hiểu phần mình và giao thức toàn hệ thống |
| Người mới | Các prompt lớn yêu cầu làm nhiều việc cùng lúc | Từng bước có mục đích, đầu vào, đầu ra, cách chạy, điều kiện xong và hướng sửa khi lỗi; Codex tự thao tác/kiểm chứng trong quyền được giao |

## Những điểm cần sửa để không hiểu sai đề

1. **DoH là NÊN CÓ**, không phải bắt buộc như cách prompt bước 5 gộp chung. Chống đổi DNS thủ công cũng là NÊN CÓ nhưng Gemini bỏ khỏi kế hoạch. Phân tích đường vòng M3 vẫn bắt buộc dù chưa thực hiện mọi biện pháp chặn đường vòng.
2. Argon2id là lựa chọn hợp lệ, nhưng đề cho phép **Argon2id hoặc scrypt**; chưa cần coi Argon2id là lựa chọn duy nhất. Tailwind, Chart.js, pytest, HMAC cho mọi gói sự kiện là gợi ý kỹ thuật, không đều là điều kiện đề bắt buộc. Đề cho HMAC hoặc chữ ký đối với policy.
3. “Chạy ngầm” của Windows Service phải phân biệt với chế độ ẩn bị cấm. Service vẫn đi cùng tray nhìn thấy được, không có lựa chọn theo dõi lén.
4. “Mọi trường không trong bảng bị loại khỏi cơ sở dữ liệu” trong mẫu Gemini là quá rộng: **7 trường áp dụng cho event**. Còn bảng account, policy, audit, session vẫn cần trường phục vụ chức năng và phải được giải thích trong privacy.
5. Không gọi audit là “công khai” theo nghĩa ai cũng xem được: trẻ được xem audit liên quan đến mình, vẫn phải kiểm quyền sở hữu; không lộ gia đình khác.
6. HMAC không đồng nghĩa chữ ký số bất đối xứng. Cần mô tả cơ chế chọn thực tế, nơi giữ khóa và cách xác minh, không đổi tên cho nhau.
7. Bản mẫu privacy khẳng định dữ liệu ở “máy gia đình”, trong khi đề cho **LAN hoặc VPS lab**. Nơi lưu phải theo phương án thực tế và thông báo đúng.
8. Phụ lục nguồn có tổng 60 mục nhưng tiêu chí nhắc 50 miền; D1/NT5 chưa có định nghĩa. Các chỗ này phải được ghi nhận và hỏi lại, không tự bổ sung thành lời giảng viên.

## Trình tự đã bổ sung

Giữ các khối công việc của Gemini nhưng thêm bước chốt yêu cầu/môi trường trước code, chia backend/agent thành các lát kiểm chứng nhỏ, đưa kiểm thử vào từng bước, dành riêng phần M1–M6, báo cáo, video và cài máy sạch. Trình tự chi tiết và điểm dừng được lưu trong IMPLEMENTATION_PLAN.md. Hiện chưa thực hiện prompt triển khai nào.
