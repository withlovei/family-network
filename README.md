# Family Network

Monorepo: Backend (Python/FastAPI) + Frontend (Next.js).

## Yêu cầu

- Python 3.10+
- Node.js 18+
- PostgreSQL

## Cấu trúc

- `backend/` — FastAPI, PostgreSQL, JWT auth, roles (user, family_manager, branch_manager, branch_contributor, admin)
- `frontend/` — Next.js 16, Tailwind, login/register/dashboard

## Thiết lập

**Cách nhanh (Mac/Linux):**

```bash
./install.sh   # cài dependency backend + frontend, tạo .env nếu chưa có
```

### Thủ công

**Backend**

```bash
cd backend
cp .env.sample .env
# Chỉnh .env: DATABASE_URL, SECRET_KEY, ADMIN_EMAIL, ADMIN_PASSWORD
python -m venv .venv
# Mac/Linux: source .venv/bin/activate
# Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

**Frontend**

```bash
cd frontend
cp .env.sample .env
# Tùy chọn: NEXT_PUBLIC_API_URL=http://localhost:8001
npm install
```

### Database

Tạo database PostgreSQL (ví dụ `family_network`), sau đó chạy migration:

**Mac/Linux:**

```bash
./migrate.sh
```

**Windows:**

```bat
migrate.bat
```

Hoặc thủ công:

```bash
cd backend && source .venv/bin/activate && alembic upgrade head
```

## Chạy

- Backend: **http://localhost:8001**
- Frontend: **http://localhost:3008**

**Mac/Linux:**

```bash
./run.sh          # chạy cả backend + frontend (all)
./run.sh backend  # chỉ backend
./run.sh frontend # chỉ frontend
```

**Windows:**

```bat
run.bat          REM mở 2 cửa sổ: backend + frontend
run.bat backend  REM chỉ backend
run.bat frontend REM chỉ frontend
```

Hoặc chạy tay:

```bash
# Terminal 1 - Backend
cd backend && source .venv/bin/activate && uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload

# Terminal 2 - Frontend
cd frontend && npm run dev
```

## Tài khoản admin mặc định

Lần chạy backend đầu tiên, nếu trong DB chưa có user nào có role admin và trong `.env` có `ADMIN_EMAIL` + `ADMIN_PASSWORD`, backend sẽ tạo một user admin để đăng nhập lần đầu. Mặc định trong `.env.sample`: `admin@example.com` / `Admin123!` (nên đổi trong production).

**Reset mật khẩu admin theo .env:** Chạy script để đặt lại mật khẩu user admin (theo `ADMIN_EMAIL` / `ADMIN_PASSWORD` trong `backend/.env`). Nếu chưa có user với email đó thì sẽ tạo mới.

```bash
./reset-admin.sh    # Mac/Linux
reset-admin.bat     # Windows
```

## API

- `POST /api/auth/register` — Đăng ký
- `POST /api/auth/login` — Đăng nhập
- `POST /api/auth/logout` — Đăng xuất
- `GET /api/users/me` — Thông tin user (cần Bearer token)
- `GET /health` — Health check

## Vai trò (roles)

- `user` — Thành viên
- `family_manager` — Quản lý gia đình
- `branch_manager` — Quản lý chi nhánh
- `branch_contributor` — Cộng tác viên chi nhánh
- `admin` — Quản trị viên
# family-network
