# PS-21 — Backend Foundation & API Services

Production-grade asynchronous FastAPI backend for the **PS-21 Conversational Insurance Acquisition & Onboarding Platform**.

---

## 1. Technology Architecture

- **Runtime:** Python 3.11+ / 3.13
- **API Framework:** FastAPI 0.115+ (ASGI, Async, OpenAPI v3)
- **Database:** SQLite 3 with WAL (`Write-Ahead Logging`) mode and foreign key constraint enforcement
- **ORM / Toolkit:** SQLAlchemy 2.0 (Modern 2.0 declarative style with `Mapped[T]` and `mapped_column()`)
- **Database Driver:** `aiosqlite` (Async SQLite connector)
- **Migrations:** Alembic with version-controlled revision files
- **Security & IAM:** JWT access tokens (15m), rotating refresh tokens (7d), Argon2 / Bcrypt cryptographic password hashing, token revocation / blacklisting table
- **Validation:** Pydantic v2 and `pydantic-settings`
- **Testing:** Pytest, `pytest-asyncio`, and `httpx`

---

## 2. Directory Structure

```text
microproject/backend/
├── app/
│   ├── main.py                     # FastAPI entrypoint, middleware, CORS & error handlers
│   ├── core/
│   │   ├── config.py               # Pydantic BaseSettings configuration
│   │   ├── database.py             # Async engine, sessionmaker, SQLite PRAGMA hooks
│   │   ├── security.py             # Password hashing and JWT generation/decoding
│   │   ├── exceptions.py           # Domain exceptions and uniform JSON error envelopes
│   │   ├── logging.py              # Structured logging
│   │   └── middleware.py           # Request ID tracking and execution latency timer
│   ├── models/                     # 31 SQLAlchemy 2.0 Declarative Models
│   │   ├── auth.py                 # User, Role, Permission, UserRole, RolePermission, RevokedToken
│   │   ├── profile.py              # Customer, Advisor, Underwriter profiles
│   │   ├── prospect.py             # Prospect, LeadSource, BehavioralSignal, LeadScore
│   │   ├── conversation.py         # Conversation, ConversationMessage
│   │   ├── product.py              # InsuranceProduct, ProductConfiguration
│   │   ├── recommendation.py       # CustomerQualification, Recommendation, Quote
│   │   ├── application.py          # Application, ApplicationDocument
│   │   ├── underwriting.py         # UnderwritingCase, UnderwritingReview
│   │   ├── agent.py                # AgentConfiguration, AgentExecution (prepared for Phase 3)
│   │   ├── audit.py                # AuditLog, ConsentRecord
│   │   └── system.py               # Notification, SystemSetting, FollowUp
│   ├── schemas/                    # Pydantic v2 Request & Response DTOs
│   ├── repositories/               # Data Access Object (DAO) Repository Layer
│   ├── services/                   # Business Logic & Deterministic Actuarial Calculations
│   ├── api/
│   │   ├── deps.py                 # Security dependencies (get_current_user, RBAC, tenant guardrails)
│   │   └── v1/                     # Modular API routers (/auth, /products, /quotes, /applications, etc.)
│   └── db/
│       ├── init_db.py              # Seeds 5 core roles, 16 permissions, and default admin user
│       └── seed_products.py        # Seeds baseline insurance products and tier configs
├── alembic/                        # Migration revisions
├── tests/                          # Automated Pytest suite (Auth, RBAC, Data Isolation)
├── requirements.txt                # Pinned dependencies
└── pyproject.toml                  # Pytest & tooling configurations
```

---

## 3. Quickstart & Local Setup

### 3.1 Activate Virtual Environment & Install Dependencies
```powershell
Set-Location "d:\My_Space\Sem 7\AAI\microproject\backend"
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### 3.2 Environment Configuration
Create or inspect `.env`:
```env
APP_NAME="PS-21 Insurance Acquisition & Onboarding Platform"
ENVIRONMENT=development
DATABASE_URL=sqlite+aiosqlite:///./ps21_insurance.db
JWT_SECRET=supersecret-ps21-insurance-platform-key-change-in-production
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=7
MISTRAL_API_KEY=
MISTRAL_MODEL=mistral-large-latest
FRONTEND_URL=http://localhost:3000
```

### 3.3 Apply Migrations & Seed Database
```powershell
# Run migrations
alembic upgrade head

# Seed core roles, permissions, and initial admin account
python -m app.db.init_db

# Seed baseline insurance products
python -m app.db.seed_products
```

Default administrator credentials:
- **Email:** `admin@ps21-insurance.com`
- **Password:** `AdminPass123!`

---

## 4. Running the Development Server

```powershell
uvicorn app.main:app --reload --port 8000
```
- **API Base:** `http://localhost:8000/api/v1`
- **Interactive Swagger Docs:** `http://localhost:8000/api/v1/docs`
- **ReDoc:** `http://localhost:8000/api/v1/redoc`

---

## 5. Running Automated Tests

```powershell
pytest -v
```
All 15 test suites verify:
- Registration, login, invalid password rejections, refresh token rotation, and logout token revocation.
- Role-Based Access Control (Customer vs. Advisor vs. Underwriter vs. Admin).
- Strict cross-customer data isolation (Customer B attempting to read or convert Customer A's quote is barred with `403 Forbidden`).
- System health and database connectivity.

