# Family Network System — Implementation TODO

**Nguồn yêu cầu:** `docs/family network.md` (Tài liệu thiết kế hệ thống Mạng lưới gia đình)

**Mục tiêu:** Network → Family → Member. Một user quản lý nhiều network. Phân quyền theo network (RBAC). Hỗ trợ kết hôn và tạo gia đình mới.

---

## Quy ước

- `[ ]` Chưa làm
- `[x]` Hoàn thành
- **(BE)** Backend · **(FE)** Frontend · **(DB)** Database · **(Ops)** DevOps
- Cuối mỗi Epic, cần có menu/điều hướng để kiểm tra nhanh tính năng.

---

## Phần 0 — Dọn dẹp / Chuyển đổi từ hệ thống cũ

Các tính năng **ngoài phạm vi** theo doc mới (có thể bỏ hoặc tạm vô hiệu hóa):

- Gia phả nhiều thế hệ, sơ đồ lineage
- Social feed, bài viết (posts)
- Phân quyền theo từng Family riêng lẻ (chỉ làm RBAC theo Network)
- UserPerson (thay bằng `members.linked_user_id`)

### 0.1. Xác định phạm vi dọn dẹp

- [ ] **(Docs)** Liệt kê endpoint/file cần xóa hoặc deprecated: `lineages`, `posts`, `user_person`, `persons` (thay bằng `members`), `ParentChild` nếu không dùng
- [ ] **(BE)** Quyết định: xóa hẳn hay giữ bảng cũ (read-only) để migrate dữ liệu (nếu có)

### 0.2. Backend — Gỡ bỏ / deprecated (sau khi Epic mới chạy ổn)

- [ ] **(BE)** Gỡ route/schema/service: Lineage, Post, UserPerson, Person (khi đã có Member + Family + Network)
- [ ] **(BE)** Cập nhật `app/api/__init__.py` và `app/main.py`: chỉ đăng ký route mới (auth, networks, families, members, marriages)
- [ ] **(DB)** (Tùy chọn) Migration xóa hoặc rename bảng cũ: `lineages`, `posts`, `user_person`, `persons`, `parent_child` — chỉ khi không cần giữ dữ liệu cũ

### 0.3. Frontend — Gỡ bỏ

- [ ] **(FE)** Gỡ trang và API client: Lineages, Posts, UserPerson; menu Dashboard chỉ còn Networks/Families/Members
- [ ] **(FE)** Cập nhật types/domain: bỏ Person/Lineage/Post, thêm Network, Family, Member, Marriage (theo doc)

---

## EPIC 1 — Authentication & User Management

- [x] **(DB)** Schema `users`: id, email (unique), password_hash, full_name, status (ACTIVE, INACTIVE, LOCKED), created_at, updated_at
- [x] **(BE)** API đăng ký: `POST /api/auth/register`
- [x] **(BE)** API đăng nhập: `POST /api/auth/login` (trả JWT hoặc session)
- [x] **(BE)** JWT hoặc session; middleware gắn `request.state.user_id`, `user_email`
- [x] **(BE)** Middleware auth: bảo vệ route (trừ login/register/health)
- [ ] **(BE)** Reset password (optional cho Phase 1)
- [x] **(BE)** Unit/integration test auth
- [x] **(FE)** Màn Login, Register, Logout (đã có thì chỉnh cho khớp API mới)

---

## EPIC 2 — Network Management

- [x] **(DB)** Bảng `family_networks`: id, name, description, created_by (FK users.id), status (ACTIVE, ARCHIVED), created_at, updated_at
- [x] **(DB)** Index: `family_networks.created_by`, (tuỳ chọn) name
- [x] **(DB)** Bảng `network_user_roles` (cho EPIC 3; dùng ngay khi tạo network → OWNER)
- [x] **(BE)** CRUD Network: create, list, get, update, soft delete (status = ARCHIVED)
- [x] **(BE)** API list network theo user: `GET /api/networks` (chỉ networks user tham gia)
- [x] **(BE)** Khi tạo network → tự tạo `network_user_roles` với role = OWNER
- [x] **(BE)** Phân quyền: chỉ OWNER/ADMIN sửa; chỉ OWNER lưu trữ (archive)
- [x] **(FE)** Dashboard: danh sách network của user; nút tạo network; vào chi tiết network

