# Đánh giá UI UX Pro Max cho KidSafe

Ngày đánh giá: 2026-11-03. Kết luận: **hữu ích như nguồn tra cứu bổ sung khi đến bước S4**, đặc biệt cho màu/chữ, trạng thái tương tác, bố cục responsive, keyboard/focus và chọn biểu đồ. Đây không phải bộ giao diện KidSafe đã dựng hoặc công cụ tự bảo đảm UI đạt yêu cầu.

## Nguồn và bản tải

- Repo người dùng cung cấp: [nextlevelbuilder/ui-ux-pro-max-skill](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill).
- Bản đã tải cố định tại [commit 713eef51b04efc98d6fa565323b495f7c9c89fd4](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill/tree/713eef51b04efc98d6fa565323b495f7c9c89fd4).
- Thư mục nguồn: `.claude/skills/ui-ux-pro-max`; bản trong dự án: `.local-tools/design-skills/ui-ux-pro-max/`.
- Dùng helper của skill-installer với `--ref` và `--dest` cụ thể. Đã lấy kèm LICENSE của repo và README tại cùng commit; SOURCE.json trong bản tải ghi nguồn/mục đích.
- Đây là bản công cụ/tham khảo **trong dự án**, chưa đăng ký vào danh mục skill toàn cục hoặc tự kích hoạt. Có thể đọc và gọi lại ở lượt sau nhờ đường dẫn đã ghi trong AGENTS. Không cần cài npm CLI toàn cục để dùng công cụ tra cứu này.
- `.local-tools/` và `.tmp/` được gitignore: bản tải và đầu ra tạm không trở thành dependency/mã sản phẩm nộp. Nếu chuyển dự án sang máy khác, tải lại đúng commit/path bằng helper theo metadata này và giữ thông báo giấy phép đi kèm.

Không sửa skill gốc đã tải. Nội dung bên trong được đọc để tham khảo, không có quyền thay yêu cầu trực tiếp của người dùng, DoAn01 hoặc các quyết định KidSafe.

Kiểm tra bản tải: 76 file nguồn (gồm LICENSE và README lấy thêm) khớp Git blob SHA-1 trong tree của commit đã ghi; file thứ 77 là SOURCE.json do Codex tạo để ghi xuất xứ. Kiểm này xác nhận bản tải khớp nguồn, không phải bảo đảm mọi hướng dẫn hoặc mã nguồn bên ngoài đều đúng/an toàn.

## Đã kiểm tra như thế nào

Đã đọc SKILL.md, script search.py, đường import và các thao tác I/O liên quan trong core/design_system/reasoning_contract trước khi gọi tra cứu. Các lần chạy bên dưới dùng Python đóng gói sẵn, cờ `-B`, chỉ tra cứu domain và trả JSON; không dùng `--persist`, không tạo MASTER.md hoặc mã UI. Đây là kiểm tra khả năng tra cứu công cụ, **không phải kiểm thử phần mềm KidSafe hay audit bảo mật đầy đủ của repo bên ngoài**.

| Truy vấn thật | Domain | Kết quả quan sát | Đánh giá sử dụng |
| --- | --- | --- | --- |
| `children education` | product | Có kết quả Kids Learning và Educational App; nhắc parent dashboard, playful/clear hierarchy | Liên quan đối tượng trẻ, nhưng KidSafe không phải app dạy ABC/toán; chỉ lấy nguyên tắc phân tầng và cảm giác thân thiện |
| `children education` | color | Trả palette LMS | Chưa khớp trực tiếp trẻ nhỏ; đã thử thu hẹp một lần |
| `kids learning` | color | Kết quả đầu Kids Learning, nhóm xanh dương/vàng/hồng và nền sáng | Palette tham khảo có liên quan; chưa thay bộ mint/teal gợi ý từ ảnh hoặc chốt màu thay người dùng |
| `keyboard focus` | ux | Trả Focus States và Focus Not Obscured | Hữu ích để kiểm thao tác bàn phím/focus; không tự tuyên bố đã đạt tiêu chuẩn accessibility |
| `time comparison` | chart | Kết quả đầu Radar/Spider, sau đó so sánh nhóm bằng bar | Không phù hợp trực tiếp báo cáo thời lượng theo ngày; không chọn radar cho bài toán này |
| `time series` | chart | Kết quả đầu Trend Over Time/Line Chart | Phù hợp hướng biểu đồ thời gian; chọn biểu đồ cuối theo dữ liệu thật và cách trình bày của KidSafe |

