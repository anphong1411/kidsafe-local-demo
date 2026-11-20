# Cài KidSafe cho Windows x64

Bộ cài dành cho Windows 10/11 x64 và có sẵn Python cùng các thư viện của agent. Windows của con cần một tài khoản quản trị để cài và một tài khoản cục bộ loại **Standard user** để con sử dụng.

## Chuẩn bị và ghép đôi

1. Chuẩn bị máy chủ KidSafe HTTPS mà máy của con có thể truy cập. Dùng [mô hình hai máy cùng LAN](TWO_PC_SETUP.md) hoặc [một máy và Windows VM](ONE_PC_SETUP.md).
2. Mở `/login`. Nếu chưa có tài khoản, chọn **Tạo tài khoản phụ huynh**, điền tên, tài khoản và mật khẩu, rồi đăng nhập. Thêm hồ sơ con và mở **Thiết bị & ghép đôi**. Tải **Tệp kết nối** và bộ cài Windows. Không cần tạo tài khoản web cho con. Nếu máy con không mở được trang tải qua HTTPS của LAN, tải bằng trình duyệt đã tin CA trên máy cha mẹ rồi chuyển hai tệp sang máy con.
3. Chạy `KidSafe-Setup-x64.exe` trên máy của con và xác nhận quyền quản trị. Chọn tệp `KidSafe-ket-noi.kidsafe`, tài khoản Windows thường của con và kết nối Wi-Fi/Ethernet đang dùng.
4. Trên dashboard, chọn đúng hồ sơ rồi tạo mã ghép đôi 8 ký tự. Nhập mã trong cửa sổ cài, trong vòng 10 phút. Sau khi có thông báo thành công, đăng nhập **tài khoản Windows thường của con** để khởi động KidSafe. App mở màn hình Hôm nay của em để xem giờ và xin thêm 5/10/15 phút. Đóng cửa sổ chỉ thu về tray; bấm biểu tượng KidSafe hoặc mở KidSafe từ Start để xem lại.

Tệp kết nối chỉ chứa địa chỉ HTTPS, CA công khai, dấu vân tay chứng chỉ và khóa xác minh chính sách. Hãy tải từ dashboard của gia đình qua kết nối tin cậy. Bộ cài kiểm tra TLS và pin trước khi gửi mã. Chứng chỉ localhost đơn thuần không dùng được trên máy con.

Để gỡ, thu hồi thiết bị trên dashboard trước nếu máy con còn online. Sau đó dùng **Installed apps → KidSafe → Uninstall** bằng tài khoản quản trị. Nếu bước khôi phục DNS lỗi, giữ lại dữ liệu và bộ cài hiện tại để phục hồi.

## Tạo lại bộ cài

Trên máy phát triển Windows x64, dùng Python của dự án với dependency đúng `requirements.lock` và trình biên dịch Inno Setup. Lệnh tạo `releases/KidSafe-Setup-x64.exe` và thử import thư viện từ runtime sẽ được nhúng.

```powershell
.\.venv\Scripts\python.exe -m scripts.build_windows_setup --iscc 'C:\path\to\ISCC.exe'
```

Đặt file này ở thư mục `releases/` của máy chủ để kích hoạt nút tải trên `/download`. Bản build hiện tại chưa ký số. Kiểm tra cài/gỡ, tray, ACL và hoàn nguyên DNS trên Windows sạch trước khi phát hành rộng rãi. [Inno Setup](https://jrsoftware.org/isinfo.php)
