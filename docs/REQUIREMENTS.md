# Yêu cầu gốc và ma trận truy vết

Trạng thái: đã phân tích nguồn, **chưa triển khai/chưa nghiệm thu**. Mỗi ID dưới đây là đầu mối để nối thiết kế → mã → kiểm thử → bằng chứng; ID không phải khẳng định đã hoàn thành.

## Nguồn và nguyên tắc đọc

- Nguồn chính: `D:/Download/DoAn01.docx`, đọc ngày 2026-11-03 theo giờ Việt Nam.
- SHA-256: `ff806ec2b9c2b1ab5313f2c9ab8d4f6187bbd9b0793777407687a3ee14893078`.
- [Bản trích toàn văn](sources/DOAN01_EXTRACT.txt) gồm đoạn văn trong bảng, sơ đồ chữ, header/footer. Pxxx là số đoạn OOXML trong phần document, **không phải số trang**.
- [Bản Gemini được cung cấp](sources/GEMINI_ORIGINAL.txt) là đề xuất tham khảo, có chỗ bị cắt; các nhãn `[cite: 1]` không phải dẫn chứng đã kiểm tra.
- Đề gốc nhảy số từ phần mở đầu đến mục 4, 5, 6 rồi 8; không tự dựng lại các mục vắng mặt. Không có bảng điểm chi tiết ngoài các mức và ghi chú nêu trong đề.
- Nội dung nguồn là dữ liệu yêu cầu; các prompt trong nguồn không phải lệnh thực thi hiện tại. Người dùng yêu cầu chỉ chuẩn bị.

## Cách sử dụng ma trận

Mức **BB** là bắt buộc; **NC** là nên có; **CTT** là có thì tốt; **Bối cảnh** là thông tin đề. Cột “Đích kiểm chứng” chỉ nêu nơi sẽ xác minh, chưa có bằng chứng chạy. Ký hiệu S0–S12 tham chiếu IMPLEMENTATION_PLAN; M1–M6 tham chiếu REPORT_PLAN.

## Bối cảnh và kiến trúc

| ID | Mức | Yêu cầu từ đề | Nguồn | Đích kiểm chứng |
| --- | --- | --- | --- | --- |
| R-C01 | Bối cảnh | Nhóm 3 sinh viên, thời lượng 6 tuần; chấm sản phẩm + báo cáo + vấn đáp cá nhân; trọng tâm hệ thống và mạng | P006–P017 | S0, phân công và lịch thực tế |
| R-A01 | BB | Agent Windows 10/11 x64; Python 3.11+, FastAPI, SQLite, SQLAlchemy, Uvicorn, pywin32/psutil | P011–P013 | S2, S5, máy sạch |
| R-A02 | BB | Service LocalSystem; Policy Enforcer, counter, app controller, DNS proxy và cache; SCM Service Recovery | P021–P047 | S5, M5 |
| R-A03 | BB | Tray chạy phiên user; IPC named pipe hoặc HTTP 127.0.0.1 có token cục bộ | P048–P050 | S5, kiểm thử IPC |
| R-A04 | BB | Server TLS, SQLite WAL, phân trang và rate limit | P051–P053 | S3, API/security |
| R-A05 | BB | Web phụ huynh dùng được trên điện thoại; Jinja2 + HTMX hoặc React nhẹ | P054–P056 | S4, trình duyệt desktop/mobile |
| R-A06 | BB | Policy gần nhất + hàng đợi SQLite trong ProgramData; chỉ SYSTEM/Administrators được ghi | P057–P059 | S5, ACL/offline |
| R-P01 | BB | Enroll: mã 8 ký tự hạn 10 phút, fingerprint thiết bị, trả device_id và access/refresh; lưu sự đồng ý cha mẹ tại ghép đôi theo cách đề nêu | P061–P062 | S3, S5, consent/token tests |
| R-P02 | BB | Heartbeat 60 giây: trạng thái, quota đã dùng, policy_version; trả phiên bản mới + lệnh chờ; lệch phiên bản thì GET /policy | P063 | S3, S5, đo mạng |
| R-P03 | BB | WebSocket: khóa, mở khóa, cộng 15 phút; độ trễ dưới 5 giây | P064 | S8, đo end-to-end |
| R-P04 | BB | Offline vẫn áp cache, đếm giờ và đệm sự kiện; online đồng bộ theo lô có idempotency key | P065 | S5, S8, M5 |
| R-P05 | BB | Nhóm phải chọn fail-open/fail-closed sau N ngày mất kết nối, nêu lý do và bảo vệ khi vấn đáp | P066 | S0, S5, M5 |