---

## EPIC 3 — Network User Role (RBAC)

- [x] **(DB)** Bảng `network_user_roles`: đã có từ EPIC 2
- [x] **(BE)** API thêm user vào network (theo email): `POST /api/networks/{id}/members` body: email, role
- [x] **(BE)** API cập nhật role: `PATCH /api/networks/{id}/members/{member_user_id}` body: role
- [x] **(BE)** API list members: `GET /api/networks/{id}/members`
- [x] **(BE)** API xóa member (status REMOVED): `DELETE /api/networks/{id}/members/{member_user_id}`; kiểm tra OWNER/ADMIN trong service
- [x] **(BE)** Không cho đổi role OWNER, không cho xóa OWNER
- [ ] **(BE)** Test từng role (optional)
- [x] **(FE)** Màn quản lý thành viên network (chỉ OWNER/ADMIN): danh sách, thêm user theo email, đổi role, xóa

---

## EPIC 4 — Family Management

- [x] **(DB)** Bảng `families`: id, network_id (FK), name, description, created_by (FK users.id), status (ACTIVE, ARCHIVED, MERGED), created_at, updated_at
- [x] **(DB)** Index: `families.network_id`
- [x] **(BE)** CRUD Family trong network; validate OWNER/ADMIN cho tạo/sửa/lưu trữ
- [x] **(BE)** Soft delete family (status = ARCHIVED)
- [x] **(BE)** API: `GET/POST /api/networks/{id}/families`, `GET/PATCH /api/families/{id}`, `PATCH /api/families/{id}/archive`
- [x] **(FE)** Network detail: danh sách family; nút tạo gia đình; trang tạo/sửa/chi tiết family

---

## EPIC 5 — Member Management

- [x] **(DB)** Bảng `members`: id, family_id (FK), full_name, gender (MALE, FEMALE, OTHER), date_of_birth, is_alive, linked_user_id (nullable), status (ACTIVE, REMOVED), created_at, updated_at
- [x] **(DB)** Index: `members.family_id`, `members.linked_user_id`
- [x] **(BE)** CRUD Member; validate quyền qua family → network (OWNER/ADMIN cho tạo/sửa/xóa)
- [x] **(BE)** Link Member với User: POST/DELETE `/api/members/{id}/link`; validate 1 user – 1 member per network
- [x] **(BE)** API: GET/POST `/api/families/{id}/members`, GET/PATCH `/api/members/{id}`, PATCH `/api/members/{id}/remove`
- [x] **(FE)** Family detail: danh sách member; thêm thành viên; sửa (trang /members/{id}/edit); xóa; hiển thị đã gắn tài khoản

---

## EPIC 6 — Marriage Logic

- [x] **(DB)** Bảng `marriages`: id, member_id_1 (FK), member_id_2 (FK), marriage_date, status (ACTIVE, DIVORCED, ENDED), created_at, updated_at
- [x] **(DB)** Ràng buộc: member_id_1 ≠ member_id_2; index `marriages.member_id_1`, `marriages.member_id_2`
- [x] **(BE)** API tạo marriage: validate hai member cùng network; không có marriage ACTIVE khác cho từng member (nếu không hỗ trợ đa hôn)
- [x] **(BE)** Option “tạo family mới khi kết hôn”: tạo family → cập nhật family_id của 2 member
- [x] **(BE)** Logic ly hôn: cập nhật marriage.status = DIVORCED; không tự xóa family (nghiệp vụ bổ sung nếu cần tách family)
- [x] **(BE)** API: `POST /api/marriages`, `GET /api/networks/{id}/marriages`, `GET /api/marriages/{id}`, `PATCH /api/marriages/{id}` (status DIVORCED/ENDED)
- [ ] **(BE)** Unit test: cùng network, trùng marriage ACTIVE, tạo family mới, ly hôn
- [x] **(FE)** Flow kết hôn (đã đổi): **Tạo gia đình mới** trong **chi tiết gia đình** — chọn 1 thành viên (con), thêm vợ/chồng mới → tạo gia đình mới + ghi nhận kết hôn; danh sách marriage + nút ly hôn trong family detail

