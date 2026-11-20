# KidSafe — ứng dụng quản lý thời gian và an toàn máy tính cho trẻ

**Nhận source để quay demo?** Bắt đầu tại [Hướng dẫn chạy local và quay video trên hai máy Windows](docs/DEMO_HAI_MAY.md).

Ứng dụng gồm backend FastAPI/SQLAlchemy/SQLite WAL, hai giao diện Jinja2 + HTMX cho phụ huynh và trẻ, cùng agent Windows service/tray. Quản lý hồ sơ/thiết bị, lịch 7×48, quota chung/phần giữ offline, app name/SHA-256, DNS/SafeSearch, lệnh WebSocket, báo cáo, audit và xóa dữ liệu. Xem [kiểm chứng thực tế](docs/evidence/README.md), [nhật ký triển khai](docs/IMPLEMENTATION_LOG.md), [trạng thái hiện hành](docs/PROJECT_STATE.md).

Đã có bộ cài/gỡ/hoàn nguyên DNS cho máy trẻ và giao diện nối API thật. Chưa nghiệm thu service/tray/ACL/DNS trên Windows user thường, chưa đủ benchmark/capture M1–M6 hoặc cài Windows sạch ≤15 phút. Đây là giới hạn kiểm chứng của môi trường hiện tại, không phải bằng chứng các tiêu chí đã đạt. Hồ sơ nộp Word/PDF/video cuối chưa hoàn tất.

## Chạy ứng dụng

**Cách dùng đã chốt:** phụ huynh dùng web, con dùng app Windows. Sau khi ghép đôi, KidSafe trên máy con hiển thị thời gian, hoạt động và nút xin thêm 5/10/15 phút; con không cần đăng nhập web. Xem [hướng dẫn app của con](docs/CHILD_APP.md).

**Tài khoản phụ huynh:** mở `/login` và chọn **Tạo tài khoản phụ huynh**, hoặc vào `/register`. Điền tên, tài khoản và mật khẩu, sau đó đăng nhập và thêm hồ sơ con. Tài khoản được lưu trong SQLite của máy chủ. Xem [cách dùng và lưu dữ liệu khi triển khai](docs/ACCOUNT_SETUP.md).

**Cài trên máy con:** trang `/download` cung cấp bộ cài Windows 10/11 x64 khi máy chủ có `releases/KidSafe-Setup-x64.exe`. Xem [hướng dẫn cài và ghép đôi](docs/WINDOWS_SETUP.md).

**Đăng trang tải công khai:** dùng [gói và hướng dẫn GitHub Pages](docs/GITHUB_PAGES_DEPLOY.md). Tạo lại gói bằng `./.venv/Scripts/python.exe -m scripts.package_github_pages`. Máy chủ KidSafe tiếp tục chạy riêng trong LAN khi demo hai máy.

**Xem trước giao diện phụ huynh qua link**. Dùng [bản preview Streamlit và hướng dẫn deploy](demo/streamlit_preview/README.md). Bản xem trước có tài khoản riêng và dữ liệu minh họa.

**Chỉ có một máy:** xem [ONE_PC_SETUP.md](docs/ONE_PC_SETUP.md), gồm mở web cho người mới và tạo WindowsVM để thử agent. Profile riêng `.runtime/vm`, host `https://localhost:8446`, guest NAT `https://10.0.2.2:8446`. Không cài agent trên host cho bài thử này.

**Chạy trên hai máy:** làm theo [TWO_PC_SETUP.md](docs/TWO_PC_SETUP.md). Launcher có `-RuntimeDirectory '.runtime\lan'` để tạo chứng chỉ/IP, tài khoản và database LAN riêng, không ghi đè demo localhost. Hướng dẫn dùng cổng8444 để tránh xung đột bản demo8443.

PowerShell tại gốc kho: `./Start-KidSafe.ps1`. Có thể chỉ định `-Python 'C:\Program Files\Python312\python.exe'` khi Python chưa có trong PATH. Script tạo venv/cài dependency khi cần, tạo cấu hình private và khởi động HTTPS. Hoặc dùng các lệnh riêng bên dưới.

