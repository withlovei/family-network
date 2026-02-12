## Family Network — API Contract (MVP / Phase 1)

Nguồn rules: `docs/init.md`. Tất cả quyền truy cập dữ liệu nhạy cảm phải đi qua **AccessService** (default deny).

### Base

- **API base**: `/api`
- **Auth header**: `Authorization: Bearer <access_token>`
- **Error shape**:

```json
{ "detail": "message" }
```

---

## Auth

### `POST /api/auth/register`

**Request**

```json
{ "email": "you@example.com", "full_name": "Nguyễn Văn A", "password": "secret" }
```

**Response**

```json
{
  "user": {
    "id": "uuid",
    "email": "you@example.com",
    "full_name": "Nguyễn Văn A",
    "is_active": true,
    "role": "user",
    "created_at": "2026-02-12T00:00:00Z"
  },
  "token": { "access_token": "jwt", "token_type": "bearer" }
}
```

### `POST /api/auth/login`

**Request**

```json
{ "email": "admin@example.com", "password": "Admin123!" }
```

**Response**: same as register.

### `POST /api/auth/logout`

**Response**

```json
{ "message": "Logged out successfully" }
```

---

## User ↔ Person mapping (Phase 1 foundation)

> Spec: `User` có thể liên kết 1..n `Person` (không gộp Person và User).

### `GET /api/users/me`

**Response**

```json
{ "id": "uuid", "email": "admin@example.com", "role": "admin" }
```

### `GET /api/me/persons`

**Response**

```json
{
  "items": [
    { "person_id": "uuid", "full_name": "..." }
  ]
}
```

### `POST /api/me/persons/link`

Link user với person (UserPerson).

**Request**

```json
{ "person_id": "uuid" }
```

**Response**

```json
{ "ok": true }
```

---

## Person (Phase 1)

### `POST /api/persons`

**Request**

```json
{
  "full_name": "Nguyễn Văn A",
  "gender": "male",
  "birth_date": "1990-01-01",
  "death_date": null,
  "primary_lineage_id": "uuid"
}
```

### `GET /api/persons/{id}`

AccessService rule: allow if same accessible_lineages OR direct relation (parent/child/current spouse).

---

## Post (Phase 1)

### `POST /api/posts`

**Request**

```json
{
  "author_person_id": "uuid",
  "visibility": "LINEAGE_PUBLIC",
  "content": "..."
}
```

### `GET /api/posts`

List posts viewer có quyền xem theo AccessService + visibility rules trong `docs/init.md`.

