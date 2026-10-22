# Enterprise API Management & Analytics Dashboard

A portfolio-ready backend project built with **FastAPI, PostgreSQL, SQLAlchemy 2, JWT authentication, role-based access control, Alembic, pytest, and Docker Compose**.

It provides:
- JWT login and role-based access (`admin`, `analyst`, `viewer`)
- User administration (admin-only)
- CRUD APIs for business records
- Search, filtering, pagination, and sorting
- Analytics endpoints for record counts and status breakdowns
- Request ID middleware and structured application logging
- PostgreSQL health checks and Docker-based local setup
- Automated tests using SQLite for a quick test run

> This is a starter portfolio application, not a production-certified system. Before production use, add secret management, HTTPS/reverse proxy configuration, rate limiting, audit retention, backup/restore procedures, and a formal security review.

## Architecture

```text
Client / Dashboard
       |
       v
FastAPI routers
  |-- Auth
  |-- Users (admin)
  |-- Records (CRUD)
  |-- Analytics
       |
       v
Service / CRUD layer
       |
       v
SQLAlchemy ORM
       |
       v
PostgreSQL
```

## 1. Requirements

- Python 3.11+
- Docker Desktop + Docker Compose (recommended), or local PostgreSQL
- Git

## 2. Run with Docker

```bash
cp .env.example .env
docker compose up --build
```

On Windows PowerShell, copy the environment file with:

```powershell
Copy-Item .env.example .env
docker compose up --build
```

Open:
- Swagger UI: http://localhost:8000/docs
- Health: http://localhost:8000/health
- API prefix: http://localhost:8000/api/v1

The first startup creates database tables and seeds a development admin account if `SEED_ADMIN=true`.

**Development login**
- Email: `admin@example.com`
- Password: `ChangeMe123!`

Change these values in `.env` before sharing or deploying the project. Do not use the development credentials in production.

## 3. Run locally without Docker

Create a virtual environment and install dependencies:

```bash
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

pip install -r requirements.txt
```

Set `DATABASE_URL` in `.env` to your PostgreSQL connection string, then run:

```bash
uvicorn app.main:app --reload
```

Tables are created on startup for ease of local setup. Alembic configuration is included for future schema migrations.

## 4. API quick start

### Login

```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin@example.com&password=ChangeMe123!"
```

Copy the returned `access_token`, then use it as a bearer token.

### Create a record

```bash
curl -X POST http://localhost:8000/api/v1/records \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Quarterly API migration",
    "description": "Migrate reporting endpoints",
    "status": "open",
    "priority": "high",
    "owner": "Data Platform"
  }'
```

### List records

```bash
curl "http://localhost:8000/api/v1/records?status=open&page=1&page_size=10" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Analytics

```bash
curl http://localhost:8000/api/v1/analytics/overview \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## 5. Roles

| Role | Read records | Create/update records | Delete records | Analytics | Manage users |
|---|---:|---:|---:|---:|---:|
| admin | Yes | Yes | Yes | Yes | Yes |
| analyst | Yes | Yes | No | Yes | No |
| viewer | Yes | No | No | Yes | No |

## 6. Main endpoints

| Method | Endpoint | Access | Description |
|---|---|---|---|
| GET | `/health` | Public | Health check |
| POST | `/api/v1/auth/login` | Public | OAuth2 password login |
| GET | `/api/v1/auth/me` | Authenticated | Current user |
| GET | `/api/v1/users` | Admin | List users |
| POST | `/api/v1/users` | Admin | Create user |
| GET | `/api/v1/records` | Authenticated | Filter/search/paginate records |
| POST | `/api/v1/records` | Admin/analyst | Create record |
| GET | `/api/v1/records/{id}` | Authenticated | Get record |
| PATCH | `/api/v1/records/{id}` | Admin/analyst | Update record |
| DELETE | `/api/v1/records/{id}` | Admin | Delete record |
| GET | `/api/v1/analytics/overview` | Authenticated | KPI summary |
| GET | `/api/v1/analytics/status-breakdown` | Authenticated | Counts by status |
| GET | `/api/v1/analytics/records-by-month` | Authenticated | Monthly created-record counts |

## 7. Tests

```bash
pytest -q
```

The tests override the database with SQLite, so Docker/PostgreSQL is not required to run the test suite.

## 8. GitHub publishing

```bash
git init
git add .
git commit -m "Initial enterprise API analytics platform"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/enterprise-api-analytics.git
git push -u origin main
```

Before publishing, check `.env` is not tracked. `.gitignore` excludes it.

## 9. Resume description (use after you build and verify it)

**Enterprise API Management & Analytics Dashboard**  
*Python, FastAPI, PostgreSQL, SQLAlchemy, JWT, Docker, pytest*

- Built a REST API platform with JWT authentication and role-based authorization for administrative, analyst, and viewer roles.
- Implemented CRUD operations with filtering, search, sorting, pagination, and validation using FastAPI and SQLAlchemy.
- Developed analytics endpoints for KPI summaries, status breakdowns, and monthly record trends.
- Containerized the application and database with Docker Compose and added automated API tests using pytest.

Only claim features you have personally run and verified.