## F1 Quản lý thời gian

| ID | Mức | Yêu cầu và tiêu chí | Nguồn | Đích kiểm chứng |
| --- | --- | --- | --- | --- |
| R-F1-01 | BB | Quota ngày thường/cuối tuần; thử quota 3 phút và khóa đúng hạn | P074–P076 | S6, V-F1 |
| R-F1-02 | BB | Lịch 7×48, bước 30 phút; ngoài lịch khóa trong 5 giây | P077–P079 | S6, V-F1 |
| R-F1-03 | BB | Không tính lúc khóa hoặc idle quá 5 phút; sai số ≤ ±30 giây/giờ so đồng hồ bấm tay | P080–P082 | S6, phép đo đủ 1 giờ |
| R-F1-04 | BB | Cảnh báo trước 10/5/1 phút; ân hạn 60 giây để lưu bài; quan sát trong D1 | P083–P085 | S6, demo, làm rõ D1 |
| R-F1-05 | BB | Lùi đồng hồ 3 giờ không tăng quota và phải ghi nhận sự kiện | P086–P088 | S6, M6, làm rõ loại log |
| R-F1-06 | NC | Ngân sách theo nhóm app; hai bộ đếm độc lập | P089–P091 | Sau bắt buộc, hai counter |
| R-F1-07 | CTT | Thưởng giờ khi hoàn thành nhiệm vụ phụ huynh giao | P092–P094 | Sau bắt buộc |

## F2 Kiểm soát ứng dụng và website

| ID | Mức | Yêu cầu và tiêu chí | Nguồn | Đích kiểm chứng |
| --- | --- | --- | --- | --- |
| R-F2-01 | BB | Allowlist/blocklist ứng dụng, tên tiến trình + SHA-256 executable; đổi tên notepad.exe → game.exe vẫn nhận diện | P100–P102 | S6, kiểm thử file sao chép an toàn |
| R-F2-02 | BB | Chặn bằng kết thúc tiến trình và cửa sổ giải thích, không im lặng | P103–P105 | S6, demo |
| R-F2-03 | BB | DNS proxy 127.0.0.1:53, tên miền + mọi subdomain; chặn ≥95% bộ 50 miền; 0 false positive trên 20 miền giáo dục | P106–P108 | S7, V-DNS, làm rõ mẫu số |
| R-F2-04 | BB | 6 nhóm: giáo dục, giải trí, mạng xã hội, trò chơi, không phù hợp lứa tuổi, chưa phân loại; policy mặc định 6–11 tuổi; bảng ít nhất 200 mục nộp kèm | P109–P111 | S2/S7, dataset + policy |
| R-F2-05 | BB | SafeSearch bằng DNS; kiểm bằng nslookup và trình duyệt | P112–P114 | S7, ảnh/lệnh |
| R-F2-06 | NC | DoH: block endpoint phổ biến, NXDOMAIN canary, khuyến nghị policy trình duyệt; thử bật DoH Chrome và nêu kết quả/cách xử lý | P115–P117 | S7/S9, M3 |
| R-F2-07 | NC | Chống đổi DNS thủ công; thử 8.8.8.8, chứng minh còn chặn hoặc giải thích giới hạn | P118–P120 | S9, M3 |
| R-F2-08 | CTT | Proxy HTTP(S) lọc đường dẫn hoặc WFP | P121–P123 | Sau bắt buộc, không phá tối thiểu dữ liệu |
| R-F2-09 | BB | Dữ liệu thử công khai, an toàn; tuyệt đối không dùng/truy cập/đính kèm miền người lớn để thử | P125 | S2/S7/S11, rà dataset |

