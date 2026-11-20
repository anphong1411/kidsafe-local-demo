# Chạy KidSafe trên hai máy Windows

**Luồng hiện tại dùng bộ cài .exe có sẵn Python.** Làm theo [hướng dẫn GitHub Pages và ghép đôi trong LAN](GITHUB_PAGES_DEPLOY.md), bắt đầu ở phần B nếu đã có bộ cài. Phần bên dưới ghi lại quy trình cài từ mã nguồn phục vụ kiểm thử kỹ thuật.

Máy A chạy server và web phụ huynh. Máy B là máy trẻ được phép thử khóa máy/chặn app/đổi DNS, có tài khoản admin để cài và tài khoản `kidsafe-child` thuộc Standard user để dùng. Hai máy cùng LAN/Wi-Fi tin cậy, không dùng Wi-Fi khách có cách ly thiết bị. Máy B cần Internet khi pip cài dependency.

Ví dụ dưới đây dùng IP máy A `192.168.1.10`, cổng LAN `8444`. **Thay IP ví dụ bằng IPv4 thật của máy A trong mọi lệnh.** Cổng8444 giúp tránh trùng bản demo localhost8443. Không dùng localhost trong cấu hình agent máy B vì localhost ở đó là máy B.

## 1. Chuẩn bị mã và Python

Máy A đã có kho tại `D:\DoAN MMT`, venv và dependency. Dùng bản sourceZIP mới trong `releases/KidSafe-source.zip` cho máy B; giải nén vào `C:\KidSafe-source`. Không sao chép .venv hoặc thư mục .runtime.

Máy B cài Python64bit từ https://www.python.org/downloads/windows/, Python3.11+ (dự án được kiểm với3.12). Chọn Customize installation → Install for all users; đặt dưới `C:\Program Files\Python312` nếu dùng3.12. Chương trình cài và các thư viện phải nằm ở nơi trẻ không ghi được. Kiểm tra đường dẫn thực trước khi dùng lệnh mẫu; installer KidSafe từ chối Python dưới AppData. Khi chỉ dùng máy A hiện tại không cần cài lại Python ở máy A; nếu đổi sang máy A khác cần cài Python và dùng Start-KidSafe.ps1 -Python đường dẫn thật.

PowerShell để chạy script riêng của dự án có thể cần:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned
```

Nếu fileZIP tải về bị Mark-of-the-Web, chỉ bỏ chặn các script của gói KidSafe đã kiểm nguồn: `Get-ChildItem -LiteralPath . -Recurse -Filter *.ps1 | Unblock-File` khi đang đứng đúng thư mục KidSafe. Không đổi execution policy toàn máy.

## 2. Máy A: xem IP và tạo cấu hình LAN

Mở PowerShell tại gốc kho:

```powershell
Set-Location 'D:\DoAN MMT'
Get-NetIPConfiguration
```

Chọn IPv4 của Wi-Fi/Ethernet đang dùng; không chọn127.0.0.1 hoặc adapterảo. Trong Settings → Network & Internet, đặt mạng LAN tin cậy này là Private. Giữ hai máy bật, không sleep trong lúc thử.

```powershell
.\Start-KidSafe.ps1 -RuntimeDirectory '.runtime\lan' -CertificateHosts '192.168.1.10' -Bind '0.0.0.0' -Port 8444
```

Đợi Uvicorn báo chạy. Giữ cửa sổ này mở. Lệnh tạo profile mới ở `.runtime\lan`, chứng chỉ có IP server, database/khóa/tài khoản riêng; không sửa/xóa profile demo `.runtime\lab.json`. Chạy lại cùng lệnh để dùng lại profileLAN. Nếu profile đã có mà IP không khớp, launcher báo lỗi; không ghi đè khóa/chứng chỉ. IP thay đổi cần cấu hình/chứng chỉ phù hợp trước khi ghép lại, không tắt pin/TLS để né lỗi.

## 3. Máy A: mở cổng và tin CA lab

Mở **PowerShell Administrator** thứ hai:

```powershell
Set-Location 'D:\DoAN MMT'
if (-not (Get-NetFirewallRule -Name 'KidSafe-LAN-8444' -ErrorAction SilentlyContinue)) {
    New-NetFirewallRule -Name 'KidSafe-LAN-8444' -DisplayName 'KidSafe LAN 8444' -Direction Inbound -Action Allow -Protocol TCP -LocalPort 8444 -Profile Private -RemoteAddress LocalSubnet
}
```

Không tắt WindowsFirewall và không mở port trên router ra Internet. Rule chỉ áp mạng Private và LocalSubnet.

Trong PowerShell của tài khoản dùng web phụ huynh, thêm đúng CA do profileLAN vừa tạo vào kho tin cậy của tài khoản đó:

```powershell
Import-Certificate -FilePath 'D:\DoAN MMT\.runtime\lan\tls\ca.crt' -CertStoreLocation 'Cert:\CurrentUser\Root'
```

Đây là thêm CA lab của bạn để Chrome/Edge tin HTTPS. Chỉ dùng CA được chuyển trực tiếp từ profile của mình, không tải CA bất kỳ từ mạng. Nếu PowerShell Administrator chạy bằng tài khoản khác, CurrentUser là tài khoản admin đó; cần import bằng tài khoản thực dùng browser.

Mở `https://192.168.1.10:8444/login`. Tài khoản/mật khẩu:

```powershell
$login = Get-Content -Raw -LiteralPath '.runtime\lan\lab.json' | ConvertFrom-Json
$login.demo_username
$login.demo_password
```

Đọc mật khẩu riêng trên máy A, không chụp/in vào báo cáo, không gửi lab.json cho máy B. Browser phải vào trang đăng nhập không lỗi chứng chỉ.

## 4. Máy A: xuất các file công khai để mang sang máy B

```powershell
.\.venv\Scripts\python.exe -m scripts.export_public_config --config '.runtime\lan\lab.json'
```

Sao chép đúng hai file từ `.runtime\lan\public`: `ca.crt` và `server-public.json`, đặt vào `C:\KidSafe-public` trên máy B. Có thể dùng USB hoặc thư mục chia sẻ. Không sao chép lab.json, file.key, database hoặc .venv.

## 5. Máy B: tài khoản trẻ và kiểm kết nối

Tạo user `kidsafe-child` trong Settings → Accounts → Other users → Add account → I don't have this person's sign-in information → Add a user without a Microsoft account. Giữ **Standard user**, đặt mật khẩu nhớ được. Tài khoản admin hiện tại vẫn giữ để quản trị/gỡ. Đăng nhập thử tài khoản trẻ một lần để Windows hoàn tất profile, rồi Sign out và trở lại admin.

PowerShell máy B:

```powershell
Test-NetConnection 192.168.1.10 -Port 8444
```

Phải có `TcpTestSucceeded : True`. Nếu False, kiểm đúngIP, server còn chạy, mạngPrivate ở máy A, firewallrule và không Wi-Fi guest/VPN cách ly; chưa cài agent khi chưa kết nối được.

Để web child chạy dưới user trẻ tin CA, PowerShell **Administrator máy B**:

```powershell
Import-Certificate -FilePath 'C:\KidSafe-public\ca.crt' -CertStoreLocation 'Cert:\LocalMachine\Root'
```

LocalMachine áp dụng cho mọi user trên máy lab. Agent vẫn tự kiểm CAfile+pin độc lập, không bỏ kiểm TLS.

## 6. Máy B: cài agent

PowerShell **Administrator**, đứng đúng thư mục giải nén:

```powershell
Set-Location 'C:\KidSafe-source'
Get-NetAdapter | Where-Object Status -eq 'Up' | Format-Table Name,ifIndex,InterfaceDescription
```

Chọn ifIndex của card Wi-Fi/Ethernet máy B đang dùng. Ví dụ12; không lấy số card ở máy A. Nếu dùng đồng thời nhiều card có thể cần chỉ rõ mọi card có DNS sử dụng; lần đầu chỉ giữ kết nối lab dự định thử để dễ kiểm tra.

Trên web parent máy A: Thêm hồ sơ → Thiết bị & ghép đôi → Tạo mã ghép đôi → đồng ý. Mã 8 ký tự dùng một lần, hạn 10 phút; tạo sát lúc chạy bộ cài.

