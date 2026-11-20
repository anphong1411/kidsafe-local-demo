# Chạy KidSafe trên hai máy để quay video

Máy A là máy quản lý. Phụ huynh mở web trên máy này. Máy B là máy con, chạy ứng dụng KidSafe trong khay hệ thống Windows. Dùng hai máy Windows x64 cùng mạng Wi-Fi gia đình, hoặc cùng mạng dây. Giữ máy A thức suốt buổi quay. Chuẩn bị tài khoản quản trị trên cả hai máy và một tài khoản Windows thường trên B. Sao lưu bài đang làm trước khi thử khóa máy.

## 1. Nhận mã nguồn trên máy A

Nếu có Git, mở PowerShell ở nơi muốn lưu project, gõ `git clone` tiếp theo là một khoảng trắng, dán link HTTPS của **repo source** rồi thêm ` KidSafe` ở cuối và nhấn Enter. Sau đó gõ `cd KidSafe`. Những lần nhận bản cập nhật, mở PowerShell trong thư mục này và gõ `git pull`.

Nếu chưa dùng Git, vào repo → **Code → Download ZIP**, giải nén và mở thư mục chứa **Start-KidSafe.ps1**. Nhấp phải khoảng trống → **Open in Terminal**. Kiểm tra có file `releases\KidSafe-Setup-x64.exe`. Máy A cần Python 3.12 x64 (chọn Add python.exe to PATH khi cài) và Internet ở lần đầu để tải thư viện. Máy B đã có Python bên trong bộ cài.

## 2. Bật máy chủ trên A

Trong Windows Settings → Network & internet, đặt mạng gia đình đang dùng thành **Private**. Gõ `ipconfig` và tìm **IPv4 Address** dưới Wi-Fi hoặc Ethernet đang kết nối. Ví dụ nếu A có IP 192.168.1.10, nhập IP đó khi chạy các dòng sau ở thư mục source.

```powershell
python --version
$serverIp = Read-Host 'Nhap IPv4 cua may A'
.\Start-KidSafe.ps1 -RuntimeDirectory '.runtime\lan' -CertificateHosts $serverIp -Bind $serverIp -Port 8444
```

Nếu PowerShell báo script bị chặn, kiểm tra đúng source do nhóm gửi, chạy `Set-ExecutionPolicy -Scope Process RemoteSigned` trong cửa sổ hiện tại. Với bản ZIP tải từ trình duyệt, mở Properties của ZIP → **Unblock** nếu có, giải nén lại rồi chạy. Đợi dòng Uvicorn running và giữ cửa sổ mở.

Mở **PowerShell thứ hai bằng Run as administrator** trên A. Cho phép kết nối từ mạng nội bộ vào cổng demo.

```powershell
if (-not (Get-NetFirewallRule -Name KidSafe-LAN-8444 -ErrorAction SilentlyContinue)) {
    New-NetFirewallRule -Name KidSafe-LAN-8444 -DisplayName 'KidSafe LAN 8444' -Direction Inbound -Action Allow -Protocol TCP -LocalPort 8444 -Profile Private -RemoteAddress LocalSubnet
}
```

Mở **Terminal thường** tại thư mục source bằng tài khoản phụ huynh. Tin chứng chỉ do máy A vừa tạo và mở đúng địa chỉ LAN.

```powershell
Import-Certificate -FilePath '.runtime\lan\tls\ca.crt' -CertStoreLocation 'Cert:\CurrentUser\Root'
$serverIp = Read-Host 'Nhap lai IPv4 cua may A'
Start-Process "https://${serverIp}:8444/register"
```

Tạo tài khoản phụ huynh với mật khẩu từ 10 ký tự rồi đăng nhập. Tạo hồ sơ con bằng tên giả để quay. Trong **Thời gian & lịch**, chọn khung giờ hiện tại được phép sử dụng và đặt hạn mức trước khi ghép máy. Mở **Thiết bị & ghép đôi** của đúng hồ sơ và tải **KidSafe-ket-noi.kidsafe**. Chép tệp này cùng **releases\KidSafe-Setup-x64.exe** sang B bằng USB. Giữ thư mục `.runtime` riêng trên A. Lần sau chạy lại lệnh ở đầu mục 2 với cùng IP và thư mục để dùng lại tài khoản, hồ sơ và lịch sử.

