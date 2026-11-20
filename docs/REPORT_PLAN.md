# Kế hoạch báo cáo, phụ lục và video KidSafe

Tên KidSafe do người dùng chọn ngày 2026-11-03. OpenGuard Kids/OGK là tên thành phần trong đề để đối chiếu; đổi tên không làm đổi yêu cầu. Đây là đề cương, chưa có báo cáo cuối hay kết quả thử thực tế.

## Báo cáo chính docs/BaoCao.docx

Đề yêu cầu 20–30 trang. Phân bổ dưới đây gợi ý khoảng 25–28 trang, sẽ kiểm sau render và xác nhận quy ước tính bìa/mục lục/phụ lục với giảng viên nếu cần.

| Phần | Nội dung | Trang dự kiến |
| --- | --- | --- |
| Bìa, mục lục, tóm tắt | Tên đề tài, nhóm, phạm vi, kết quả thật khi có | 3 |
| Bài toán và yêu cầu | Người dùng, 6–11 tuổi, minh bạch, BB/NC/CTT, ma trận truy vết | 3 |
| Kiến trúc và dữ liệu | Service/tray/server/web, ERD, event schema, trust boundaries | 4 |
| Vòng đời và giao thức | Enrollment/consent/token, heartbeat, batch/idempotency, policy integrity, WebSocket, offline/expiry/deletion | 4 |
| Hiện thực chức năng | F1–F4, quyết định đã chốt, màn hình và luồng chính | 4 |
| Bảo mật và riêng tư | F5, STRIDE, checklist ASVS thực tế, giới hạn | 3 |
| Kiểm thử và đánh giá | Test counts, bằng chứng/đo chính, dẫn M1–M6, hạn chế thật | 3 |
| Phân công, tự đánh giá, kết luận, tài liệu tham khảo | Nhiệm vụ/% từng người, AI disclosure, hướng phát triển | 2–4 |

Không bịa tên thành viên, phần trăm đóng góp hoặc kết quả. Hỏi tên/phân công khi biết điều kiện nhóm; tổng % và cách tự đánh giá phải được thành viên kiểm tra. Báo cáo phải nêu lựa chọn fail-open/fail-closed sau N ngày và cách bảo vệ lựa chọn trong vấn đáp.

Theo D021, hiện **để trống phân công** và chưa tự gán vai trò tạm. Thông tin thành viên, công việc và % đóng góp được điền sau từ người dùng/kết quả làm thực tế; việc để trống hiện tại không bỏ yêu cầu phân công của báo cáo cuối.

D020 chọn phương án tạm để xin xác nhận: 60 giây cuối nằm trong quota, quota 3 phút khóa ở phút 3. Khi viết báo cáo/video phải ghi đúng mức xác nhận; xem QUESTIONS_FOR_INSTRUCTOR, không kể đây là yêu cầu giảng viên đã làm rõ nếu chưa có phản hồi.

Quyết định thực tế đã chốt để đưa vào báo cáo sau này: server LAN riêng, N=3 ngày/fail-closed giữ quota và lịch cuối; quota chung theo trẻ chia trước từng máy và đổi khi có mạng; lời nhắc nhẹ nhàng; mở khóa ngoài lịch cho ngoại lệ 15 phút có audit. Lý do đề xuất để nhóm thảo luận khi vấn đáp: mất mạng không trở thành cách vượt lịch/quota; cần đánh đổi với việc không nhận được phê duyệt mới khi server không liên lạc. Giờ chưa trả của máy offline không được cấp lại cho máy khác, nên có thể phải chờ xác nhận mới chuyển được. Đây là thiết kế chuẩn bị, chưa được viết thành giải pháp đã làm.

Bổ sung D017 đã duyệt: Mở khóa tối đa 15 phút dù quota cạn, ghi riêng giờ ngoại lệ; Cộng 15 tăng quota chung nhưng không bỏ lịch; Khóa ngay hủy ngoại lệ; các rule app/domain vẫn giữ. D018 ưu tiên NC DoH/chống đổi DNS sau BB. Báo cáo phải tách kết quả của NC này với phần phân tích M3 bắt buộc, không nâng mức NC thành điều kiện nộp mới.

## Phụ lục docs/BaoCaoKyThuatMang.pdf

