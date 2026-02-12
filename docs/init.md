FAMILY NETWORK SYSTEM DESIGN
1. Overview

Hệ thống “Mạng lưới gia đình” là một nền tảng SaaS kết hợp:

Gia phả truyền thống (patrilineal tree)

Mạng xã hội riêng tư theo nhánh

Phân quyền theo quan hệ huyết thống và hôn nhân

Lưu trữ kỷ niệm, sự kiện, thông báo

Mục tiêu:

Giữ đúng truyền thống: gia phả theo dòng cha

Đáp ứng hiện đại: quan hệ dạng mạng lưới

Phân quyền chặt chẽ giữa các nhánh

Một tài khoản có thể thuộc nhiều nhánh

2. Core Concepts
2.1 Person vs User

Person

Thực thể trong gia phả

Có thể đã mất

Có thể chưa có tài khoản

User

Tài khoản đăng nhập

Có thể liên kết với một hoặc nhiều Person

Không được gộp Person và User làm một.

3. Domain Model
3.1 Person
Person (
    id UUID PRIMARY KEY,
    full_name TEXT,
    gender ENUM('male','female'),
    birth_date DATE,
    death_date DATE,
    primary_lineage_id UUID,
    created_at TIMESTAMP
)

3.2 Lineage (Nhánh gia đình)
Lineage (
    id UUID PRIMARY KEY,
    name TEXT,
    root_person_id UUID,
    tradition_type ENUM('patrilineal','modern'),
    created_at TIMESTAMP
)

3.3 Parent-Child Relationship
ParentChild (
    parent_id UUID,
    child_id UUID,
    relation_type ENUM('biological','adopted'),
    PRIMARY KEY (parent_id, child_id)
)

3.4 Marriage
Marriage (
    id UUID PRIMARY KEY,
    person_a_id UUID,
    person_b_id UUID,
    start_date DATE,
    end_date DATE,
    status ENUM('married','divorced','widowed')
)

3.5 User
User (
    id UUID PRIMARY KEY,
    email TEXT UNIQUE,
    password_hash TEXT,
    created_at TIMESTAMP
)

3.6 User-Person Mapping
UserPerson (
    user_id UUID,
    person_id UUID,
    PRIMARY KEY (user_id, person_id)
)

4. Lineage Rules (Truyền thống)
4.1 Kế thừa nhánh

Con trai: inherit primary_lineage từ cha

Con gái: inherit primary_lineage từ cha

Khi kết hôn:

Không thay đổi primary_lineage

Chỉ mở rộng accessible_lineages

4.2 Accessible Lineages

Không lưu cố định trong DB.
Tính động dựa trên:

primary_lineage

hôn nhân đang hiệu lực

AccessibleLineages(person):

Set = { person.primary_lineage }

For each active marriage:
    add spouse.primary_lineage


Không propagate lên cha mẹ.
Không mở rộng toàn bộ nhánh bên kia.

5. Access Control Model (ReBAC)

Phân quyền dựa trên quan hệ.

Tạo AccessService:

canViewPerson(viewer_id, target_person_id)

canViewPost(viewer_id, post_id)

canViewEvent(viewer_id, event_id)

6. Viewing Person Rules

Cho phép nếu:

target.primary_lineage ∈ viewer.accessible_lineages
OR

viewer và target có quan hệ trực tiếp:

spouse (active)

parent

child

Không cho phép nếu khác nhánh và không có quan hệ trực tiếp.

7. Post System
7.1 Post Table
Post (
    id UUID PRIMARY KEY,
    author_person_id UUID,
    visibility ENUM('LINEAGE_PUBLIC','DIRECT_FAMILY_PRIVATE'),
    content TEXT,
    created_at TIMESTAMP
)

8. Post Visibility Rules
8.1 LINEAGE_PUBLIC

Viewer được xem nếu:

author.primary_lineage ∈ viewer.accessible_lineages
OR

viewer là:

spouse (active)

parent

child

Không mở rộng sang toàn bộ nhánh của spouse.

8.2 DIRECT_FAMILY_PRIVATE

Chỉ cho phép:

author

cha mẹ

con cái

vợ/chồng hiện tại

Định nghĩa DirectFamily(A):

Parents(A)
∪ Children(A)
∪ CurrentSpouse(A)
∪ A


Không bao gồm:

anh chị em

ông bà

cháu

họ hàng

9. Divorce Handling

Khi Marriage.end_date != null:

Remove spouse.primary_lineage khỏi accessible_lineages

Spouse cũ mất quyền truy cập post DIRECT_FAMILY_PRIVATE

Quyền được tính theo trạng thái hiện tại (không snapshot)

10. Genealogy Export

Gia phả truyền thống:

Bắt đầu từ Lineage.root_person_id

Duyệt theo ParentChild

Chỉ extend tiếp nếu:
child.primary_lineage == lineage.id

Con gái:

Hiển thị trong cây

Không tiếp tục extend nếu đã chuyển nhánh theo cấu hình truyền thống

Output:

JSON

PDF

Tree UI

11. Event System
Event (
    id UUID PRIMARY KEY,
    creator_person_id UUID,
    lineage_id UUID,
    visibility ENUM('LINEAGE','PRIVATE'),
    title TEXT,
    description TEXT,
    event_date DATE
)


Visibility:

LINEAGE → toàn bộ lineage xem được

PRIVATE → direct family

12. Architecture (SaaS + Cloud)
12.1 Backend

Language: Node.js / Go / Java

Framework: NestJS / Spring Boot

Auth: JWT + Refresh Token

12.2 Database

PostgreSQL

Row Level Security theo lineage_id

Redis cache accessible_lineages

12.3 Storage

S3 compatible (MinIO / AWS S3)

Media files stored outside DB

12.4 Services

Auth Service

Person Service

Lineage Service

Access Service

Post Service

Event Service

Media Service

AccessService phải là lớp trung tâm.

13. Performance Strategy

Cache:

direct relations

accessible_lineages

Không cache danh sách người được phép xem từng post

Dùng index:

primary_lineage_id

author_person_id

marriage(person_a_id, person_b_id)

14. Security Principles

Mặc định deny

Không bao giờ expose dữ liệu khác nhánh nếu không có quan hệ

Tất cả API phải đi qua AccessService

Audit log mọi truy cập nhạy cảm

15. Future Extensions

Modern mode (bilateral lineage)

Custom visibility

Role: LineageAdmin

AI tự động vẽ cây gia phả

Notification system

Mobile app

16. Implementation Phases

Phase 1:

Person

Lineage

Marriage

AccessService

Basic Post

Phase 2:

Event

Media

Export genealogy

Phase 3:

Advanced privacy

Admin roles

SaaS billing