TÀI LIỆU THIẾT KẾ HỆ THỐNG
PROJECT: MẠNG LƯỚI GIA ĐÌNH (FAMILY NETWORK SYSTEM)

====================================================================

Mục tiêu hệ thống

Hệ thống cho phép người dùng tạo và quản lý nhiều mạng lưới gia đình độc lập. Trong mỗi mạng lưới có nhiều gia đình. Trong mỗi gia đình có nhiều thành viên. Khi thành viên kết hôn có thể tạo gia đình mới và hình thành cấu trúc mở rộng theo chiều ngang.

Hệ thống không xử lý gia phả nhiều đời, không tập trung vào dòng họ tổ tiên, mà tập trung vào cấu trúc tổ chức gia đình hiện tại và khả năng mở rộng.

Mục tiêu chính:

Quản lý cấu trúc Network → Family → Member.

Cho phép một user quản lý nhiều network.

Phân quyền theo từng network.

Hỗ trợ nghiệp vụ kết hôn và tạo gia đình mới.

Thiết kế mở rộng và đảm bảo toàn vẹn dữ liệu.

====================================================================

Phạm vi chức năng

2.1. Trong phạm vi

Quản lý user và xác thực.

Tạo và quản lý Family Network.

Phân quyền user theo từng Network.

Tạo và quản lý Family Unit.

Thêm, sửa, xoá Member.

Kết hôn giữa các Member.

Tạo Family mới khi kết hôn.

Liên kết Member với User (optional).

Soft delete và quản lý trạng thái.

2.2. Ngoài phạm vi (giai đoạn hiện tại)

Gia phả nhiều thế hệ.

Sơ đồ cây phức tạp theo lineage.

Phân quyền chi tiết theo từng Family riêng lẻ.

Tài sản, tài chính gia đình.

Social feed, bài viết.

====================================================================

Mô hình dữ liệu (ERD logic)

3.1. Entity: Users

Bảng: users

Thuộc tính:

id (PK)

email (unique)

password_hash

full_name

status (ACTIVE, INACTIVE, LOCKED)

created_at

updated_at

Mô tả:
User là tài khoản đăng nhập hệ thống. User được tạo trước khi tham gia bất kỳ network nào.

Quan hệ:

1 user có thể thuộc nhiều network thông qua network_user_roles.

1 user có thể được liên kết với 1 member trong từng network (tùy thiết kế ràng buộc).

3.2. Entity: Family Networks

Bảng: family_networks

Thuộc tính:

id (PK)

name

description

created_by (FK → users.id)

status (ACTIVE, ARCHIVED)

created_at

updated_at

Mô tả:
Family Network là cấp cao nhất, đóng vai trò container.

Quan hệ:

1 network có nhiều families.

1 network có nhiều network_user_roles.

3.3. Entity: Network User Roles

Bảng: network_user_roles

Thuộc tính:

id (PK)

network_id (FK → family_networks.id)

user_id (FK → users.id)

role (OWNER, ADMIN, MEMBER, VIEWER)

status (ACTIVE, REMOVED)

created_at

updated_at

Ràng buộc:

Unique (network_id, user_id).

Mô tả:
Quản lý quyền của user trong từng network.

3.4. Entity: Families

Bảng: families

Thuộc tính:

id (PK)

network_id (FK → family_networks.id)

name

description

created_by (FK → users.id)

status (ACTIVE, ARCHIVED, MERGED)

created_at

updated_at

Mô tả:
Family là đơn vị gia đình cụ thể trong một network.

Quan hệ:

1 network có nhiều family.

1 family có nhiều member.

3.5. Entity: Members

Bảng: members

Thuộc tính:

id (PK)

family_id (FK → families.id)

full_name

gender (MALE, FEMALE, OTHER)

date_of_birth

is_alive (boolean)

linked_user_id (FK → users.id, nullable)

status (ACTIVE, REMOVED)

created_at

updated_at

Mô tả:
Member là cá nhân trong gia đình. Không bắt buộc có account.

Ràng buộc:

1 member chỉ thuộc 1 family tại 1 thời điểm.

Nếu linked_user_id tồn tại, phải đảm bảo không xung đột logic với network.

3.6. Entity: Marriages

Bảng: marriages

Thuộc tính:

id (PK)

member_id_1 (FK → members.id)

member_id_2 (FK → members.id)

