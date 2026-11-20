# KidSafe Windows agent

**D050:** `child_window.py` là cửa sổ Windows native trong cùng PID tray, không cần tài khoản web. Hiển thị giờ còn trên máy, quỹ giải trí, hoạt động đã đồng bộ, 10 thay đổi gần nhất và nút xin 5/10/15 phút. Dùng IPC có xác thực hiện hành, không đưa bearer của thiết bị vào UI. Đóng cửa sổ thu về tray; mở từ icon hoặc Start. Cửa sổ preview có thể thử an toàn bằng `python -m agent.child_window --preview`; đây chỉ là dữ liệu mẫu, không chạy service/lease/enforcement. [Hướng dẫn](../docs/CHILD_APP.md)

D036 dùng `app_groups.py` để đối chiếu tên hoặc SHA-256, áp dụng trạng thái khóa, giờ và quỹ nhóm. `entertainment.py` ghi số giây foreground theo nhóm và vào quỹ giải trí khi nhóm chọn chế độ đó. Cập nhật server trước agent. Sau đó cập nhật agent trên lab trẻ để áp dụng quy tắc nhóm. Tệp được đổi tên vẫn nhận diện qua SHA-256. Dữ liệu giữa nhiều máy có độ trễ heartbeat và dùng lại số đã nhận trong ngày khi mất mạng.

D035: `entertainment.py` giữ bộ đếm foreground theo ngày của các tên `.exe` phụ huynh chọn. Agent bản mới chặn nhóm này khi thời lượng cục bộ cộng tổng từ máy khác đã đồng bộ đạt hạn mức. Chặn qua AppMonitor có thông báo và xác nhận đã hiển thị trước khi đóng tiến trình. Khi mất kết nối, agent dùng số đã nhận trong ngày và tiếp tục cộng thời gian cục bộ. Mức vượt quỹ do các máy dùng đồng thời phụ thuộc độ trễ đồng bộ. Cập nhật và khởi động lại agent trên lab trẻ để áp dụng. Kiểm thử Windows thật vẫn cần thực hiện trên lab.

Service LocalSystem + tray nhìn thấy trong phiên user trẻ, Python 3.11+ x64. Lõi đã kiểm thử; **chưa nghiệm thu cài service, ACL, tray/logon/logoff, khóa máy và đổi DNS trên máy trẻ riêng**. Không chạy enforcement trên host làm việc để thay nghiệm thu lab.

`runtime.py` nối policy Ed25519, counter monotonic bền vững, heartbeat 30 giây, WebSocket pin TLS trước bearer, queue SQLite WAL, DNS UDP/TCP IPv4/IPv6 và app monitor. Import module không tự thay đổi host.

## Cài trên máy trẻ lab

Ưu tiên [bộ cài Windows x64](../docs/WINDOWS_SETUP.md) để ghép đôi bằng tệp kết nối và mã 10 phút. Phần bên dưới dành cho quy trình cài từ mã nguồn.

Yêu cầu Windows 10/11 x64, Python máy-wide trong Program Files (trẻ không sửa được), tài khoản trẻ **user thường**, server TLS LAN riêng, CA/pin/public key và mã ghép 8 ký tự. Windows 11 là môi trường phát triển; Windows 10 chưa thử. Cần Internet để pip lấy dependency đã khóa.

Trong PowerShell Administrator **trên máy trẻ lab**:

```powershell
& 'D:\KidSafe-source\agent\scripts\Install-ChildLab.ps1' `
  -ChildLab -Python 'C:\Program Files\Python312\python.exe' `
  -ServerUrl 'https://192.168.1.10:8443' -CaFile 'D:\lab-ca\ca.crt' `
  -CertificatePin '<SHA256 DER certificate>' -SigningPublicKey '<Ed25519 base64>' `
  -EnrollmentCode '<8 characters>' -ChildUser 'LABPC\child' -InterfaceIndices 12
```

Chọn adapter bằng `InterfaceIndices`; bộ cài không đoán/chỉnh tất cả adapter. Script tạo venv trong Program Files, cài `requirements.lock`, ACL code/interpreter chỉ admin/SYSTEM ghi, thư mục service chỉ admin/SYSTEM truy cập; trẻ chỉ đọc config tray (token IPC, port, cờ lab). Access/refresh dùng DPAPI theo danh tính service; enrollment chạy dưới SYSTEM. Fingerprint ngẫu nhiên, không thu serial hoặc tên user vào event.

Bộ cài đăng ký service + SCM recovery (5/15/60 giây), tác vụ user hiện tray lúc logon, tác vụ SYSTEM khởi động service lúc trẻ logon. Không nhận lease hợp lệ trong 15 giây khởi động hoặc mất lease quá 5 giây thì dừng enforcement/DNS; kết thúc bình thường do thiếu tray không bị SCM ép chạy ẩn. Tray chờ service tối đa 60 giây khi vẫn hiện icon. Không chạy UI trong Session 0.

IPC mặc định từ chối peer: ngoài bearer token, service đối chiếu **PID thực sở hữu kết nối TCP**, exact interpreter/command line `pythonw.exe -I <protected tray.py> --config <protected config>`, username, token không thuộc Administrators và session khác 0. Windows venv redirector và base interpreter đều được kiểm. `-I` loại user site/PYTHONPATH; pythonw không tạo console phụ nhưng tray vẫn bắt buộc nhìn thấy. Điều này phụ thuộc ACL code/interpreter/dependency; vẫn cần kiểm thử child giả IPC thực tế trong lab.

