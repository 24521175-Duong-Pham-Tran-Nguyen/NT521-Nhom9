# Security Requirements cho hàm json_search()

Các Security Requirements được xây dựng từ Threat Model theo framework STRIDE, tập trung xử lý hai nhóm threat chính:

- Information Disclosure
- Elevation of Privilege

## SR-01 - Bảo vệ apiKey

Threat liên quan:
- Information Disclosure
- Elevation of Privilege

Yêu cầu: Hàm json_search() chỉ được trả về giá trị của trường apiKey khi role của người dùng là admin. 
Kết quả nếu role không phải admin, hàm phải trả về danh sách rỗng.

Ví dụ: json_search("apiKey", data, role="viewer")
Kết quả mong đợi: []

## SR-02 - Bảo vệ managementIpAddress

Threat liên quan:
- Information Disclosure
- Elevation of Privilege

Yêu cầu: Chỉ các role admin và operator được phép đọc managementIpAddress. Role viewer không được phép nhận giá trị của trường này.

Ví dụ: json_search("managementIpAddress", data, role="viewer")
Kết quả mong đợi: []

## SR-03 - Cho phép truy cập issueSummary

Yêu cầu: Các role admin, operator và viewer đều được phép đọc issueSummary theo chính sách phân quyền.

## SR-04 - Từ chối mặc định khi không đủ quyền

Threat liên quan:
- Information Disclosure
- Elevation of Privilege

Yêu cầu:
Nếu key thuộc danh sách được bảo vệ trong policy.py nhưng role của người dùng không nằm trong danh sách được phép, json_search() không được trả về giá trị của key đó. 
Kết quả phải là một danh sách rỗng.

## SR-05 - Áp dụng kiểm tra quyền trong toàn bộ quá trình đệ quy

Threat liên quan:
- Information Disclosure
- Elevation of Privilege

Yêu cầu: Kiểm soát truy cập phải được áp dụng đối với tất cả kết quả tìm thấy, kể cả khi key nằm trong dictionary hoặc list lồng nhiều cấp. Không được phép có trường hợp một kết quả nằm sâu trong cấu trúc JSON bỏ qua việc kiểm tra quyền.

## SR-06 - Kiểu dữ liệu trả về nhất quán

Yêu cầu: json_search() luôn phải trả về kiểu list.
Trong các trường hợp:
- không tìm thấy key;
- role không đủ quyền;
thì hàm phải trả về danh sách rỗng.