Cần Python 3.11+ x64. Chạy PowerShell tại gốc kho:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.lock
.\.venv\Scripts\python.exe -m scripts.init_lab
.\.venv\Scripts\python.exe -m scripts.seed_lab
.\.venv\Scripts\python.exe -m scripts.run_server
```

Đăng nhập tại `https://localhost:8443/login`; giao diện parent `/app/overview`, child `/child`, API docs `/docs`. Tài khoản/mật khẩu demo ngẫu nhiên trong `.runtime/lab.json`; không đưa file này vào gói nộp. CA ở `.runtime/tls/ca.crt`, chưa tự cài trust Windows; trình duyệt cần tin CA lab để không cảnh báo chứng chỉ, agent luôn kiểm CA + pin. Lần chạy sau bỏ init; script từ chối ghi đè identity. Ctrl+C dừng server. Xem [demo](demo/README.md), [dashboard](dashboard/README.md) và [agent](agent/README.md).

Máy trẻ: trên máy Windows lab riêng/user thường, làm theo `agent/README.md` và `agent/scripts/Install-ChildLab.ps1`. Xuất CA/pin/public key bằng `python -m scripts.export_public_config`; chỉ mang `.runtime/public/` qua máy trẻ, **không mang lab.json hoặc .key**. Ghép bằng mã một lần do parent tạo. LAN cần cấp chứng chỉ từ đầu có `--host <IP/DNS server>` trong SAN; chỉ đổi bind hoặc URL là chưa đủ. Có thể dùng `Start-KidSafe.ps1 -CertificateHosts '192.168.1.10' -Bind '0.0.0.0'` trong lab được cấu hình phù hợp.

Kiểm tra độc lập khi server đang chạy: `.\.venv\Scripts\python.exe -m scripts.check_lab`. Test: `.\.venv\Scripts\python.exe -m pytest --basetemp=.tmp/pytest-local`; đổi thư mục tạm khi có test song song. Các test socket chỉ dùng localhost, không đổi DNS/khóa máy/cài service.

Đã chốt với người dùng: tên **KidSafe**, dashboard **Jinja2 + HTMX**, nhóm 3 người, còn 5 tuần, dùng Windows 11 và có quyền quản trị để cài lab. Đề vẫn yêu cầu trẻ dùng tài khoản user thường. OGK/OpenGuard Kids là tên tham chiếu trong đề gốc.

Server chạy **LAN trên máy riêng với máy trẻ**. Sau **3 ngày offline**, agent vẫn áp quota/lịch cuối (fail-closed). Quota **dùng chung theo trẻ giữa các máy**, chia trước ngân sách offline cho từng máy và đổi phần chia khi có mạng, tổng không vượt quota. **Mở khóa ngoài lịch có ngoại lệ 15 phút và audit**, hết hạn quay về lịch/quota. Cảnh báo nhẹ nhàng, có thời gian còn lại, nhắc lưu bài và nút xin thêm giờ.

Quy tắc đã chốt thêm: **Cộng 15 phút** tăng quota chung nhưng không bỏ lịch; **Mở khóa** cho tối đa 15 phút cả khi quota đã hết, ghi giờ ngoại lệ; **Khóa ngay** hủy ngoại lệ. Danh sách chặn app/website vẫn giữ. Sau phần bắt buộc, ưu tiên **DoH và chống đổi DNS**.

Hồ sơ yêu cầu/brainstorming được giữ để truy vết. Phương án ân hạn là 60 giây cuối nằm trong quota (3 phút khóa ở phút 3), đang chờ giảng viên xác nhận. Phân công để trống theo yêu cầu, chờ thông tin thành viên sau.

Đã bổ sung [định hướng giao diện](docs/UI_DESIGN_BRIEF.md) từ [sáu ảnh bạn cung cấp](docs/design-references/README.md): ảnh lớp cho bố cục/luồng, Pinterest cho màu sắc và cảm giác trẻ em. Theo D028, UI đã được triển khai tiếp khi thiếu lab; G-UI giữ làm cổng nghiệm thu, không tự đánh dấu Windows đã đạt.