## 3. Ghép máy B

1. Trên B, mở PowerShell và chạy `Test-NetConnection 192.168.1.10 -Port 8444`, thay IP ví dụ bằng IP thật của A. Chỉ tiếp tục khi thấy **TcpTestSucceeded = True**. Nếu False, kiểm tra máy A còn chạy, IP, mạng Private, rule ở mục 2 và hai máy có đang dùng Wi-Fi khách cách ly thiết bị hay không.
2. Trên B vào **Settings → Accounts → Other users**, thêm tài khoản Windows thường cho con. Đăng nhập tài khoản đó một lần, đăng xuất rồi trở về tài khoản quản trị.
3. Chạy bộ cài trên B bằng quyền quản trị. Chọn tệp kết nối, đúng tài khoản con và đúng card Wi-Fi/Ethernet. Trên A tạo mã ghép đôi cho hồ sơ, xác nhận đồng ý. Nhập mã 8 ký tự vào bộ cài trong 10 phút. Mã hết hạn thì tạo mã mới. Bộ cài của nhóm chưa ký Authenticode. Có thể đối chiếu SHA-256 bằng `Get-FileHash .\KidSafe-Setup-x64.exe` với file .sha256 đi kèm trước khi chạy.
4. Khi cài xong, đăng xuất quản trị và đăng nhập tài khoản Windows của con. Mở KidSafe từ Start hoặc khay hệ thống. Trên A, kiểm tra đúng thiết bị có thời điểm liên lạc mới. Nếu chưa thấy, kiểm tra icon trên B, IP trong tệp kết nối và kết quả thử cổng. Nếu cần chẩn đoán, chạy `Get-Service KidSafe` trên B.

## 4. Kịch bản quay

| Cảnh | Thao tác để quay | Bằng chứng cần thấy |
| --- | --- | --- |
| Ghép đôi | A mở hồ sơ và danh sách thiết bị, B mở app từ khay | Đúng thiết bị đang liên lạc và cửa sổ con hiện thời gian còn lại |
| Xin giờ | B chọn xin 5 phút. A mở Yêu cầu, duyệt rồi trở lại B | Trạng thái và thời gian cập nhật sau khi đồng bộ |
| Lọc web | A thêm example.org vào danh sách chặn. Đợi B nhận chính sách, thử nslookup example.org và một miền an toàn được phép trên B | Ghi lại kết quả thực tế của cả hai truy vấn |
| Điều khiển | Lưu bài trên B. A chọn Khóa máy ngay, chờ xác nhận, sau đó chọn Mở khóa | B khóa thực sự. Sau lệnh mở, người dùng tự đăng nhập lại Windows |
| Báo cáo | A mở báo cáo và lịch sử thao tác | Chỉ ra thời điểm và hoạt động tương ứng với các cảnh vừa quay |

Quay hai màn hình hoặc chuyển cảnh giữa A và B. Che mật khẩu, mã ghép đôi và dữ liệu cá nhân. Hãy chạy thử cả kịch bản một lần trước khi quay. Bài đo quota 3 phút nên dùng hồ sơ mới đặt hạn mức từ trước khi ghép. Một máy con đủ quay luồng trên, kiểm chứng chia quota giữa hai thiết bị con cần thêm máy hoặc VM.

## 5. Dừng và gỡ sau khi quay

Để giữ dữ liệu cho lần sau, nhấn Ctrl+C ở cửa sổ server A sau khi kết thúc buổi demo. App trên B vẫn áp dụng chính sách offline. Khi kết thúc thử nghiệm và muốn trả B về trạng thái bình thường, đăng nhập quản trị trên B → **Installed apps → KidSafe → Uninstall**, kiểm tra DNS và truy cập mạng trở lại. Trên A, nếu ngừng dùng lab, gỡ rule riêng bằng `Remove-NetFirewallRule -Name KidSafe-LAN-8444` trong PowerShell quản trị. Xem thêm [xử lý lỗi và khôi phục DNS](TWO_PC_SETUP.md).
