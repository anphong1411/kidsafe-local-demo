# Kế hoạch kiểm thử và bằng chứng nghiệm thu

Trạng thái: **chưa có test được viết/chạy, chưa có số đo hoặc kết quả đạt**. Pytest là đề xuất cho stack Python; sẽ khóa công cụ/phiên bản khi triển khai. Các test phải kiểm hành vi, đầu vào sai và biên; không thêm test trùng lặp chỉ để đạt số lượng.

## Kế hoạch unit test tối thiểu

| Mã | Hành vi và biên cần kiểm | Yêu cầu |
| --- | --- | --- |
| U01 | Quota ngày thường/cuối tuần và rollover ngày theo timezone đã chốt | R-F1-01 |
| U02 | Lịch 7×48, biên ô 30 phút, ma trận sai kích thước bị từ chối | R-F1-02 |
| U03 | Không tính thời gian máy khóa | R-F1-03 |
| U04 | Idle trước/đúng/sau 5 phút theo semantics đã chốt | R-F1-03 |
| U05 | Monotonic không tăng quota khi wall clock lùi 3 giờ | R-F1-05, M6 |
| U06 | Warning 10/5/1; D020 tạm: 60 giây lưu bài trong quota, quota 3 phút khóa phút 3; quota ngắn hơn mốc cảnh báo | R-F1-04, D020 chưa được giảng viên xác nhận |
| U07 | SHA-256 nhận diện executable sau đổi tên, file thay nội dung được phát hiện | R-F2-01 |
| U08 | Rule app allow/block và precedence đã chốt | R-F2-01 |
| U09 | Domain exact/subdomain không khớp nhầm miền có đuôi giống | R-F2-03 |
| U10 | Chuẩn hóa domain/IDN/case/trailing dot/suffix, không lưu URL đầy đủ | R-F3-01 |
| U11 | Policy integrity đúng/sai, version replay/rollback theo contract | R-F4-03 |
| U12 | Event 7 trường/9 type, extra field/type sai/duration không hợp lệ bị từ chối | R-F3-01 |
| U13 | Enrollment expiry biên 10 phút, mã sai/dùng lại theo contract | R-P01 |
| U14 | Access hết hạn 15 phút, device mismatch và revoke | R-F5-04 |
| U15 | Password length, lockout lần thứ 5, mở lại sau 15 phút | R-F5-01 |
| U16 | Query ownership không cho parent A đọc/ghi trẻ của B | R-F5-06 |
| U17 | Idempotency replay không nhân đôi event và command cộng giờ | R-P04 |
| U18 | Retention biên 90 ngày, không xóa nhầm bản ghi mới | R-F3-04 |
| U19 | AES-GCM tag sai bị từ chối, không tái dùng nonce trong thiết kế đã chọn | R-F5-05 |
| U20 | Trước/đúng/sau 3 ngày offline vẫn giữ policy/quota/lịch cuối, không tự cấp thêm giờ | R-P05 |
| U21 | Quota chung chia trước hai máy: đồng thời online/offline, reconnect/reboot không nhân đôi ngân sách | R-F4-01, D013/D015 |
| U22 | Chuyển phần ngân sách: máy cho chưa ACK, ACK mất, retry/crash; tổng đã dùng + quyền còn lại không vượt quota và grant rõ ràng | D015 |
| U23 | Ngoại lệ mở khóa ngoài lịch 15 phút, hết hạn trở về lịch/quota; replay/reboot không gia hạn; audit đúng phạm vi | D016, R-F4-04 |
| U24 | Cộng 15 tăng quota chung một lần, không đổi lịch; Mở khóa khi quota hết cấp ngoại lệ hữu hạn, không nhân theo số thiết bị | D017 |
| U25 | Khóa ngay hủy ngoại lệ; lệnh cũ/replay không phục hồi; chặn app/domain vẫn áp khi có ngoại lệ | D017 |

## Kịch bản tích hợp dự kiến, đề yêu cầu ít nhất 5

| Mã | Luồng thật cần kiểm | Kỳ vọng |
| --- | --- | --- |
| I01 | Parent đăng nhập → tạo mã → agent enroll → heartbeat/policy | Có consent, device/tokens đúng hạn, cache đã xác minh |
| I02 | Parent đổi quota/lịch → agent áp → warning/grace/lock | Policy ≤60 giây; ngoài lịch ≤5 giây; timeline quota theo cách hiểu đã chốt |
| I03 | Trẻ xin giờ → duyệt → WebSocket cộng 15 → retry cùng command | Áp <5 giây khi online; cộng đúng một lần; audit/trẻ xem đúng |
| I04 | App đổi tên + DNS subdomain + SafeSearch | App nhận diện/chặn có lý do; DNS đạt mẫu số đã làm rõ; nslookup và trình duyệt |
| I05 | Mất mạng/server down → dùng cache/đệm → reconnect; qua ngưỡng 3 ngày trên hai máy | Counter tiếp tục; không đếm trùng; giữ policy cuối sau 3 ngày; tổng quota theo trẻ không vượt do cấp trùng; đo recovery |
| I06 | Xóa dữ liệu online/offline → agent reconnect → batch cũ gửi lại | Server/cache được xóa, pending/ACK đúng, không tái nhập dữ liệu cũ |
| I07 | Hai gia đình; child-view; CSRF; logout; token/pin sai | Không IDOR, mọi ghi có CSRF, logout hủy, pin sai từ chối |
| I08 | User thường thử sửa cache/config/IPC; kill service/tray | ACL/IPC chặn; recovery đo được; mất icon không còn agent chạy ẩn |
| I09 | Chia 90 phút A60/B30; A offline, thử chuyển giờ sang B rồi reconnect/ACK/retry | Không cấp lại phần A còn có quyền dùng; trạng thái chờ rõ; chuyển hợp lệ chỉ có tác dụng một lần |
| I10 | Parent Mở khóa ngoài lịch/quota hết → ngoại lệ 15 phút → hết hạn hoặc Khóa ngay; gửi lại lệnh cũ | Audit/giờ ngoại lệ rõ; hết hạn quay về lịch/quota; Khóa ngay hủy; replay không hồi sinh; app/domain vẫn chặn; tổng giờ không nhân theo số máy |
| I11 (NC) | Bật DoH Chrome, query canary/endpoint, đổi DNS 8.8.8.8 rồi rollback | Ghi kết quả thật và giới hạn từng cách; NC ưu tiên sau BB, không thay M3 BB |