marriage_date

status (ACTIVE, DIVORCED, ENDED)

created_at

updated_at

Ràng buộc:

member_id_1 ≠ member_id_2.

Hai member phải thuộc cùng network.

Không cho phép 1 member có nhiều marriage ACTIVE cùng lúc (nếu không hỗ trợ đa hôn).

====================================================================

Business Rules

User phải tồn tại trước khi tham gia network.

1 user có thể quản lý nhiều network.

1 network có nhiều family.

1 family có nhiều member.

1 member chỉ thuộc 1 family chính tại một thời điểm.

Kết hôn có thể dẫn đến tạo family mới.

Khi tạo family mới do kết hôn:

Tạo family mới.

Cập nhật family_id của 2 member sang family mới.

Ly hôn:

Cập nhật marriage.status = DIVORCED.

Không tự động xoá family.

Quyết định tách family hay giữ nguyên phải là nghiệp vụ bổ sung.

====================================================================

Luồng nghiệp vụ chính

5.1. Tạo Network

User đăng nhập.

Tạo network.

Hệ thống tự động tạo network_user_role với role = OWNER.

5.2. Thêm user vào Network

OWNER/ADMIN thêm user theo email.

Gán role.

Tạo record network_user_roles.

5.3. Tạo Family

ADMIN/OWNER tạo family trong network.

Family gắn với network_id tương ứng.

5.4. Thêm Member

Chọn family.

Tạo member.

Nếu có account, gắn linked_user_id.

5.5. Kết hôn

Chọn 2 member.

Validate:

Cùng network.

Không có marriage ACTIVE khác.

Tạo marriage.

Option: tạo family mới.

Nếu tạo mới:

Tạo family.

Update family_id của 2 member.

====================================================================

Phân quyền

Role cấp Network:

OWNER:

Toàn quyền.

Xoá network.

Phân quyền user.

ADMIN:

Tạo/sửa/xoá family.

Thêm/sửa member.

Tạo marriage.

MEMBER:

Xem.

Có thể chỉnh sửa thông tin bản thân (nếu linked).

VIEWER:

Chỉ xem.

Tất cả kiểm tra phân quyền thực hiện tại middleware backend.

====================================================================

Kiến trúc hệ thống đề xuất

7.1. Backend

REST API hoặc GraphQL.

Kiến trúc layered:

Controller

Service

Repository

Áp dụng soft delete.

Role-based access control (RBAC).

7.2. Database

PostgreSQL hoặc MySQL.

Sử dụng foreign key đầy đủ.

Index cho các cột:

users.email

network_user_roles(network_id, user_id)

families.network_id

members.family_id

marriages.member_id_1

marriages.member_id_2

====================================================================

Phân rã công việc (Work Breakdown Structure)

EPIC 1: Authentication & User Management

Thiết kế schema users.

API đăng ký.

API đăng nhập.

JWT hoặc session.

Middleware auth.

Reset password.

Unit test và integration test.

EPIC 2: Network Management

Thiết kế bảng family_networks.

CRUD Network.

API list network theo user.

Tự động tạo OWNER role.

Test phân quyền.

EPIC 3: Network User Role (RBAC)

Thiết kế bảng network_user_roles.

API thêm user vào network.

API cập nhật role.

Middleware kiểm tra role.

Test các case role khác nhau.

EPIC 4: Family Management

Thiết kế bảng families.

CRUD Family.

Validate network ownership.

Soft delete family.

Test boundary case.

EPIC 5: Member Management

Thiết kế bảng members.

CRUD Member.

Link Member với User.

Validate member thuộc đúng network.

Test di chuyển member giữa family.

EPIC 6: Marriage Logic

Thiết kế bảng marriages.

API tạo marriage.

Validate 1-1 active marriage.

Logic tạo family mới khi kết hôn.

Logic ly hôn.

Unit test nghiệp vụ phức tạp.

EPIC 7: UI/UX

Dashboard: danh sách network.

Network detail: danh sách family.

Family detail: danh sách member.

Flow kết hôn và tạo family mới.

Kiểm tra role hiển thị UI.

EPIC 8: QA & Testing

Test case cho từng role.

Test case marriage edge cases.

Test performance với nhiều network.

Regression test.

EPIC 9: DevOps

Setup CI/CD.

Migration DB.

Seed data.

Environment dev/staging/prod.