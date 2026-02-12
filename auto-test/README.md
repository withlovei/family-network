# Family Network — Auto Test

Thư mục chứa automation test cho API (backend) và E2E (frontend).

## Cấu trúc

```
auto-test/
├── api/              # API tests (pytest + httpx)
│   ├── conftest.py   # Fixtures: base_url, client
│   └── test_auth.py  # Auth endpoints: register, login, logout, users/me
├── frontend/         # E2E tests (Playwright)
│   ├── e2e/          # Spec files
│   └── playwright.config.ts
├── run-tests.sh      # Chạy tất cả tests
└── README.md
```

## Yêu cầu

- **API tests**: Python 3.10+, backend đang chạy trên http://localhost:8001
- **Frontend tests**: Node.js 18+, frontend đang chạy trên http://localhost:3008

## Chạy tests

### API tests

```bash
# Backend phải đang chạy trên port 8001
./run.sh backend

# Chạy API tests
cd auto-test/api && pip install -r requirements.txt && pytest -v

# Hoặc từ project root
./auto-test/run-tests.sh api
```

### Frontend E2E tests

```bash
# Backend + Frontend phải đang chạy
./run.sh

# Terminal khác: chạy E2E
cd auto-test/frontend && npm install && npx playwright test

# Hoặc từ project root
./auto-test/run-tests.sh frontend
```

### Chạy tất cả

```bash
./auto-test/run-tests.sh all
```

## Biến môi trường

- `API_BASE_URL`: Backend URL (mặc định http://localhost:8001)
- `FRONTEND_BASE_URL`: Frontend URL (mặc định http://localhost:3008)
- `TEST_ADMIN_EMAIL`, `TEST_ADMIN_PASSWORD`: Credentials cho E2E (mặc định admin@example.com / Admin123!)