Ngày 2026-11-04, người dùng chỉ định **[Design-PH.md](docs/Design-PH.md) làm nguồn định hướng bảng màu/style cho giao diện phụ huynh**. Hướng màu trẻ em/Pinterest tiếp tục dành cho child-view; chi tiết phối màu parent được thống nhất từ nguồn này khi tới S4.

## Đọc theo thứ tự

1. [Trạng thái và việc còn chờ](docs/PROJECT_STATE.md).
2. [Yêu cầu đề gốc và các điểm cần làm rõ](docs/REQUIREMENTS.md).
3. [Gemini đã đủ chưa và những phần cần bổ sung](docs/GEMINI_REVIEW.md).
4. [Sổ brainstorming và các câu hỏi đang chờ](docs/BRAINSTORM_NOTES.md).
5. [Kế hoạch từng bước khi được yêu cầu bắt đầu](docs/IMPLEMENTATION_PLAN.md).

## Hồ sơ bổ trợ

| Tài liệu | Mục đích |
| --- | --- |
| [ARCHITECTURE.md](docs/ARCHITECTURE.md) | Kiến trúc nháp, giao thức, điểm chưa chốt |
| [PRIVACY.md](docs/PRIVACY.md) | Bảng dữ liệu và bản giải thích cho trẻ |
| [THREATMODEL.md](docs/THREATMODEL.md) | STRIDE, biện pháp dự kiến, checklist ASVS chưa kiểm chứng |
| [VALIDATION_PLAN.md](docs/VALIDATION_PLAN.md) | Tiêu chí nghiệm thu, unit/integration, phép đo và bằng chứng |
| [REPORT_PLAN.md](docs/REPORT_PLAN.md) | Báo cáo chính, M1–M6, video và gói nộp |
| [AI_USAGE.md](docs/AI_USAGE.md) | Khai báo công cụ AI và mức kiểm chứng thực tế |
| [QUESTIONS_FOR_INSTRUCTOR.md](docs/QUESTIONS_FOR_INSTRUCTOR.md) | Câu hỏi về nguồn đề, bộ DNS, ân hạn và loại log; chưa có trả lời giảng viên |
| [UI_DESIGN_BRIEF.md](docs/UI_DESIGN_BRIEF.md) | Ý tưởng UI, màn hình/trạng thái cần có, cách vận dụng ảnh lớp và Pinterest |
| [Design-PH.md](docs/Design-PH.md) | Tài liệu người dùng cung cấp, định hướng bảng màu/style riêng cho parent |
| [DESIGN_SKILL_REVIEW.md](docs/DESIGN_SKILL_REVIEW.md) | Đánh giá UI UX Pro Max, bản tham khảo đã tải, kết quả tra thử và cách dùng bổ trợ |
| [AGENTS.md](AGENTS.md) | Lệnh ghi nhớ bám đề và giới hạn giai đoạn hiện tại |

## Cài đặt và chạy

Chưa có mã nguồn hoặc lệnh cài/chạy/build/test. Không chạy các prompt triển khai trong bản Gemini ở giai đoạn này. Khi có sản phẩm, phần này phải được thay bằng hướng dẫn đã thử trên Windows sạch, mục tiêu hoàn thành trong 15 phút, kèm tài khoản demo, cấu hình mẫu, dependency có phiên bản/lockfile, hướng dẫn cài và gỡ dịch vụ hợp pháp.

## Trạng thái

- Đã đọc và đối chiếu nguồn; đã lập hồ sơ chuẩn bị.
- Đã ghi câu trả lời của sáu đợt brainstorming; phân biệt quyết định người dùng, đề xuất kỹ thuật và điểm chờ giảng viên.
- Chờ người dùng rà soát hồ sơ; phân công được chủ động để trống. Chỉ bắt đầu làm phần mềm khi người dùng ra lệnh rõ ràng.