---

## EPIC 7 — UI/UX

- [x] **(FE)** Dashboard: danh sách network (Mạng lưới), link vào từng network; EmptyState + LoadingSpinner
- [x] **(FE)** Network detail: danh sách family; nút tạo family; phân quyền (canEdit = OWNER/ADMIN)
- [x] **(FE)** Family detail: danh sách member; thêm/sửa member; hiển thị marriage; canEdit từ network role
- [x] **(FE)** Flow kết hôn và tạo family mới (đã có ở Epic 6)
- [x] **(FE)** Kiểm tra role: ẩn/hiện nút theo OWNER/ADMIN (family + network detail)
- [x] **(FE)** Header/menu: Mạng lưới (link Dashboard); user dropdown (email, vai trò, đăng xuất)
- [x] **(FE)** Empty/Loading/Error states (PageLoading, LoadingSpinner, EmptyState); responsive (Tailwind sm:)

---

## EPIC 8 — Network detail: 2 chế độ CMS & Graph

- [x] **(FE)** Chế độ xem: toggle **CMS** và **Đồ thị** trên màn chi tiết mạng lưới.
- [x] **(FE)** **Chế độ CMS**: bảng biểu — gia đình (bảng + tìm kiếm, cột Tên, Mô tả, Trạng thái, Thao tác); thành viên mạng (bảng + tìm kiếm); bảng thành viên gia đình toàn mạng (Họ tên, Gia đình, Giới tính, Sửa).
- [x] **(FE)** **Chế độ Graph**: đồ thị force-directed (react-force-graph-2d) — node = thành viên gia đình, cạnh = kết hôn; tooltip tên + gia đình; màu theo gia đình; click node mở trang sửa member.

---

## EPIC 9 — QA & Testing

- [ ] Test case từng role (OWNER/ADMIN/MEMBER/VIEWER) cho từng API
- [ ] Test marriage edge cases: cùng network, khác network (reject), double active marriage (reject), ly hôn rồi kết hôn lại
- [ ] Test performance: nhiều network, nhiều family, nhiều member (optional)
- [ ] Regression: auth, CRUD network/family/member, marriage flow

---

## EPIC 10 — DevOps (có thể làm song song hoặc sau)

- [ ] **(Ops)** CI/CD: chạy test, lint
- [ ] **(DB)** Migration thống nhất: tạo bảng mới (users nếu đổi, family_networks, network_user_roles, families, members, marriages); không phá dữ liệu đang dùng
- [ ] **(Ops)** Seed data: 1 user, 1 network, 1–2 family, vài member (optional)
- [ ] **(Ops)** Environment: dev / staging / prod; config DB, JWT secret

---

## Tóm tắt thứ tự ưu tiên

1. **EPIC 1** (Auth) — nền tảng.
2. **EPIC 2** (Network) + **EPIC 3** (RBAC) — để mọi thứ gắn với network và quyền.
3. **EPIC 4** (Family) → **EPIC 5** (Member) — cấu trúc Network → Family → Member.
4. **EPIC 6** (Marriage) — nghiệp vụ đặc thù.
5. **EPIC 7** (UI/UX) — có thể làm song song từ sau Epic 2.
6. **Phần 0** (dọn dẹp): có thể làm sau khi Epic 2–6 đã chạy ổn, hoặc làm từng bước (deprecated route trước, xóa code cũ sau).

File này thay thế nội dung TODO cũ (theo `init.md` / Person–Lineage–Post). Các tính năng cũ không còn trong phạm vi thiết kế mới có thể bỏ đi khi đã chuyển xong sang model Network → Family → Member.