## Hành vi đã lập trình

Counter chỉ trừ khi lịch/quota cho phép, phiên chưa khóa và idle không quá 5 phút. 60 giây lưu bài nằm trong quota theo D020 tạm thời. Cộng giờ giữ lịch. Theo D038, mở khóa mới dùng bộ đếm ngoại lệ riêng và kết thúc ở mốc nửa đêm đã ký hoặc khi nhận lệnh Khóa máy ngay. Agent mới giữ mốc tuyệt đối qua reboot. Agent cũ vẫn áp dụng tối đa 15 phút và cần cập nhật để thực thi mốc mới. Usage và command/ACK ghi transaction trước ACK. Chuyển ngân sách có hiệu lực từ ngày sau, sau ACK giảm bền vững của máy cho.

Sau 3 ngày offline vẫn giữ lịch/quota cuối, không tự mở chặn. Reboot lệch đồng hồ hơn 300 giây mà thiếu nguồn thời gian đáng tin sẽ chờ server (`clock_uncertain`); đây là lựa chọn bảo thủ, chưa phải secure clock offline. Lệch giờ được lưu vào `security_audit` cục bộ (chỉ drift, retention 90 ngày), tách khỏi đúng 7 trường/9 loại activity event; không tự thêm loại event thứ mười. Worker gap/suspend hơn 5 giây không tính là thời gian dùng. Chưa đo một giờ thật để kết luận sai số ±30 giây/giờ.

App monitor chỉ xét tiến trình user trẻ, nhận diện tên + SHA-256; đổi tên không qua hash. Tiến trình lõi shell trong thư mục Windows được bảo vệ khỏi kết thúc để tránh phá phiên. Allowlist cần hash, không cho tên giả mạo tự được phép. Khi bị chặn, tray hiện hộp thoại Windows; service đợi ACK cửa sổ đang nhìn thấy rồi mới kết thúc PID đã kiểm path/create-time. Thiếu ACK 4 giây thì dừng enforcement thay vì chặn âm thầm. Thời lượng báo cáo theo app foreground, loại idle/khóa; không lấy nội dung cửa sổ, URL, ảnh hoặc phím bấm.

DNS bind `127.0.0.1:53` + `[::1]:53`, UDP/TCP, suffix đúng ranh giới, cache TTL hữu hạn, upstream cố định, SafeSearch và bỏ HTTPS/SVCB hints trên host SafeSearch. Script DNS lưu GUID, IPv4/IPv6, static/DHCP trước đổi adapter; runtime chỉ áp loopback sau có tray + resolver, hoàn nguyên khi dừng và trước lần phục hồi sau kill. Adapter mất/restore lỗi giữ snapshot để phục hồi, không báo thành công. Admin/VPN/DoH/IP trực tiếp vẫn cần thử; proxy không tự chứng minh chặn mọi đường vòng.

Nhánh NC D018 mặc định tắt: thêm `-DisableBrowserDoh` khi cài lab sẽ bật NXDOMAIN canary + endpoint DoH phổ biến và policy Chrome/Edge/Firefox. `Manage-LabBrowserPolicy.ps1` snapshot từng giá trị registry (có/không, kiểu, nội dung) trước sửa, khôi phục khi service dừng/gỡ; không xóa policy khác. Mã dựa trên tài liệu chính thức [Chrome](https://chromeenterprise.google/policies/#DnsOverHttpsMode), [Edge](https://learn.microsoft.com/en-us/deployedge/microsoft-edge-policies/DnsOverHttpsMode), [Firefox](https://firefox-admin-docs.mozilla.org/reference/policies/dnsoverhttps/), đối chiếu ngày 2026-11-04. Cần reload/restart trình duyệt và kiểm `chrome://policy`, `edge://policy`, `about:policies` trong lab; chưa khẳng định đã thử bật DoH thật. User thường không được đổi cấu hình adapter; truy vấn trực tiếp `nslookup example.com 8.8.8.8` vẫn có thể vượt proxy vì chưa có WFP/firewall cưỡng chế. Đây là giới hạn đã ghi rõ, không tuyên bố chống đổi DNS hoàn toàn.

## Gỡ và phục hồi

Ưu tiên gỡ thiết bị trong dashboard khi online để thu hồi token/gửi xóa cache. Sau đó, Administrator trên máy lab:

```powershell
& 'C:\Program Files\KidSafe\agent\scripts\Uninstall-ChildLab.ps1' -ChildLab
```

Script dừng/xóa tác vụ, dừng/gỡ service và hoàn nguyên DNS. Không xóa đệ quy thư mục; metadata bảo vệ còn lại được giữ để rà soát/phục hồi. Đây là gỡ quản trị, chưa phải NC gỡ bằng mật khẩu phụ huynh. Khôi phục DNS riêng bằng `Manage-LabDns.ps1 -Action Restore -Snapshot <snapshot> -InterfaceIndices '12'`.

## Kiểm chứng

```powershell
.venv\Scripts\python.exe -m pytest tests/agent -q --basetemp=.tmp/pytest-agent
```

Test loopback dùng cổng cao động, không sửa DNS/firewall/SCM, không khóa host hoặc kết thúc app. Parse PowerShell không phải đã cài thành công. Độ trễ end-to-end <5 giây, SafeSearch browser, 50/20 miền, Wireshark, recovery/ACL/logoff, cài Windows sạch ≤15 phút vẫn cần bằng chứng lab theo R-A02/03/06, R-F1, R-F2, R-F5-07/09, M1/M3–M6 và R-D09.