Unit dùng mock/clock kiểm thử có kiểm soát là hợp lệ nhưng không thay Windows service, DNS, tray và TLS chạy thực trong nghiệm thu tích hợp.

## Các phép nghiệm thu bắt buộc ngoài số lượng test

| Nhóm | Kịch bản | Ngưỡng/bằng chứng |
| --- | --- | --- |
| V-F1 | Quota 3 phút; D020 tạm: nhắc lưu bài lúc phút 2, khóa phút 3; ngoài lịch; warning 10/5/1 | Video/log thời gian; ghi cách hiểu ân hạn chưa được giảng viên xác nhận, cập nhật khi có phản hồi; ngoài lịch ≤5 giây |
| V-COUNT | So đồng hồ bấm tay đủ 1 giờ; có lock/idle; lùi clock 3 giờ | Sai số ≤±30 giây/giờ; không tăng quota; có log; dùng lab, khôi phục giờ sau thử |
| V-DNS | Tập 50 miền được định nghĩa, 20 giáo dục; subdomain | Chặn ≥95%, false positive 0/20; báo tử/mẫu và expected labels; chưa áp tùy tiện 50/60 |
| V-SAFE | SafeSearch qua nslookup và trình duyệt | Ảnh query/answer và trạng thái search; không chỉ log “đã bật” |
| V-REMOTE | Thao tác dashboard → agent thực thi | Policy ≤60 giây, urgent <5 giây; đo start/end thống nhất, không chỉ server ACK |
| V-PRIV | Event schema/90 ngày/xóa đồng bộ | DB/API/cache inspect; không URL; pending deletion rõ; không upload lại sau xóa |
| V-WEB | Mobile/desktop; child-view dữ liệu/audit | Dùng thật trên điện thoại hoặc browser mobile viewport rồi xác minh thiết bị thực khi có; không vượt quyền |
| V-UI-REF | Sau G-UI, đối chiếu UI_DESIGN_BRIEF/ảnh tham khảo với parent/child/tray thực | Bố cục rõ và phù hợp trẻ, chữ tiếng Việt đọc được, tiến trình đúng số thật, quota chung/phần máy/ngoại lệ phân biệt; pending/ACK/offline/error/0 trung thực; app/domain rules và quyền vẫn đúng; chụp và kiểm desktop/tablet/mobile |
| V-SETUP | Windows sạch, chỉ có điều kiện nền đã khai báo | Cài chạy ≤15 phút; giữ ghi thời gian/các bước/phiên bản; gỡ/restore DNS thành công |

## M1–M6

Chi tiết cấu trúc trong REPORT_PLAN. Mỗi phép M4 có ít nhất 30 mẫu riêng, gồm CPU/RAM idle và peak; DNS có/không agent với cùng bộ dữ liệu và cache conditions được công bố; policy end-to-end. Ghi raw samples, cách lấy percentile, môi trường và load. Không dùng một tập 30 mẫu chung cho mọi phép đo.

M3 sẽ thử cả 9 kỹ thuật đề liệt kê: đổi DNS, DoH, DoT, VPN/proxy, IP trực tiếp, Safe Mode, boot USB, tài khoản Windows khác, kill process. Ít nhất 7 phải có kết quả thực; không có điều kiện thì ghi chưa thử, không tự điền “đã chặn”.

## Quản lý bằng chứng

Khi triển khai tạo `docs/evidence/` và `docs/evidence/INDEX.md`. Mỗi record gồm ID yêu cầu/test, ngày, máy/OS/version, cấu hình, bước chạy, expected/actual, thời gian, ảnh/log/capture/raw data và kết luận. Không chụp token/key/mật khẩu thật hoặc dữ liệu trẻ thật. Giữ ảnh kết quả chạy ≥15 unit + ≥5 integration để nộp.

Chỉ đánh dấu **đạt** khi có kết quả và evidence thật. Test thất bại phải được sửa hoặc ghi còn thiếu; snapshot/mô phỏng không được ghi thành thử máy thật. Hiện mọi phép kiểm chứng sản phẩm trong file này đều **chưa chạy**.