Không có kết quả nào ở trên được coi là thiết kế đã được người dùng duyệt. Gợi ý reward/gamification, claymorphism, animation, React hoặc thư viện chart trong kết quả không tự trở thành chức năng/dependency mới. Khi đối chiếu nguyên tắc/tiêu chuẩn bên ngoài để tuyên bố đạt, phải kiểm nguồn chính thức và UI thật ở S4/S9.

## Cách phối hợp với các nguồn đã có

| Nguồn | Vai trò trong KidSafe |
| --- | --- |
| DoAn01 + REQUIREMENTS + quyết định người dùng | Quyết định chức năng, quyền, schema, timing và phạm vi bắt buộc |
| Ảnh lớp | Tham khảo bố cục và luồng parent/child |
| Design-PH.md, người dùng chỉ định ngày 2026-11-04 | Nguồn định hướng màu/style parent được ưu tiên hơn đề xuất màu chung và catalog skill; giữ phạm vi dashboard KidSafe |
| Screenshot Pinterest | Tham khảo màu sắc/cảm giác phù hợp trẻ em |
| UI_DESIGN_BRIEF | Ghi định hướng KidSafe, trạng thái thật, các gợi ý chưa chốt |
| design-taste-frontend, nhánh app screens | Giúp chọn bố cục có chủ đích và kiểm bằng browser/screenshot |
| UI UX Pro Max | Tra cứu bổ sung màu/chữ/interaction/chart và checklist theo vấn đề cụ thể |

Khi hai skill cho lời khuyên khác nhau, xét công việc của màn hình, đối tượng 6–11 tuổi, ảnh người dùng và dữ liệu thật; ghi lý do chọn trong brief. Không trộn nhiều phong cách chỉ vì có trong catalog; không ưu tiên quy tắc của skill hơn yêu cầu người dùng.

## Giới hạn về stack và thời điểm

Danh sách stack trong bản công cụ đã tải **không có mục Jinja2/HTMX riêng**. Chỉ dùng domain chung cho web/UI; nếu sau này chọn Tailwind thật thì mới tham khảo thêm `html-tailwind` cho phần tương ứng. Không tự thêm Tailwind, React, GSAP hoặc đổi stack vì một kết quả tìm kiếm.

Giữ D024: hoàn thiện backend/mạng bắt buộc → G-UI → S4. Khi tới S4 mới cân nhắc sinh đề xuất design system, kiểm độ phù hợp rồi lưu quyết định có chọn lọc. Không dùng sinh MASTER.md để ghi đè brief/ảnh/quyết định đã có. Bản tải này đã sẵn để dùng lại ở các lượt sau; không phải lệnh bắt đầu viết phần mềm.

## Lệnh tra cứu để dùng về sau

Chạy từ thư mục dự án, bằng Python đã xác định cho môi trường; biến dưới đây giải quyết script thành đường dẫn tuyệt đối. Các lệnh chỉ là cách gọi tra cứu, không cần người dùng chạy để tiếp tục giai đoạn chuẩn bị.

```powershell
$skillSearch = (Resolve-Path -LiteralPath '.local-tools/design-skills/ui-ux-pro-max/scripts/search.py').Path
python -B $skillSearch 'kids learning' --domain color --max-results 2 --json
python -B $skillSearch 'keyboard focus' --domain ux --max-results 2 --json
python -B $skillSearch 'time series' --domain chart --max-results 2 --json
```

Xem tên/loại kết quả trước khi áp dụng. Nếu kết quả lệch chủ đề, thử thu hẹp đúng một lần và ghi rõ giới hạn nếu vẫn không khớp; không lưu đầu ra chưa kiểm tra thành quyết định thiết kế.
