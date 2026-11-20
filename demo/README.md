# Demo KidSafe

**Xem trước online cho nhóm**. Gói Streamlit riêng có trang đăng nhập và giao diện phụ huynh với dữ liệu mẫu. Xem [cách đóng gói và deploy](streamlit_preview/README.md).

Hai giao diện chạy cùng backend HTTPS: `/login`, `/app/overview` cho parent và `/child` cho tài khoản trẻ. Khởi động nhanh bằng `Start-KidSafe.ps1`, hoặc từng lệnh bên dưới. Video nộp cuối chưa quay; dữ liệu do browser test tạo được ghi rõ tên “hồ sơ demo”, không giả làm số đo enforcement Windows.

Từ gốc kho, sau khi cài dependency:

```powershell
.\.venv\Scripts\python.exe -m scripts.init_lab
.\.venv\Scripts\python.exe -m scripts.seed_lab
.\.venv\Scripts\python.exe -m scripts.run_server
```

Địa chỉ app: `https://localhost:8443/login`; API docs vẫn ở `/docs`. Tài khoản phụ huynh được tạo riêng ở `.runtime/lab.json`; mật khẩu ngẫu nhiên, không nhúng vào mã hoặc báo cáo. CA công khai ở `.runtime/tls/ca.crt`; không tắt kiểm chứng TLS của agent. Chứng chỉ chưa được tự cài vào Windows trust store. Không chia sẻ `lab.json`, file `.key` hoặc database thật.

Script init từ chối ghi đè cấu hình đã có. Lần chạy sau bỏ bước init. Ctrl+C dừng server khi chạy trực tiếp. Loopback chỉ dùng trên một máy; khi dùng LAN cần cấp chứng chỉ có IP/DNS của server trong SAN và mở cổng theo lab thật, không chỉ đổi URL.

Một máy vật lý có thể chạy server ở host và agent ở Windows VM, nhưng hiện chưa phát hiện VM đã cài. Không cài agent enforcement lên máy làm việc để thay thế kiểm thử user thường/khóa/DNS. Kịch bản hai máy theo D011 vẫn là kế hoạch nghiệm thu.
