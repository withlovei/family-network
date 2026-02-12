## Family Network — Implementation TODO

Nguồn yêu cầu: `docs/init.md`

### Quy ước

- [ ] Chưa làm
- [x] Hoàn thành
- (BE/FE/DB/Ops): phân nhóm công việc
- Cuối **mỗi Phase**, frontend phải có **menu/header điều hướng** để truy cập và kiểm tra nhanh các tính năng vừa build

---

## Phase 0 — Foundation (chuẩn bị)

- [x] **(DB)** Chuẩn hóa quyết định ID: dùng **UUID cho tất cả bảng** (Person/Lineage/Marriage/Post/Event/User…) hay giữ `users.id` là int như hiện tại
- [x] **(BE)** Chốt strategy auth + mapping `User ↔ Person` (user có thể map nhiều person)
- [x] **(BE)** Chốt phạm vi role: role global (admin/manager…) vs role theo Lineage (LineageAdmin) cho Phase 1
- [x] **(Ops)** Docker compose local (Postgres) hoặc hướng dẫn local DB thống nhất
- [x] **(Docs)** Define API contract MVP (endpoint list + payload + error shape)

---

## Phase 1 — MVP (Person/Lineage/Marriage/AccessService/Basic Post)

### 1) Database schema & migrations

- [ ] **(DB)** Tạo migrations cho:
  - [ ] `persons` (Person)
  - [ ] `lineages` (Lineage)
  - [ ] `parent_child` (ParentChild)
  - [ ] `marriages` (Marriage)
  - [ ] `user_person` (UserPerson)
  - [ ] `posts` (Post)
- [ ] **(DB)** Index theo spec:
  - [ ] `persons.primary_lineage_id`
  - [ ] `posts.author_person_id`
  - [ ] `marriages(person_a_id, person_b_id)`

### 2) Backend services (core business)

- [ ] **(BE)** `AccessService`
  - [ ] Tính `accessible_lineages(person)` theo rules (primary_lineage + active marriage spouse.primary_lineage)
  - [ ] `canViewPerson(viewer_person_id, target_person_id)`
  - [ ] `canViewPost(viewer_person_id, post_id)`
  - [ ] `canViewEvent(viewer_person_id, event_id)` (stub cho Phase 2)
- [ ] **(BE)** `PersonService`
  - [ ] CRUD Person
  - [ ] Read Person có kiểm tra `AccessService.canViewPerson`
- [ ] **(BE)** `LineageService`
  - [ ] Create lineage + root person binding
  - [ ] Get lineage detail
- [ ] **(BE)** `MarriageService`
  - [ ] Create marriage (start)
  - [ ] End marriage (divorce/widowed) → quyền truy cập tính theo trạng thái hiện tại
- [ ] **(BE)** `PostService`
  - [ ] Create post với `visibility = LINEAGE_PUBLIC | DIRECT_FAMILY_PRIVATE`
  - [ ] List posts viewer được xem (enforce AccessService)
  - [ ] Get post detail (enforce AccessService)

### 3) Backend API endpoints (REST)

- [ ] **(BE)** Auth
  - [ ] `POST /api/auth/register`
  - [ ] `POST /api/auth/login`
  - [ ] `POST /api/auth/logout`
- [ ] **(BE)** User/Person mapping
  - [ ] `GET /api/users/me`
  - [ ] `GET /api/me/persons` (list persons mapped to user)
  - [ ] `POST /api/me/persons/link` (link a person)
  - [ ] `POST /api/me/persons/active` (choose active person for session/context)
- [ ] **(BE)** Person
  - [ ] `POST /api/persons`
  - [ ] `GET /api/persons/{id}` (AccessService)
  - [ ] `PATCH /api/persons/{id}`
- [ ] **(BE)** Lineage
  - [ ] `POST /api/lineages`
  - [ ] `GET /api/lineages/{id}`
- [ ] **(BE)** Marriage
  - [ ] `POST /api/marriages`
  - [ ] `POST /api/marriages/{id}/end`
- [ ] **(BE)** Post
  - [ ] `POST /api/posts`
  - [ ] `GET /api/posts`
  - [ ] `GET /api/posts/{id}`

### 4) Frontend UX/UI (MVP)

- [ ] **(FE)** Header / Navigation
  - [ ] Header cố định (logo/tên app + menu)
  - [ ] Menu item cho các tính năng Phase 1: Dashboard, Persons, Lineages, Posts
  - [ ] Hiển thị user + role + nút Đăng xuất
- [ ] **(FE)** Menu kiểm tra Phase 1
  - [ ] Có một mục (hoặc submenu) “Phase 1 / MVP” để dễ truy cập các screen test chính
  - [ ] Đảm bảo mỗi khi Phase 1 hoàn thành, tất cả luồng chính đều có thể start từ menu này
- [ ] **(FE)** Auth screens
  - [ ] Login
  - [ ] Register
  - [ ] Logout
- [ ] **(FE)** Active person flow
  - [ ] Screen chọn “Bạn là ai trong gia phả?” (active person)
  - [ ] Link person (nếu chưa map)
- [ ] **(FE)** Dashboard
  - [ ] Hiển thị thông tin user + active person + accessible lineages
- [ ] **(FE)** Post
  - [ ] Create post (chọn visibility)
  - [ ] Feed (list) + detail
- [ ] **(FE)** Responsive + error states
  - [ ] Empty states
  - [ ] Loading states
  - [ ] Friendly error messages

### 5) QA / Security basics

- [ ] **(BE)** Default deny: tất cả endpoint đọc dữ liệu phải qua AccessService
- [ ] **(BE)** Audit log (tối thiểu) cho truy cập nhạy cảm (view person/post)
- [ ] **(BE/FE)** Test plan thủ công cho rules:
  - [ ] Same lineage → xem được LINEAGE_PUBLIC
  - [ ] Married (active) → mở rộng accessible_lineages đúng
  - [ ] Divorce → revoke quyền theo rules
  - [ ] DIRECT_FAMILY_PRIVATE chỉ direct family (parents/children/current spouse/self)

---

## Phase 2 — Event / Media / Export genealogy

### Event

- [ ] **(DB)** `events` table + enums visibility `LINEAGE | PRIVATE`
- [ ] **(BE)** `EventService` + `canViewEvent`
- [ ] **(FE)** Calendar/list event + create event + visibility

### Media

- [ ] **(Ops)** S3-compatible storage (MinIO local)
- [ ] **(BE)** Upload/sign URL + metadata table
- [ ] **(FE)** Upload + gallery in post/event

### Export genealogy

- [ ] **(BE)** Export JSON tree theo rule:
  - [ ] Duyệt từ `Lineage.root_person_id`
  - [ ] Chỉ extend tiếp nếu `child.primary_lineage == lineage.id` (patrilineal)
- [ ] **(FE)** Tree UI (interactive)
- [ ] **(BE)** (Optional) PDF export

---

## Phase 3 — Advanced privacy / Admin roles / SaaS billing

- [ ] **(BE)** Advanced privacy (custom visibility)
- [ ] **(BE)** Role theo lineage (LineageAdmin) + admin console
- [ ] **(Ops)** Billing (Stripe) + tenant isolation (SaaS)
- [ ] **(Sec)** RLS theo lineage_id (Postgres) + cache accessible_lineages (Redis)