## F3 Minh bạch và báo cáo

| ID | Mức | Yêu cầu và tiêu chí | Nguồn | Đích kiểm chứng |
| --- | --- | --- | --- | --- |
| R-F3-01 | BB | Sự kiện đúng 7 trường: ts, device_id, child_id, type, subject, duration_sec, policy_id; type chỉ thuộc 9 giá trị bên dưới; subject app hoặc miền cấp hai, không URL đầy đủ | P127 | S2/S3/S5, schema/negative tests |
| R-F3-02 | BB | Dashboard: thời lượng ngày/tuần, top 10 app, top 10 domain, số bị chặn, danh sách yêu cầu | P128 | S4/S8, báo cáo không đếm trùng |
| R-F3-03 | BB | Trẻ xem cùng dữ liệu trên màn hình “Hôm nay em đã dùng gì”, ngôn ngữ đơn giản + hình minh họa | P129 | S4/S8, quyền child-view |
| R-F3-04 | BB | Retention 90 ngày và tác vụ tự xóa; nút xóa toàn bộ dữ liệu con trên server và cache agent | P130 | S3/S8, online/offline deletion |
| R-F3-05 | BB | PRIVACY.md bảng từng trường/mục đích/thời hạn/ai xem; trường không có mục đích phải loại; có bản cho trẻ | P131, P211–P213 | S0/S8/S11 |
| R-F3-06 | NC | Xuất báo cáo tuần PDF hoặc CSV | P132 | Sau bắt buộc |
| R-F3-07 | CTT | Nhắc nghỉ mắt 20-20-20 | P133 | Sau bắt buộc |

Chín giá trị type: `app_start`, `app_stop`, `domain_query`, `blocked_app`, `blocked_domain`, `quota_warning`, `locked`, `unlock_request`, `override_granted`. Idempotency ở metadata truyền/lô hoặc bảng riêng, không tự thêm trường thứ tám vào event. Chuẩn hóa miền có hậu tố nhiều phần như `edu.vn` cần thiết kế rõ, không tách chuỗi lấy hai nhãn một cách máy móc.

## F4 Cấu hình từ xa

| ID | Mức | Yêu cầu và tiêu chí | Nguồn | Đích kiểm chứng |
| --- | --- | --- | --- | --- |
| R-F4-01 | BB | 1 phụ huynh : n trẻ : m thiết bị | P135 | S2/S3, quan hệ + IDOR |
| R-F4-02 | BB | Sửa policy có hiệu lực trong 60 giây; lệnh khẩn trong vòng 5 giây | P136 | S8/S10, áp dụng thực tế |
| R-F4-03 | BB | Policy có version và HMAC hoặc chữ ký; agent từ chối policy bị sửa | P137 | S3/S5, integrity tests |
| R-F4-04 | BB | Audit mọi thay đổi: ai, lúc nào, IP, giá trị cũ/mới; trẻ có quyền xem | P138 | S3/S4/S8 |
| R-F4-05 | NC | Gỡ hợp pháp bằng mật khẩu phụ huynh tại máy trẻ, ghi sự kiện gỡ | P139 | Sau bắt buộc, giải quyết loại log |
| R-F4-06 | CTT | Tạm nghỉ phụ huynh 2 giờ có log | P140 | Sau bắt buộc |

## F5 Bảo mật và quyền riêng tư

