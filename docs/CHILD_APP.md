# App Windows của con

Phụ huynh quản lý trên website. Con dùng KidSafe trên Windows, không cần mở trang web hoặc đăng nhập tài khoản web của con.

## Bắt đầu

1. Phụ huynh đăng ký/đăng nhập website, thêm hồ sơ con và lấy tệp kết nối/mã ghép đôi.
2. Cài bộ cài Windows trên máy con, chọn tài khoản **Windows thường** và ghép bằng mã8 ký tự trong10 phút.
3. Khi đăng nhập tài khoản Windows của con, tray hiện và mở **Hôm nay của em**. Có thể mở lại bằng biểu tượng KidSafe hoặc KidSafe trong Start.

Trong cửa sổ có thời gian còn trên **máy này**, quỹ giải trí còn lại và hai mục: hoạt động trong ngày, thay đổi từ ba mẹ. Báo cáo được đồng bộ từ cùng dữ liệu của phụ huynh; khi mất mạng có thông báo đang chờ kết nối. Số giờ trên máy dùng bộ đếm cục bộ thực, không chờ tải trang web.

Con chọn5/10/15 phút rồi bấm **Xin thêm giờ**. App lưu yêu cầu khi offline và gửi khi kết nối lại. Ba mẹ duyệt trên web; yêu cầu không tự cộng giờ. Nếu đã có lời xin đang chờ trong10 phút, app không tạo thêm yêu cầu trùng. Quy tắc lịch và chặn app/web vẫn áp dụng. Ngoại lệ mở khóa đến hết ngày được thông báo riêng.

Đóng cửa sổ chỉ thu về tray. Chọn **Thoát (agent cũng dừng)** mới dừng tray. Không có chế độ agent ẩn. `/child` trên web được giữ cho phụ huynh xem báo cáo và tương thích tài khoản cũ, không phải bước con phải sử dụng.

## Kiểm tra an toàn trên máy phát triển

```powershell
.\.venv\Scripts\python.exe -m agent.child_window --preview
.\.venv\Scripts\python.exe -m scripts.check_child_window --output .tmp/child-ui
```

Hai lệnh chỉ mở UI với dữ liệu mẫu; nút gửi bị tắt trong preview. Không có service, lease, khóa máy, kết thúc tiến trình hoặc đổi DNS. Công cụ chụp chỉ dùng `PrintWindow` của chính cửa sổ mẫu, không chụp desktop.

Bộ cài1.0.1 chứa cửa sổ native và runtime Python; không dùng WebView/trình duyệt, không phụ thuộc tkinter/MFC. Đã thử UI trong runtime đóng gói trên Windows 11. Cài/gỡ thật, tray/service/user thường/DNS và độ trễ mạng vẫn cần nghiệm thu trên child lab được phép; không chạy enforcement trên host làm việc để thay bằng chứng này.