| Mục | Phải có | Dữ liệu/bằng chứng cần lưu |
| --- | --- | --- |
| M1 | Sơ đồ mở trang bị chặn: browser → stub resolver → proxy → rule lookup → response | Capture Wireshark/tcpdump query/response an toàn, ảnh chú thích và filter/lệnh |
| M2 | 4 phương án hosts/DNS proxy/HTTP(S) proxy/WFP × 5 tiêu chí: độ chính xác, chặn HTTPS, chi phí hiện thực, vượt rào, hiệu năng; vì sao chọn DNS | Bảng so sánh có nguồn kỹ thuật chính thức và lập luận phù hợp lab; không nhầm DNS lọc host với giải mã HTTPS |
| M3 | ≥7 kỹ thuật vượt rào, từng mục mô tả/thử thật/kết quả/đối phó hoặc chấp nhận rủi ro | Dự kiến thử cả 9 kỹ thuật đề nêu; máy/OS/bước/ảnh/giới hạn; không nâng kết quả “chưa thử” thành “đã chặn” |
| M4 | CPU/RAM idle+peak; DNS p50/p95 có và không agent; policy latency | ≥30 mẫu mỗi phép/điều kiện; raw CSV, phương pháp/cache/load, cấu hình máy, công thức/percentile và biểu đồ |
| M5 | Mất mạng, server down, agent kill | Expected/actual, timestamp bắt đầu/phục hồi, policy/cache/queue/recovery và icon |
| M6 | Monotonic, đối chiếu server mỗi heartbeat, ngưỡng cảnh báo | Diagram/time trace và thử lùi 3 giờ; phân biệt đo khoảng thời gian với timestamp hiển thị |

Phụ lục không được chỉ là ảnh benchmark. M2 cần phân tích; M3/M5 cần thử; M1 cần capture. Nguồn kỹ thuật/phiên bản cần kiểm tra khi viết chính thức.

## Video demo demo/video.mp4

Mục tiêu khoảng 6 phút trong ngưỡng 5–7 phút, có thuyết minh hoặc phụ đề tiếng Việt. Kịch bản dự kiến, sẽ điều chỉnh theo phần mềm thật:

| Thời lượng | Cảnh |
| --- | --- |
| 0:00–0:35 | Bài toán, tên KidSafe, thành phần/máy lab, tray nhìn thấy |
| 0:35–1:15 | Parent tạo mã, ghép máy, consent và policy |
| 1:15–2:30 | Quota/lịch, cảnh báo/grace và khóa; có thể quay trước để dựng rõ mốc, ghi chú nếu tua nhanh |
| 2:30–3:25 | App đổi tên vẫn nhận diện; DNS/subdomain và SafeSearch an toàn |
| 3:25–4:15 | Xin giờ, duyệt/cộng 15/khóa khẩn, dashboard mobile và child-view/audit |
| 4:15–5:10 | Mất mạng/cache/reconnect; chỉnh giờ; xóa dữ liệu và trạng thái ACK |
| 5:10–6:00 | Kết quả test, số đo mạng, giới hạn đường vòng và kết thúc |

Không lấy video 6 phút để thay phép đo 1 giờ. Không giấu độ trễ bằng dựng phim; nếu demo rút gọn thì dẫn evidence phép đo thật. Không lộ bí mật hay dùng nội dung/domain không an toàn.

## Checklist gói nộp

- [ ] `/agent`: source, requirements.txt, cài service/tray/dừng/gỡ/restore cấu hình.
- [ ] `/server`: source, migration, seed và demo credentials trong README.
- [ ] `/dashboard`: parent và child, mobile dùng được.
- [ ] `/tests`: ≥15 unit + ≥5 integration và ảnh kết quả thật.
- [ ] `/docs/BaoCao.docx`: 20–30 trang, phân công/% được xác nhận.
- [ ] `/docs/BaoCaoKyThuatMang.pdf`: đủ M1–M6, số liệu khớp nguồn thô.
- [ ] `/docs/PRIVACY.md`: đủ trường thực, mục đích/retention/người xem và bản trẻ.
- [ ] `/docs/THREATMODEL.md`: ≥8 threat + checklist ASVS có evidence/phạm vi.
- [ ] `/docs/AI_USAGE.md`: công cụ/phần/cách kiểm chứng thật.
- [ ] `/demo/video.mp4`: 5–7 phút, tiếng Việt, mở được.
- [ ] `/README.md`: máy Windows sạch cài ≤15 phút, lệnh đã thử, config example, tài khoản demo.
- [ ] Bảng phân loại ≥200 mục/6 nhóm và bộ test an toàn nộp kèm; đã giải quyết cách hiểu 50/60.
- [ ] Không kèm khóa riêng, token thật, venv/dependencies cài sẵn hoặc dữ liệu cá nhân thật.

## Chuẩn bị vấn đáp

Mỗi người hiểu phần mình và các giao diện nối với phần khác. Tập trả lời: vì sao DNS proxy; vì sao không chặn hết DoH/VPN/USB; cách chống double count; pinning khác TLS thường; monotonic khác wall clock; HMAC khác chữ ký; deletion khi offline; hạn chế của quyền admin; lựa chọn fail-mode. Chưa phân công người cụ thể khi chưa có thông tin năng lực/thời gian từng thành viên.