| ID | Mức | Yêu cầu tối thiểu | Nguồn | Đích kiểm chứng |
| --- | --- | --- | --- | --- |
| R-F5-01 | BB | Argon2id hoặc scrypt; mật khẩu ≥10 ký tự; sai 5 lần khóa 15 phút; rate limit IP | P144–P145 | S3, auth tests |
| R-F5-02 | BB | Cookie HttpOnly/Secure/SameSite=Lax; phiên 12 giờ; logout hủy server-side; CSRF mọi thao tác ghi | P146–P147 | S3, session/CSRF tests |
| R-F5-03 | BB | TLS 1.2+; lab được dùng CA tự ký; pin chứng chỉ agent, sai pin từ chối | P148–P149 | S3/S5, TLS test |
| R-F5-04 | BB | Access token 15 phút + refresh; ràng buộc device_id; danh sách thu hồi khi gỡ thiết bị | P150–P151 | S3/S5, token lifecycle |
| R-F5-05 | BB | AES-GCM trường nhạy cảm; khóa từ env/DPAPI, không hardcode; băm bí mật thiết bị | P152–P153 | S2/S3/S5, storage review |
| R-F5-06 | BB | parent/child-view/admin; ownership ở tầng truy vấn chống IDOR | P154–P155 | S3/S4, cross-family tests |
| R-F5-07 | BB | Trẻ là user thường, không Administrators; ACL cấu hình chỉ SYSTEM/Administrators ghi | P156–P157 | S5/S9, máy lab |
| R-F5-08 | BB | STRIDE ≥8, gồm trẻ tấn công và stalkerware; checklist ASVS trong tài liệu nộp | P158–P159, P214–P216 | S0/S9/S11 |
| R-F5-09 | BB | Không chế độ ẩn; không hiển thị được icon thì agent tự dừng; tài liệu phạm vi sử dụng hợp pháp | P160–P161 | S5/S9, lifecycle tray/service |
| R-F5-10 | Điểm cộng | TOTP hai yếu tố | P145 | Sau bắt buộc |

## Mạng, kiểm thử và sản phẩm nộp

| ID | Mức | Yêu cầu | Nguồn | Đích kiểm chứng |
| --- | --- | --- | --- | --- |
| R-M1 | BB | Luồng browser → stub resolver → DNS proxy → tra danh sách → phản hồi; ảnh Wireshark/tcpdump query/response | P169–P171 | S7/S10, phụ lục M1 |
| R-M2 | BB | So hosts/DNS proxy/HTTP(S) proxy/WFP theo 5 tiêu chí, giải thích chọn phương án | P172–P174 | S0/S10, M2 |
| R-M3 | BB | ≥7 kỹ thuật vượt rào, từng kỹ thuật có mô tả, thử thực tế, đối phó hoặc chấp nhận rủi ro | P175–P177 | S9/S10, M3; kế hoạch thử cả 9 kỹ thuật đề liệt kê |
| R-M4 | BB | CPU/RAM idle và peak; DNS p50/p95 có/không agent; policy latency; mỗi phép đo ≥30 mẫu và phương pháp | P178–P180 | S10, raw samples + M4 |
| R-M5 | BB | Mất mạng, server dừng, agent bị kill; mong đợi/thực tế/thời gian phục hồi | P181–P183 | S9/S10, M5 |
| R-M6 | BB | Monotonic + đối chiếu server mỗi heartbeat + ngưỡng cảnh báo lệch/chỉnh giờ | P184–P186 | S6/S10, M6 |
| R-D01 | BB | /agent: source, requirements.txt, hướng dẫn cài service, chạy Windows sạch | P193–P195 | S11/S12 |
| R-D02 | BB | /server: source, migration, seed; tài khoản demo trong README | P196–P198 | S2/S3/S11 |
| R-D03 | BB | /dashboard: giao diện parent và child, dùng mobile | P199–P201 | S4/S11 |
| R-D04 | BB | /tests: ≥15 unit + 5 integration, ảnh chụp kết quả | P202–P204 | S9/S11 |
| R-D05 | BB | /docs/BaoCao.docx 20–30 trang, phân công + tự đánh giá % đóng góp | P205–P207 | S11/S12 |
| R-D06 | BB | /docs/BaoCaoKyThuatMang.pdf đủ M1–M6 | P208–P210 | S10/S11 |
| R-D07 | BB | /docs/AI_USAGE.md nêu phần/công cụ/cách kiểm chứng | P217–P219 | Mọi bước, S11 |
| R-D08 | BB | /demo/video.mp4 dài 5–7 phút, phụ đề hoặc thuyết minh tiếng Việt | P220–P222 | S11/S12 |
| R-D09 | BB | README cài được ≤15 phút trên Windows sạch, giảng viên làm theo | P223–P225 | S11/S12, đo cài thực |