```powershell
$public = Get-Content -Raw -LiteralPath 'C:\KidSafe-public\server-public.json' | ConvertFrom-Json
$code = Read-Host 'Nhap ma ghep 8 ky tu tu web phu huynh'
.\agent\scripts\Install-ChildLab.ps1 -ChildLab `
  -Python 'C:\Program Files\Python312\python.exe' `
  -ServerUrl 'https://192.168.1.10:8444' `
  -CaFile 'C:\KidSafe-public\ca.crt' `
  -CertificatePin $public.certificate_pin `
  -SigningPublicKey $public.signing_public_key `
  -EnrollmentCode $code `
  -ChildUser "$env:COMPUTERNAME\kidsafe-child" `
  -InterfaceIndices 12
```

Thay Pythonpath/ifIndex bằng giá trị thật. Không thêm -DisableBrowserDoh ở lần ghép đầu; tính năng NC này thử sau khi luồng cơ bản ổn định. Nếu báo lỗi dừng để chẩn đoán; không lặp bộ cài vào thư mục đã tạo vì script chủ động từ chối ghi đè.

Sau Installed: **Sign out tài khoản admin máy B, đăng nhập kidsafe-child**. Tray và service được kích hoạt lúc trẻ logon. Mở biểu tượng ẩn ở taskbar để thấy KidSafe. Web parent phải thấy máy xuất hiện, lastseen cập nhật và policy nhận đúngversion. Có thể tạo tài khoản web riêng cho con trong trang Thiết bị; tài khoản web này khác tài khoản Windows kidsafe-child.

## 7. Kiểm tra lần đầu

Ban đầu giữ lịch cho phép, quota đủ để có thời gian kiểm tra. Parent gửi Cộng 15, xem trạng thái chờ → máy xác nhận. Sau đó thử Khóa ngay: máy B bị khóa, máy A vẫn điều khiển được. Mở khóa là cấp ngoại lệ; con vẫn tự đăng nhập Windows nếu đang ở màn hình khóa. Bài thử quota 3 phút nên dùng hồ sơ được đặt 3 phút trước khi ghép thiết bị, để tránh quyền offline đã cấp theo hạn mức lớn hơn; không thử trên user admin.

Thiết bị đầu giữ phần quota chưa cấp. Việc giảm quota chung khi máy đang giữ quyền offline có thể bị409: đổi phần chia/đợiACK và thời điểm có hiệu lực theoUI, không sửaDB để vượt ràng buộc. Để demo3phút gọn, đặtquota3phút trước khi ghép thiết bị đầu tiên.

Website: thử `example.org` trong danh sách chặn và miền con an toàn; không dùng miền nội dung người lớn. App: chỉ dùng chương trình thử an toàn có tên/SHA256 thật. Lưu ảnh/log và giờ bắt đầu/kết thúc. Hai máy không thay bằng chứng quota chung giữa hai máy trẻ; tiêu chí đó cần thêm thiết bị/VM.

## 8. Khi gặp lỗi hoặc dừng lab

Admin máy B: `Get-Service KidSafe`; `Get-ScheduledTask -TaskName 'KidSafe*'`; xem Event Viewer → Windows Logs → Application để tìm lỗi service. Không có icon thì không coi agent đang áp dụng thành công. Mã hết hạn cần cập nhật cấu hình ghép đúng quy trình, không gỡ/xóa ProgramData tùy tiện.

Gỡ/hoàn nguyên trên máyB bằng PowerShellAdmin:

```powershell
& 'C:\Program Files\KidSafe\agent\scripts\Uninstall-ChildLab.ps1' -ChildLab
```

Nếu cần chỉ khôi phục DNS sau lỗi, dùng snapshot đã lưu:

```powershell
& 'C:\Program Files\KidSafe\agent\scripts\Manage-LabDns.ps1' -Action Restore -Snapshot 'C:\ProgramData\KidSafe\service\dns-before.json' -InterfaceIndices '12'
```

Máy A: Ctrl+C cửa sổ server để dừng. Có thể xóa rule riêng sau lab: `Remove-NetFirewallRule -Name 'KidSafe-LAN-8444'`. Không xóa CA/cấu hình private nếu vẫn có thiết bị đã ghép hoặc cần dữ liệu; việc gỡ CA trust phải chọn đúng thumbprint của CA lab, không xóa certificate khác.

Các lệnh cài/đổi DNS ở đây chỉ chạy trên máy B được đồng ý thử. Bộ cài và service vẫn cần nghiệm thu Windows thật; tài liệu này không tự biến kiểm thử unit thành kết quả cài đạt.
