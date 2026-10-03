# Threat Model cho hàm json_search() theo STRIDE

## 1. Phạm vi phân tích

Hàm json_search() được sử dụng để tìm kiếm dữ liệu trong JSON trả về từ một API giám sát hạ tầng mạng.

Hàm phục vụ ba nhóm người dùng:
- admin
- operator
- viewer

Mục tiêu của threat model là xác định các nguy cơ có thể xảy ra khi hàm json_search() tìm kiếm và trả về dữ liệu mà không kiểm tra quyền truy cập.

## 2. Actors

### Admin

Admin là quản trị viên hệ thống. Có quyền truy cập các thông tin cấu hình và dữ liệu nhạy cảm.

### Operator

Operator là nhân viên vận hành hệ thống mạng. Có quyền truy cập một số thông tin phục vụ quản trị và giám sát.

### Viewer

Viewer là người dùng chỉ có quyền xem các thông tin giám sát thông thường.

## 3. Assets cần bảo vệ

Các tài sản quan trọng xuất hiện trong dữ liệu JSON gồm:

- apiKey: thông tin xác thực nhạy cảm.
- managementIpAddress: địa chỉ IP quản trị của thiết bị.
- issueSummary: thông tin mô tả sự cố mạng.

Trong đó, apiKey là thông tin có mức độ nhạy cảm cao nhất vì liên quan đến thông tin xác thực.

## 4. Trust Boundary

Trust boundary nằm giữa người dùng gọi hàm json_search() và dữ liệu JSON do API giám sát mạng cung cấp.

Nếu json_search() chỉ nhận key rồi trả về dữ liệu mà không kiểm tra role, người dùng có quyền thấp có thể truy cập thông tin dành cho role có quyền cao hơn.

## 5. Phân tích theo STRIDE

### S - Spoofing

**Nguy cơ:** Người dùng có thể giả mạo một role có quyền cao hơn nếu giá trị role được truyền trực tiếp mà không được xác thực.

**Ví dụ:** Một viewer tự khai báo role="admin" để yêu cầu đọc apiKey.

### T - Tampering

**Nguy cơ:** Dữ liệu JSON hoặc chính sách phân quyền có thể bị thay đổi trái phép, làm cho hàm trả về dữ liệu không đúng với chính sách.

**Ví dụ:** Danh sách role được phép đọc apiKey trong policy.py bị sửa để bổ sung viewer.

### R - Repudiation

**Nguy cơ:** Không có cơ chế ghi log việc người dùng tìm kiếm hoặc truy cập các trường nhạy cảm, do đó khó xác định ai đã thực hiện một yêu cầu truy cập.

Logging và audit không nằm trong phạm vi chức năng json_search() hiện tại.

### I - Information Disclosure

**Nguy cơ:** Nếu json_search() không kiểm tra role, người dùng có thể đọc các trường nhạy cảm mà họ không được phép truy cập.

**Ví dụ:** viewer gọi:

json_search("apiKey", data, role="viewer")

và nhận được giá trị apiKey.

**Tác động:** Làm lộ thông tin xác thực hoặc thông tin quản trị của hệ thống.

**Biện pháp:** Kiểm tra role theo policy.py trước khi trả về kết quả.

### D - Denial of Service

**Nguy cơ:** Một JSON có cấu trúc lồng quá sâu hoặc kích thước rất lớn có thể khiến hàm đệ quy tiêu tốn nhiều tài nguyên hoặc vượt quá giới hạn recursion.

### E - Elevation of Privilege

**Nguy cơ:** Người dùng có quyền thấp có thể truy cập dữ liệu chỉ dành cho role có quyền cao hơn nếu json_search() không thực hiện kiểm tra quyền.

**Ví dụ:** viewer truy cập managementIpAddress hoặc apiKey dù không được policy cho phép.

**Biện pháp:** Mọi kết quả tìm kiếm phải được kiểm tra theo role trước khi trả về cho người gọi.
