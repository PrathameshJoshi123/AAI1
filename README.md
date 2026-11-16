# PS-21 — Autonomous Conversational Insurance Acquisition & Onboarding Platform

[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688.svg?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Next.js](https://img.shields.io/badge/Next.js-16.0-black.svg?logo=next.js&logoColor=white)](https://nextjs.org)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.0+-3178C6.svg?logo=typescript&logoColor=white)](https://www.typescriptlang.org)
[![Python](https://img.shields.io/badge/Python-3.11%20%7C%203.13-3776AB.svg?logo=python&logoColor=white)](https://www.python.org)
[![LangGraph](https://img.shields.io/badge/LangGraph-Multi--Agent%20Orchestrator-blueviolet.svg)](https://langchain-ai.github.io/langgraph/)
[![Mistral AI](https://img.shields.io/badge/Mistral%20AI-LLM%20Engine-F54A2B.svg)](https://mistral.ai)
[![SQLite](https://img.shields.io/badge/SQLite-WAL%20Mode-003B57.svg?logo=sqlite&logoColor=white)](https://www.sqlite.org)
[![Tailwind CSS](https://img.shields.io/badge/Tailwind%20CSS-3.4-38B2AC.svg?logo=tailwind-css&logoColor=white)](https://tailwindcss.com)

A production-grade, full-stack, autonomous agentic platform engineered for end-to-end retail insurance acquisition, conversational needs assessment, actuarial premium calculation, KYC document intake, and human-in-the-loop (HITL) underwriting escalation.

---

## 📑 Table of Contents

1. [Executive Overview](#-executive-overview)
2. [Key Portals & Dashboards](#-key-portals--dashboards)
3. [Core Architectural Pillars](#-core-architectural-pillars)
4. [Technology Stack](#-technology-stack)
5. [Multi-Agent Roster (LangGraph)](#-multi-agent-roster-langgraph)
6. [Repository Architecture](#-repository-architecture)
7. [Getting Started & Local Setup](#-getting-started--local-setup)
   - [One-Click Launch (`start.bat`)](#1-one-click-launch-recommended)
   - [Manual Backend Setup](#2-backend-manual-setup)
   - [Manual Frontend Setup](#3-frontend-manual-setup)
   - [Database Migrations & Seeding](#4-database-migrations--seeding)
8. [Configuration & Environment Variables](#-configuration--environment-variables)
9. [Pre-configured User Credentials](#-pre-configured-user-credentials)
10. [Automated Testing Suite](#-automated-testing-suite)
11. [Architecture & Sequence Diagrams](#-architecture--sequence-diagrams)
12. [Compliance & Architectural Tenets](#-compliance--architectural-tenets)

---

## 🌟 Executive Overview

Traditional retail insurance acquisition is plagued by clunky static forms, disconnected actuarial calculations, opaque underwriting, and high customer drop-off. **PS-21** redefines this lifecycle through an **autonomous, agentic, multi-agent AI architecture** orchestrated via **LangGraph** and powered exclusively by **Mistral AI**. 

Unlike simple conversational bots, PS-21 pairs conversational intelligence with **deterministic actuarial calculation engines**, strict **Role-Based Access Control (RBAC)**, real-time **customer data isolation**, and **Human-in-the-Loop (HITL)** safeguards to ensure regulatory compliance under IRDAI guidelines and the Digital Personal Data Protection (DPDP) Act 2023.

---

## 🖥️ Key Portals & Dashboards

The platform serves three primary stakeholder experiences within a unified, design-consistent application:

### 1. Customer Experience Portal (`/customer`)
- **Conversational Assistant (`/customer/chat`):** Natural language exploration of coverage needs, policy recommendations, and instant query answering.
- **Interactive Needs Assessment (`/customer/needs-assessment` & `/customer/calculator`):** Guided financial and lifestyle questionnaire calculating optimal coverage requirements.
- **Indicative Actuarial Quotes (`/customer/quotes` & `/customer/quotes/[id]`):** Instant, transparent premium breakdown (Base Rate + Age Factor + BMI + Tobacco Loading + Add-ons) with an interactive **"Email Me This Quote"** drawer.
- **Self-Serve Onboarding & KYC (`/customer/onboarding` & `/customer/documents`):** Seamless application submission with secure KYC identity, address, and medical document uploads.
- **Consent & Profile Management (`/customer/profile` & `/customer/consent`):** Explicit DPDP consent logging, revocation options, and granular notification preference toggles.

### 2. Advisor & Underwriter Workstation (`/advisor`)
- **HITL Review Queue (`/advisor/queue` & `/advisor/reviews`):** Prioritized inbox for cases flagged with elevated risk (high BMI, smoker status, critical medical declarations).
- **Case Investigation Dossier (`/advisor/cases/[id]` & `/advisor/underwriting/[caseNumber]`):** Deep-dive workspace displaying full customer profile, actuarial breakdowns, document OCR verification, and risk signal timelines.
- **Underwriting Decision Engine:** Actions for direct approval, proposal loading, specific document requisitions, or formal rejection with automated customer notifications.
- **Lead Pipeline (`/advisor/leads`):** Advisor assignment tracking and proactive follow-up coordination.

### 3. Executive & Admin Control Center (`/admin`)
- **Agent Intelligence Suite (`/admin/agents`):** Real-time monitoring of all 18+ LangGraph agents, execution states, token usage, latency metrics, and kill-switch controls.
- **Conversion & Funnel Analytics (`/admin/analytics` & `/admin/funnel`):** Drop-off rate tracking across discovery, quote generation, document upload, and underwriting issuance.
- **Pricing Matrix Manager (`/admin/products`):** Dynamic actuarial pricing tables, base rates, multipliers, and policy configuration without code deployment.
- **Audit & Governance Explorer (`/admin/audit`):** Complete, immutable audit log of every system event, auth attempt, and data access.
- **Integration & Notification Probes (`/admin/integrations`):** Live SMTP email delivery testing, connection monitoring, and error reporting.

---

## 🏛️ Core Architectural Pillars

```
+---------------------------------------------------------------------------------+
|                                 Next.js 16 UI                                  |
|     Customer Portal     |     Advisor Workstation     |     Admin Dashboard     |
+---------------------------------------------------------------------------------+
                                         |
                                (REST & JSON / SSE)
                                         v
+---------------------------------------------------------------------------------+
|                                FastAPI Backend                                  |
|   +-------------------------------------------------------------------------+   |
|   |                      Layered Architecture                               |   |
|   |   API Routers -> Auth & RBAC -> Pydantic Validation -> Service Layer    |   |
|   +-------------------------------------------------------------------------+   |
|                                         |                                       |
|               +-------------------------+-------------------------+             |
|               v                                                   v             |
|   +-----------------------+                           +---------------------+   |
|   |  LangGraph Agentic    |                           | Actuarial Engine    |   |
|   |  State Machine        |                           | & Business Services |   |
|   |  (Mistral AI LLM)     |                           | (Deterministic)     |   |
|   +-----------------------+                           +---------------------+   |
|               |                                                   |             |
|               +-------------------------+-------------------------+             |
|                                         v                                       |
|   +-------------------------------------------------------------------------+   |
|   |           Repository DAO Layer (SQLAlchemy 2.0 Async / Mapped)           |   |
|   +-------------------------------------------------------------------------+   |
+---------------------------------------------------------------------------------+
                                         |
                                (Async SQLite Driver)
                                         v
+---------------------------------------------------------------------------------+
|                       SQLite 3 (WAL Mode + Foreign Keys)                       |
|          31 Relational Models: Auth, Quotes, Applications, Cases, Audit         |
+---------------------------------------------------------------------------------+
```

- **Strict "No Hallucination / No Fallback" Rule:** Actuarial premiums, eligibility scores, and underwriting rules are calculated **deterministically** by Python service classes. LLMs are never allowed to fabricate numerical rates, policy approvals, or claim decisions.
- **Strict "No Mock Data" Policy:** The system never returns fake success responses or mock payloads when integrations (e.g. SMTP or Mistral) are unavailable. Failures fail visibly with actionable diagnostic logs.
- **Human-in-the-Loop (HITL):** Cases exceeding algorithmic risk thresholds automatically pause the agent graph, checkpoint the state into the database, and escalate to an authorized Underwriter.
- **Tenant & Cross-Customer Isolation:** Enforced via backend dependency injection (`deps.py`). Customer A cannot view, mutate, or convert Customer B's quotes or documents under any circumstances (`403 Forbidden`).

---

## 💻 Technology Stack

### Frontend
- **Framework:** Next.js 16 (React 19, App Router, Server Components by default)
- **Language:** TypeScript 5.0+
- **Styling:** Tailwind CSS with a curated, professional White-and-Blue enterprise theme
- **UI Components:** [shadcn/ui](https://ui.shadcn.com/) (directly imported native primitives)
- **Icons:** Lucide React
- **Forms & Validation:** React Hook Form + Zod
- **Data Visualizations:** Recharts (Conversion funnels, agent latency, sales metrics)

### Backend
- **Framework:** FastAPI 0.115+ (ASGI, Async execution)
- **Language:** Python 3.11+ / 3.13
- **ORM:** SQLAlchemy 2.0 (Modern Declarative `Mapped[T]` & `mapped_column()`)
- **Database Driver:** `aiosqlite` (Asynchronous SQLite)
- **Database Engine:** SQLite 3 with Write-Ahead Logging (`PRAGMA journal_mode=WAL; PRAGMA foreign_keys=ON;`)
- **Migrations:** Alembic
- **Security & IAM:** JWT Access Tokens (15 min), Rotating Refresh Tokens (7 days), Argon2/Bcrypt password hashing, Token Revocation List
- **Validation:** Pydantic v2 & `pydantic-settings`
- **Email Delivery:** Asynchronous SMTP via `aiosmtplib` with Jinja2 HTML templating

### Artificial Intelligence & Multi-Agent Orchestration
- **LLM Engine:** Mistral AI exclusively (`mistral-large-latest` / `ministral-8b-2512`)
- **Agent Orchestrator:** LangGraph state machine with memory checkpointers and interrupt hooks
- **Tool Protocol:** Structured Pydantic tools with explicit granular execution permissions

---

## 🤖 Multi-Agent Roster (LangGraph)

PS-21 implements an ensemble of 18+ specialized autonomous agents operating within explicit state graph boundaries:

| Agent Name | Primary Responsibility | Input / Trigger | Output Artifact |
| :--- | :--- | :--- | :--- |
| **Prospect Intelligence Agent** | Identifies prospect persona and intent | Chat queries & behavioral signals | Prospect profile & intent classification |
| **Lead Qualification Agent** | Evaluates customer eligibility & fit | Questionnaire responses | Qualification score & triage category |
| **Needs Assessment Agent** | Analyzes lifestyle, liabilities & dependents | Customer financial disclosures | Recommended coverage limits & term length |
| **Insurance Explainer Agent** | Explains complex terms, riders, and exclusions | Customer inquiry prompts | Structured, jargon-free explanations |
| **Recommendation Agent** | Matches customer profile with product catalog | Needs assessment output | Tiered product recommendations (Silver/Gold/Platinum) |
| **Quote Coordination Agent** | Invokes actuarial engine for live pricing | Selected product configuration | Formal indicative quote object |
| **Risk Information Agent** | Ingests disclosures and calculates baseline risk | Health & occupation answers | Risk rating factor |
| **Document Review Agent** | Inspects uploaded KYC & medical records | Uploaded file metadata & OCR | Document verification status |
| **Underwriting Escalation Agent** | Packages edge cases for human review | High-risk thresholds | Underwriting case file with recommendations |
| **Conversational Advisor Agent** | Guides user through proposal completion | Customer dialogue | Validated application proposal |
| **Onboarding Agent** | Coordinates payment and issuance prerequisites | Accepted quote & proposal | Completed application record |
| **Drop-off Detection Agent** | Analyzes stall patterns and abandoned quotes | Inactivity triggers | Engagement re-entry prompt |
| **Follow-up Coordination Agent** | Schedules reminders and notification tasks | Incomplete user milestones | Notification task record |
| **Customer Support Agent** | Resolves onboarding friction and technical inquiries | Help requests | Resolution guidance or ticket escalation |
| **Conversion Analytics Agent** | Tracks funnel performance and agent effectiveness | Session transition logs | Funnel metrics and drop-off reports |
| **Compliance Monitoring Agent** | Audits conversations for regulatory compliance | Chat logs & disclosures | Compliance flag and audit entries |
| **Diagnostic Agent** | Performs system health checks and connectivity probes | Admin health requests | Health report across LLM, DB, and SMTP |

---

## 📁 Repository Architecture

```text
microproject/
├── backend/                             # Asynchronous FastAPI backend
│   ├── alembic/                         # Database migration versions
│   ├── app/
│   │   ├── ai/                          # LangGraph agents, Mistral client & tools
│   │   │   ├── agents/definitions/      # 18+ Specialized Agent implementations
│   │   │   ├── client/                  # Mistral API client & structured outputs
│   │   │   ├── graph/                   # LangGraph state machine, router, checkpoints
│   │   │   ├── observability/           # Execution audit & latency trackers
│   │   │   └── tools/                   # Registered agent tools & permission guards
│   │   ├── api/v1/                      # 30+ Modular REST routers (/auth, /quotes, etc.)
│   │   ├── core/                        # Config, async database engine, security & exceptions
│   │   ├── db/                          # Database seed scripts (roles, users, products)
│   │   ├── models/                      # 31 SQLAlchemy 2.0 declarative models
│   │   ├── repositories/                # Clean Data Access Object (DAO) layer
│   │   ├── schemas/                     # Pydantic v2 DTOs and validation schemas
│   │   ├── services/                    # Deterministic business & actuarial services
│   │   └── main.py                      # FastAPI application entrypoint
│   ├── storage/                         # Local uploaded KYC documents & files
│   ├── tests/                           # Pytest suite (AI, Leads, Auth, RBAC, Isolation)
│   ├── ps21_insurance.db                # SQLite database (generated on migration)
│   ├── pyproject.toml                   # Python tooling configuration
│   └── requirements.txt                 # Pinned backend dependencies
│
├── frontend/                            # Next.js 16 Web Application
│   ├── public/                          # Static assets and public icons
│   ├── src/
│   │   ├── app/                         # App Router pages and route groups
│   │   │   ├── (auth)/                  # Login and customer registration
│   │   │   ├── admin/                   # Admin & Executive Dashboard pages
│   │   │   ├── advisor/                 # Advisor & Underwriter Workstation pages
│   │   │   ├── customer/                # Customer Portal pages (chat, quotes, KYC)
│   │   │   ├── layout.tsx               # Root layout with global styling
│   │   │   └── page.tsx                 # Platform landing & portal selector
│   │   ├── components/                  # shadcn/ui components & specialized widgets
│   │   ├── hooks/                       # Custom React hooks (auth, quotes, notifications)
│   │   ├── lib/                         # Axios client, utils, formatters
│   │   ├── services/                    # Frontend API client service modules
│   │   └── types/                       # TypeScript interfaces and DTOs
│   ├── package.json                     # Frontend scripts and dependencies
│   ├── tailwind.config.ts               # Tailwind CSS theme tokens
│   └── tsconfig.json                    # TypeScript compiler configuration
│
├── docs/                                # Specification plans (Phases 1-11 & Master Prompt)
├── start.bat                            # Double-click launcher for Windows
├── AGENTS.md                            # Comprehensive AI development rules & tenets
├── .env                                 # Root environment configuration
└── README.md                            # Project documentation (this file)
```

---

## 🚀 Getting Started & Local Setup

### Prerequisites
- **Node.js:** v18.17+ or v20+ (`npm` or `pnpm`)
- **Python:** v3.11, 3.12, or 3.13
- **Git**

---

### 1. One-Click Launch (Recommended)
On Windows systems, execute the bundled batch script from the `microproject` root:

```cmd
start.bat
```

This will automatically:
1. Verify backend and frontend directory integrity.
2. Launch the FastAPI server in a dedicated console at **`http://127.0.0.1:8000`**.
3. Launch the Next.js development server in a dedicated console at **`http://localhost:3000`**.
4. Display links to all interactive dashboards and Swagger API documentation.

---

### 2. Backend Manual Setup

Navigate to the `backend` folder:
```powershell
cd backend
```

Create and activate a virtual environment:
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Install pinned dependencies:
```powershell
pip install -r requirements.txt
```

Run database migrations:
```powershell
alembic upgrade head
```

Seed initial roles, permissions, administrative user, and baseline insurance products:
```powershell
python -m app.db.init_db
python -m app.db.seed_products
python -m app.db.seed_pricing_matrices
python -m app.db.seed_leads
```

Start the FastAPI development server:
```powershell
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```
- **REST API Base:** `http://127.0.0.1:8000/api/v1`
- **Swagger Documentation:** `http://127.0.0.1:8000/docs`
- **ReDoc Interactive Docs:** `http://127.0.0.1:8000/redoc`

---

### 3. Frontend Manual Setup

In a new terminal, navigate to the `frontend` folder:
```powershell
cd frontend
```

Install dependencies:
```powershell
npm install
```

Start the Next.js development server:
```powershell
npm run dev
```

Access the web interface at **`http://localhost:3000`**.

---

## ⚙️ Configuration & Environment Variables

Create or configure `.env` in the `microproject/` root (or `microproject/backend/.env`):

```env
# Application Details
APP_NAME="PS-21 Insurance Acquisition & Onboarding Platform"
ENVIRONMENT="development"
DEBUG=true
PORT=8000

# Database (Async SQLite)
DATABASE_URL="sqlite+aiosqlite:///./ps21_insurance.db"

# Security & JWT Tokens
JWT_SECRET="supersecret-ps21-insurance-platform-key-change-in-production"
JWT_ALGORITHM="HS256"
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=7

# Mistral AI (Required for Multi-Agent Workflows)
MISTRAL_API_KEY="your-mistral-api-key-here"
MISTRAL_MODEL="ministral-8b-2512"

# Frontend Integration
FRONTEND_URL="http://localhost:3000"

# Email Notification Engine (SMTP Configuration)
SMTP_HOST="smtp.gmail.com"
SMTP_PORT=587
SMTP_USER="your-email@gmail.com"
SMTP_PASSWORD="your-app-password"
SMTP_FROM_EMAIL="notifications@ps21-insurance.com"
SMTP_FROM_NAME="PS-21 Insurance Platform"
SMTP_USE_TLS=true
SMTP_TIMEOUT_SECONDS=10
```

---

## 🔑 Pre-configured User Credentials

Running `python -m app.db.init_db` creates the default administrator account:

| Role | Email Address | Password | Permissions |
| :--- | :--- | :--- | :--- |
| **Admin / Owner** | `admin@ps21-insurance.com` | `AdminPass123!` | Full administrative, pricing, agent, and audit access |

*Note: Retail customers can be registered instantly via the web registration screen at `http://localhost:3000/register`.*

---

## 🧪 Automated Testing Suite

The backend includes a comprehensive test suite covering authentication, RBAC, tenant data isolation, LangGraph state flows, and SMTP notifications:

```powershell
cd backend
pytest -v
```

### Verified Test Suites:
- `test_auth.py`: User registration, password hashing verification, token refresh rotation, and logout token revocation.
- `test_rbac.py`: Role permission matrix enforcement (Customer vs. Advisor vs. Underwriter vs. Admin).
- `test_data_isolation.py`: Cross-customer boundary checks (attempts by Customer B to access Customer A's quotes/applications fail with `403 Forbidden`).
- `test_email_notifications.py`: SMTP connection failure safety, templating validation, and error logging without fake success masking.
- `test_langgraph_flow.py`: Multi-agent state transitions, tool validation, and deterministic output conformance.
- `test_human_in_the_loop.py`: Checkpoint saving and graph pause/resume under underwriting escalation.

---

## 📊 Architecture & Sequence Diagrams

High-resolution visual diagrams representing the platform's architecture and execution sequences are available in the repository root:

- **System Architecture:** `system_architecture_diagram_1794844009941.jpg`
- **LangGraph Multi-Agent State Machine:** `langgraph_multiagent_state_machine_1794851960290.jpg`
- **Actuarial Quoting Sequence:** `actuarial_quoting_sequence_diagram_1794852289428.jpg`
- **Automated Underwriting & HITL Escalation:** `automated_underwriting_hitl_sequence_diagram_1794852297915.jpg`
- **Entity Relationship Diagram (ERD):** `ps21_erd_diagram_1794852310009.jpg`
- **Performance Benchmarks & Latency:** `ps21_performance_benchmarks_figure1.jpg`

---

## 📜 Compliance & Architectural Tenets

All engineering in this repository strictly adheres to the standards defined in [`AGENTS.md`](file:///d:/My_Space/Sem%207/AAI/microproject/AGENTS.md):

1. **No Silent Fallbacks:** If Mistral AI or the SMTP provider is unavailable or misconfigured, the platform throws a transparent error and preserves state safely. It will never return fabricated quotes, mock approvals, or simulated AI answers.
2. **Zero Hardcoded Business Logic:** Premiums, eligibility thresholds, and product rules are maintained in dynamic database models and pricing matrices—never embedded inside prompts or UI components.
3. **DPDP Act & IRDAI Alignment:** Full audit logs, explicit consent collection before data intake, transparent risk assessment explanations, and strict user data segregation.
4. **Professional UI Standards:** Strictly enforced single visual identity—light/white clean surfaces, subtle slate borders, and professional blue accents, eliminating chaotic dark modes or unvetted design variations.

---

*PS-21 Insurance Acquisition & Onboarding Platform — Developed for Sem 7 Applied Artificial Intelligence (AAI).*
