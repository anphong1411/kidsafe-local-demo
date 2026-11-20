# Các điểm cần giảng viên làm rõ

Trạng thái: câu hỏi chuẩn bị cho nhóm sử dụng, **chưa có trả lời của giảng viên**. Người dùng xác nhận hiện chỉ có bản DoAn01 đã cung cấp. Đây không phải yêu cầu bổ sung đã được giảng viên ban hành.

## 1 Bộ tên miền và mẫu số tỷ lệ chặn

F2 yêu cầu chặn ≥95% trên bộ 50 miền và 0 dương tính giả trên 20 miền giáo dục. Nhưng phụ lục cộng thành 60 mục: 20 giáo dục + 10 giải trí + 8 mạng xã hội + 7 trò chơi + 5 điểm cuối DoH + 10 miền mô phỏng cần chặn.

Xin thầy/cô xác nhận bộ nộp cần 50 hay 60 mục; 20 miền giáo dục nằm trong hay ngoài bộ 50? Tỷ lệ ≥95% được tính trên 50 miền được cấu hình cần chặn, hay trên tập con có nhãn cần chặn trong bộ dữ liệu? Nhóm sẽ nộp expected labels và báo riêng số chặn đúng, bỏ lọt, dương tính giả để tránh mẫu số mơ hồ.

Tham chiếu: Q-SOURCE-01, R-F2-03/09, phụ lục P231–P248. Bảng phân loại ≥200 mục/6 nhóm là yêu cầu riêng, không thay cho bộ test DNS. Mọi miền thử đều an toàn, không có miền nội dung người lớn.

## 2 Các tham chiếu D1 và NT5

Bản đề nhóm nhận được nhắc demo D1 và nguyên tắc NT5, nhưng không có phần định nghĩa tương ứng; số mục chuyển đến 4 rồi 5, 6 và 8. Xin thầy/cô cho biết có nội dung bổ sung hoặc rubric nào cần áp dụng không?

Trong lúc chờ, nhóm vẫn giữ các yêu cầu đã viết trực tiếp: quan sát cảnh báo 10/5/1 phút và 60 giây lưu bài; trẻ xem dữ liệu của mình và audit liên quan. Không tự dựng nội dung D1/NT5 hoặc coi chúng đã được cung cấp đầy đủ.

Tham chiếu: Q-SOURCE-02, R-F1-04, R-F4-04.

## 3 Ân hạn 60 giây và quota 3 phút

Đề vừa yêu cầu quota 3 phút khóa đúng hạn, vừa yêu cầu ân hạn 60 giây lưu bài. Nhóm đề xuất **60 giây cuối nằm trong quota**: còn 1 phút thì nhắc lưu bài, quota 3 phút vẫn khóa ở phút thứ 3, không thành phút thứ 4. Xin thầy/cô xác nhận đây có phải cách nghiệm thu mong muốn không, hay 60 giây phải cộng sau khi hết quota?

Người dùng đã chọn phương án trên để chuẩn bị (D020); **chưa có xác nhận của giảng viên**. Nếu câu trả lời khác, nhóm sẽ sửa timeline, state machine, test, video và báo cáo trước khi nghiệm thu.

Tham chiếu: Q-SOURCE-04, R-F1-01/04. Yêu cầu khóa ngoài lịch trong 5 giây vẫn được giữ, không tự thêm 60 giây khiến vượt ngưỡng đó.

## 4 Ghi nhận chỉnh đồng hồ và gỡ cài đặt

Đề bắt buộc ghi nhận việc lùi đồng hồ và có phần nên có ghi sự kiện gỡ cài đặt, nhưng danh sách chín event types không có hai loại tương ứng. Nhóm đề xuất ghi vào audit/security log riêng có mục đích và quyền xem rõ, giữ nguyên event bảy trường/chín type. Xin thầy/cô xác nhận cách làm này phù hợp hay cần quy ước khác?

Tham chiếu: Q-SOURCE-03, R-F1-05, R-F4-05, R-F3-01. Nhóm chưa tự thêm event type thứ mười.

## Cập nhật khi có câu trả lời

| Câu | Ngày nhận | Nội dung trả lời/nguồn xác nhận | File cần cập nhật | Trạng thái |
| --- | --- | --- | --- | --- |
| 1 | Chưa có | — | REQUIREMENTS, dataset design, VALIDATION_PLAN, báo cáo | Chờ giảng viên |
| 2 | Chưa có | — | REQUIREMENTS, demo/report plan | Chờ giảng viên |
| 3 | Chưa có | — | BRAINSTORM, ARCHITECTURE, IMPLEMENTATION_PLAN, VALIDATION_PLAN | Chờ giảng viên |
| 4 | Chưa có | — | Schema/audit design, PRIVACY, VALIDATION_PLAN | Chờ giảng viên |

Ghi câu trả lời theo nguồn thật, giữ lịch sử phương án trước đó và ngày thay đổi. Không biến suy luận của AI hoặc lựa chọn nhóm thành lời xác nhận của giảng viên.
