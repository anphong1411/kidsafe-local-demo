# Một máy tính chạy KidSafe — hướng dẫn từng bước

Bạn có thể làm hai chặng: (A) mở web phụ huynh để làm quen; (B) tạo Windows máy ảo để thử khóa/chặn thật. Chỉ có chặng B mới kiểm chứng agent Windows. Windows thật bên ngoài cửa sổ máy ảo gọi là **máy chính/host**; Windows trong cửa sổ gọi là **máy ảo/guest**.

Máy hiện tại trước đó kiểm được khoảng 16 GB RAM, CPU Core Ultra 7 và ổD còn khoảng 302 GB. Đề xuất bắt đầu một VM 4 GB RAM, 2 CPU và đĩa 80 GB. Đây là phân bổ khởi đầu, không phải đo hiệu năng. Chưa cài/tạo VM trong lượt hướng dẫn này.

## A. Mở web trên máy chính

1. Nhấn Windows, gõ PowerShell và mở Windows PowerShell bình thường. Chặng này chưa cần Administrator.
2. Dán từng khối lệnh rồi nhấn Enter. Nếu hỏi execution policy, đọc và xác nhận cho cửa sổ hiện tại.

```powershell
Set-Location 'D:\DoAN MMT'
Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned
.\Start-KidSafe.ps1 -RuntimeDirectory '.runtime\vm' -CertificateHosts '10.0.2.2' -Bind '127.0.0.1' -Port 8446
```

Nếu server8446 đã chạy từ lượt Codex chuẩn bị, không chạy thêm một bản trên cùng cổng. Mở URL ở bước4. Khi server chưa chạy, khối trên là lệnh khởi động cho những lần sau. Giữ cửa sổ server mở; Ctrl+C dừng nó.

3. Mở PowerShell **thứ hai**, dán:

```powershell
Set-Location 'D:\DoAN MMT'
Import-Certificate -FilePath '.runtime\vm\tls\ca.crt' -CertStoreLocation 'Cert:\CurrentUser\Root'
$login = Get-Content -Raw '.runtime\vm\lab.json' | ConvertFrom-Json
$login.demo_username
$login.demo_password
```

Lệnh import giúp trình duyệt của chính tài khoản Windows này tin CA lab vừa tạo. Chỉ tin đúng file CA của KidSafe trong dự án; không import CA bất kỳ tải trên mạng. Mật khẩu hiện riêng ở cửa sổ của bạn, không gửi/chụp lab.json vì có khóa bí mật.

4. Mở Chrome/Edge và nhập **https://localhost:8446/login**. Đăng nhập bằng hai dòng username/password vừa xem. Nếu đã mở browser trước khi importCA, đóng/mở lại browser khi cần. Lỗi chứng chỉ phải kiểm đúng URL/profile, không tắt kiểm chứng TLS của agent.
5. Nhấn Thêm hồ sơ, đặt tên con. Có thể thử giao diện lịch/bộ lọc trước; **chưa có agent nên thao tác khóa/chặn chưa tác động đến Windows**. Nếu muốn bài quota3phút, đặt3phút trước khi ghép thiết bị đầu, rồi chuẩn bị xong mới đăng nhập user trẻ.

Profile `.runtime\vm` riêng với demo `.runtime` và LAN `.runtime\lan`. Mật khẩu/dữ liệu khác nhau; dùng đúng profile và URL8446. Không cài agent trên máy chính cho bài thử này.

## B. Tải và tạo Windows máy ảo

1. Trên máy chính tải **Windows Installer** của VirtualBox từ https://www.oracle.com/virtualization/technologies/vm/downloads/virtualbox-downloads.html. Chạy installer; nếu cần khởi động lại thì lưu công việc trước, sau đó mở lại server ở chặng A. ExtensionPack không cần cho lab cơ bản này.
2. Tải Windows 11 ISO **x64** từ nguồn Microsoft. Bản đánh giá90ngày: https://www.microsoft.com/en-us/evalcenter/evaluate-windows-11-enterprise (đăng ký theo trang Microsoft). ISO là một tệp, không mở setup.exe để cài đè Windows máy chính. Lưu ISO ở ổ D để đủ dung lượng.
3. Mở VirtualBox → New. Tên chính xác **KidSafe-Child01**; folder `D:\VirtualMachines`; chọn ISO vừa tải; OS Windows 11 64bit. Tắt tùy chọn Unattended Installation nếu muốn làm theo màn hình cài từng bước.
4. Cấp RAM4096 MB, CPU2, đĩa ảo VDI 80 GB cấp phát động; bật UEFI/TPM 2.0 theo lựa chọn Windows 11 của wizard, Secure Boot khi cấu hình hỗ trợ. Ổ 80 GB là file đĩa ảo cho guest; không chọn phân vùng C/D của host làm raw disk.
5. Vào Settings → Network: chỉ Adapter 1 bật, **Attached to NAT**, Cable Connected bật. Không chọn NAT Network/Bridged/Host-only cho hướng dẫn này.
6. Khi máy ảo **đang tắt hẳn**, chạy PowerShell trên **máy chính**:

```powershell
& 'C:\Program Files\Oracle\VirtualBox\VBoxManage.exe' modifyvm 'KidSafe-Child01' --nat-localhostreachable1 on
```

Lệnh cho phép guest dùng10.0.2.2 để tới localhost của host. Đây là tùy chọn NAT của VirtualBox, không phải IP Wi-Fi và không phải tắt firewall. Nếu không tìm VBoxManage, kiểm đường dẫn cài VirtualBox thực; nếu báo máy đang chạy thì ShutDown guest rồi thử lại.

7. Nhấn Start, làm theo Windows Setup bên trong cửa sổ VM. Chọn cài vào ổảo80GB. Làm theo yêu cầu tài khoản/đăng ký của bản Windows chính thức, không dùng công cụ bypass. Hoàn tất đến desktop Windows trong VM, dùng tài khoản admin lab để cài đặt. Phím **Ctrl bên phải** là phímHost mặc định để thoát giữ bàn phím/chuột về host.
8. Trong guest tạo thêm user **kidsafe-child**, loại **Standard user**: Settings → Accounts → Other users → Add account → tùy chọn tạo user cục bộ khi Windows cung cấp. Tài khoản admin lab vẫn giữ riêng. Đăng nhập kidsafe-child một lần cho Windows hoàn tất profile, sau đó Sign out và trở lại admin guest.

Nếu VM báo lỗi ảo hóa/TPM/không khởi động, giữ nguyên thông báo để chẩn đoán theo máy thật, không giả định đổi BIOS/tắt tính năng bảo mật sẽ giải quyết. Không nói VM đã chạy chỉ từ bộ cấu hình ở trên.

## C. Đưa source và CA công khai vào máy ảo

Codex chuẩn bị thư mục **D:\DoAN MMT\.runtime\vm\transfer** gồm KidSafe-source.zip, ca.crt và server-public.json. Nếu cần cập nhật sau này, trên host:

```powershell
Set-Location 'D:\DoAN MMT'
.\.venv\Scripts\python.exe -m scripts.export_public_config --config '.runtime\vm\lab.json'
New-Item -ItemType Directory -Force '.runtime\vm\transfer' | Out-Null
Copy-Item -LiteralPath 'releases\KidSafe-source.zip' -Destination '.runtime\vm\transfer\KidSafe-source.zip'
Copy-Item -LiteralPath '.runtime\vm\public\ca.crt' -Destination '.runtime\vm\transfer\ca.crt'
Copy-Item -LiteralPath '.runtime\vm\public\server-public.json' -Destination '.runtime\vm\transfer\server-public.json'
```

Chỉ chia sẻ thư mục transfer, không chia sẻ toàn bộ .runtime vì có privatekeys.

1. Guest đang ở desktop với admin lab: trong menu cửa sổ VM chọn Devices → Insert Guest Additions CD image. Trong guest mở This PC → đĩa VirtualBox Guest Additions → VBoxWindowsAdditions.exe, cài rồi restart guest.
2. Tắt guest, mở Settings của VM → Shared Folders → Add: Folder Path là thư mục transfer ở trên, Folder Name **KidSafeTransfer**, bật Read-only và Auto-mount; chọn Make Permanent nếu có.
3. Khởi động guest, đăng nhập admin. Mở File Explorer trong guest, gõ `\\VBOXSVR\KidSafeTransfer`. Copy ba file vào **C:\KidSafe-transfer** trong guest. Giải nén KidSafe-source.zip vào **C:\KidSafe-source**, sao cho có `C:\KidSafe-source\agent`.
4. Trong guest tải Python 64-bit từ https://www.python.org/downloads/windows/. Python 3.11+, dự án đã kiểm với 3.12. Chọn Customize installation, Install for all users và cài dưới Program Files. Ví dụ `C:\Program Files\Python312\python.exe`; kiểm đường dẫn thật. Bộ cài agent từ chối Python dưới AppData vì user trẻ có thể ghi mã ở đó.

## D. Ghép agent chỉ bên trong Windows máy ảo

1. Guest mở PowerShell, chạy:

```powershell
Test-NetConnection 10.0.2.2 -Port 8446
```

Phải TcpTestSucceeded=True. Nếu False: serverhost còn chạy? Adapter 1 có đúngNAT? Lệnh localhostreachable đã chạy lúc VM tắt? Chưa cài agent nếu chưa kết nối được. `localhost` bên trong guest là chính guest, nên không dùng URLlocalhost cho agent.

2. Guest mở PowerShell **Run as administrator**. Các lệnh ở phần này chỉ chạy trong guest:

```powershell
Import-Certificate -FilePath 'C:\KidSafe-transfer\ca.crt' -CertStoreLocation 'Cert:\LocalMachine\Root'
Get-NetAdapter | Where-Object Status -eq 'Up' | Format-Table Name,ifIndex,InterfaceDescription
```

Lệnh import giúp browser của các user guest tin CA lab. Ghi ifIndex của Ethernet NAT. Ví dụ12 trong lệnh sau phải thay bằng ifIndex thật của **guest**, không lấy card Wi-Fi của host.

3. Host mở web parent https://localhost:8446/login → hồ sơ con → Thiết bị & ghép đôi → Tạo mã → đồng ý. Mã 8 ký tự hạn 10 phút, tạo sát lúc cài; chuẩn bị Python/source/mạng xong trước.
4. Guest PowerShell Admin:

```powershell
Set-Location 'C:\KidSafe-source'
Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned
$public = Get-Content -Raw 'C:\KidSafe-transfer\server-public.json' | ConvertFrom-Json
$code = Read-Host 'Nhap ma ghep 8 ky tu tu web tren may chinh'
.\agent\scripts\Install-ChildLab.ps1 -ChildLab `
  -Python 'C:\Program Files\Python312\python.exe' `
  -ServerUrl 'https://10.0.2.2:8446' `
  -CaFile 'C:\KidSafe-transfer\ca.crt' `
  -CertificatePin $public.certificate_pin `
  -SigningPublicKey $public.signing_public_key `
  -EnrollmentCode $code `
  -ChildUser "$env:COMPUTERNAME\kidsafe-child" `
  -InterfaceIndices 12
```

Nếu script của ZIP bị chặn do tải Internet, chỉ bỏ chặn các file của gói KidSafe có nguồn đã kiểm: `Get-ChildItem -LiteralPath . -Recurse -Filter *.ps1 | Unblock-File` khi đang ở đúng C:\KidSafe-source. Không đổi execution policy toàn máy. Nếu installer báo lỗi thì dừng để chẩn đoán, không lặp ghi đè/xóaProgramData.

5. Cài xong Sign out admin **trong guest**, đăng nhập kidsafe-child. KidSafe phải có icon trong taskbar/vùng icon ẩn. Host web parent phải thấy thiết bị kết nối, version nhận đúng. Không có icon thì không coi enforcement đã chạy.
6. Muốn con dùng web, parent tạo tài khoản web của con trong trang thiết bị. Trong guest con mở **https://10.0.2.2:8446/login** bằng tài khoản web đó. Tài khoảnweb khác tài khoản Windows kidsafe-child.

## E. Thử từng việc và dừng đúng cách

- Host parent Cộng 15 → pending → guestACK. Khóa ngay chỉ khóa guest; host vẫn dùng được. Mở khóa cấp ngoại lệ tối đa 15 phút, con tự đăng nhập Windows nếu đang khóa.
- Quota 3 phút nên đặt trước khi ghép máy đầu; hạn mức giảm sau cấp quyền offline có thể cần máy trả ACK và thời điểm hiệu lực, không sửa DB để né. Cảnh báo còn 1 phút nằm trong quota theo phương án tạm D020.
- Chặn example.org và miền con an toàn; thử app an toàn có hash thật. Không dùng miền người lớn. Không thực hiện lệnh cài agent/đổi DNS trên host.
- Thử mất mạng bằng bỏ Cable Connected của **card VM** rồi bật lại; không tắt Wi-Fi host để giả nghiệm thu riêng guest.
- Gỡ/restore trong guest Admin: `& 'C:\Program Files\KidSafe\agent\scripts\Uninstall-ChildLab.ps1' -ChildLab`.
- Tắt guest bằng Start→Power→Shutdown. Host dừng server bằng Ctrl+C trong cửa sổ server. Những lần sau: bật server host cùng lệnh A, bật VM, đăng nhập user trẻ. Một VM không chứng minh quota chung giữa hai máy trẻ; mụcđó cầnVM thứ hai khi đủtài nguyên.

Nếu có lỗi: chụp nguyên thông báo, không chụp mật khẩu/token/lab.json; ghi rõ đang ở host hay guest và bước nào. Bằng chứng khóa/app/DNS/SCM/ACL vẫn phải lấy từ guest Windows hoạt động thật; hướng dẫn này chưa thay kết quả nghiệm thu.

Nguồn tham khảo: [VirtualBox](https://www.oracle.com/virtualization/technologies/vm/downloads/virtualbox-downloads.html), [NAT và10.0.2.2](https://docs.oracle.com/en/virtualization/virtualbox/7.2/user/networkingdetails.html), [localhostreachable](https://docs.oracle.com/en/virtualization/virtualbox/7.2/user/vboxmanage.html), [Windows evaluation](https://www.microsoft.com/en-us/evalcenter/evaluate-windows-11-enterprise).
