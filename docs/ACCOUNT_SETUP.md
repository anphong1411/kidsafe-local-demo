# Tạo tài khoản phụ huynh và giữ dữ liệu khi triển khai

## Luồng sử dụng

1. Tại trang Đăng nhập, chọn **Tạo tài khoản phụ huynh**. Có thể mở thẳng `/register`.
2. Điền tên của bạn, tên tài khoản từ 3 ký tự, mật khẩu ít nhất 10 ký tự và nhập lại mật khẩu. Tên tài khoản dùng chữ không dấu, số hoặc `. _ @ -`.
3. Sau khi tạo thành công, trang đăng nhập điền sẵn tên tài khoản. Nhập mật khẩu để vào bảng điều khiển.
4. Chọn **Thêm hồ sơ con**, rồi **Thiết bị & ghép đôi**. Tải tệp kết nối và tạo mã ghép 8 ký tự có hiệu lực 10 phút. Con sử dụng app Windows đã ghép đôi để xem thời gian và xin thêm giờ; không cần tài khoản web.

Tạo tài khoản không tự đăng nhập và không tạo dữ liệu mẫu. Mỗi phụ huynh có gia đình riêng; tài khoản công khai luôn có vai trò `parent`. Tài khoản Windows thường của con khác tài khoản web phụ huynh. Người đã đăng nhập hợp lệ có thể mở trang thiết bị trong cùng trình duyệt; người chưa đăng nhập hoặc đã đăng xuất sẽ được chuyển về `/login`.

## Tài khoản được lưu ở đâu?

Tài khoản nằm trong SQLite của máy chủ FastAPI, theo `KIDSAFE_DATABASE_URL`. Mật khẩu lưu dưới dạng scrypt; tên hiển thị được mã hóa AES-GCM. Dữ liệu không chỉ nằm trong trình duyệt. Đăng xuất hoặc khởi động lại ứng dụng không xóa tài khoản.

## Khi đưa web lên máy chủ khác

Máy chủ phải chạy được Python/FastAPI và có thư mục hoặc volume lưu trữ bền vững. Chỉ đưa HTML lên hosting tĩnh sẽ không chạy được đăng ký, đăng nhập hay lưu dữ liệu của KidSafe.

- Trỏ `KIDSAFE_DATABASE_URL` vào ổ lưu bền vững, chẳng hạn `sqlite:///D:/KidSafe-data/kidsafe.db` trên Windows hoặc `sqlite:////var/lib/kidsafe/kidsafe.db` trên Linux. Không để DB trên ổ tạm bị tạo lại khi deploy.
- Giữ nguyên `KIDSAFE_ENCRYPTION_KEY` và `KIDSAFE_SIGNING_SEED` trong cấu hình bí mật của máy chủ. Không sinh khóa mới mỗi lần khởi động. Khóa mã hóa thay đổi sẽ khiến dữ liệu tên/audit cũ không đọc được.
- Sao lưu DB nhất quán cùng các khóa bằng cơ chế SQLite backup hoặc khi ứng dụng đã dừng; không sao chép riêng file DB đang chạy mà bỏ qua WAL. Không đưa DB và khóa lên Git.
- Cấu hình HTTPS và `KIDSAFE_ALLOWED_HOSTS` đúng địa chỉ triển khai. Giữ một worker theo kiến trúc WebSocket/rate limit hiện tại.

Mô hình đang chạy vẫn là server trong LAN. Đưa server lên Internet còn cần thiết kế kết nối agent và reverse proxy phù hợp; việc thêm đăng ký không tự chuyển mô hình mạng. Chưa có nhà cung cấp hosting cụ thể được chọn hoặc bản deploy cloud được kiểm chứng.

Đã kiểm thử tài khoản mới đăng nhập lại được sau khi tạo một instance ứng dụng khác với cùng DB/khóa; nâng cấp schema giữ được tài khoản cũ. Xem [bằng chứng D049](evidence/d049-registration/README.md).