## Điểm mơ hồ phải xử lý trước hạng mục liên quan

| Mã | Vấn đề | Hướng chuẩn bị, chưa phải quyết định |
| --- | --- | --- |
| Q-SOURCE-01 | Phụ lục P231–P248 cộng 20+10+8+7+5+10 = 60, trong khi F2 nói bộ 50 miền và 20 giáo dục | Xin giảng viên xác nhận mẫu số. Giữ dataset phân loại ≥200 tách khỏi bộ kiểm thử. Có thể chuẩn bị superset 60 và tập con 50 được gắn nhãn rõ, nhưng chưa tự tuyên bố đây là cách chấm của đề. |
| Q-SOURCE-02 | Đề nhắc “D1”, “NT5” nhưng không định nghĩa đầy đủ; các mục 1–3 và 7 không có trong file cung cấp | Người dùng xác nhận chỉ có DoAn01. Ghi câu hỏi giảng viên trong QUESTIONS_FOR_INSTRUCTOR; vẫn thực hiện yêu cầu hiển thị cảnh báo và trẻ xem audit đã được mô tả trực tiếp. |
| Q-SOURCE-03 | Bắt buộc log chỉnh giờ; NC log gỡ, nhưng 9 event types không có loại riêng | Đề xuất dùng audit/security log riêng có mục đích và retention, giữ nguyên 7 trường + 9 loại event; cần chốt/đối chiếu giảng viên trước khi thêm schema. |
| Q-SOURCE-04 | Quota khóa đúng hạn nhưng đồng thời ân hạn 60 giây; không có timeline chi tiết | D020: phương án chuẩn bị dùng 60 giây cuối trong quota, quota 3 phút khóa ở phút 3, đang chờ giảng viên xác nhận. Ghi timeline/test theo phương án tạm, không tuyên bố đã được duyệt. |
| Q-SOURCE-05 | Độ trễ lệnh có chỗ “dưới 5”, chỗ “trong vòng 5”; poll 60 giây còn có network overhead | Dùng tiêu chí bảo thủ lệnh <5 giây; thiết kế nhận biết/áp policy để đo end-to-end ≤60 giây, không chỉ đặt timer 60 giây rồi khẳng định đạt. |
| Q-SOURCE-06 | Agent offline không thể xóa vật lý tức thì từ xa | Thiết kế xóa server ngay + lệnh xóa bền vững + ACK agent, chặn tái nhập dữ liệu cũ; giao diện báo đang chờ. Không nói “đã xóa mọi nơi” khi agent chưa xác nhận. |
| Q-SOURCE-07 | Đề để nhóm chọn N ngày offline; quyền ưu tiên allowlist/blocklist/lịch/quota/lệnh mở khóa chưa chỉ rõ | Đã chốt N=3 ngày/fail-closed; quota chung chia trước từng máy. Theo D017/D038, Cộng 15 giữ lịch, Mở khóa có audit và giờ ngoại lệ cho đến nửa đêm hoặc khi phụ huynh Khóa ngay, giữ quy tắc chặn app/domain. Đây là quyết định nhóm. |
| Q-SOURCE-08 | “Tên miền cấp hai” và danh mục 200 mục chưa quy định format/file | Đề xuất domain đăng ký theo suffix chuẩn; phân biệt miền lọc đầy đủ và subject tối thiểu. Xác nhận cách hiểu trước hạng mục. |
| Q-SOURCE-09 | Dừng agent khi icon không hiện trong bối cảnh boot/logoff/nhiều phiên | Thiết kế handshake tray/service có xác thực và trạng thái hiển thị; hỏi cách xử lý chuyển phiên; không dùng cờ “ẩn” để lách yêu cầu. |

Các câu hỏi này không phải lý do để bỏ yêu cầu. Mỗi câu trả lời sẽ được ghi trong BRAINSTORM_NOTES và cập nhật lại thiết kế/kế hoạch kiểm chứng.
