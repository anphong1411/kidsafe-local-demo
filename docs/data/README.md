# Dữ liệu phân loại mẫu

`domain_categories.csv` là bảng gợi ý thủ công để trình bày sáu nhóm, không phải dịch vụ đánh giá độ an toàn của website. Chưa xác minh toàn bộ miền còn hoạt động hay mọi nội dung trên miền phù hợp trẻ em. Không truy cập nội dung người lớn để xây bảng này.

Nhóm `age_inappropriate` trong bộ mẫu dùng các trang mua bán có rủi ro trẻ tự giao dịch, **không có nghĩa các website đó là nội dung người lớn**. Social và nhóm này được đề xuất chặn mặc định tuổi 6–11; phụ huynh cần rà soát. Một miền giáo dục lớn có thể chứa nội dung dành cho người lớn tuổi hơn; nhãn giáo dục không bảo đảm toàn bộ nội dung thích hợp. Các miền con là mục lọc riêng, không được tính là website độc lập trong báo cáo độ bao phủ.

Nguồn: danh sách minh họa do Codex biên soạn từ tên tổ chức/dịch vụ công khai; `review_status=provisional_manual` chủ động giữ trạng thái chưa nghiệm thu. Script tái tạo: `python -m scripts.build_domain_data`. Không dùng bảng này làm bằng chứng đạt phép đo DNS 50 miền hoặc 20 miền giáo dục: các phép đo phải có tập expected/actual riêng và kết quả truy vấn thật. Cần kiểm tra thủ công nguồn/category trước khi nộp; không tuyên bố đạt R-F2-04 từ số dòng đơn thuần.
