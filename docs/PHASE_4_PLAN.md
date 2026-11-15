# PS-21 — Phase 4 Technical Specification & Implementation Plan
## Prospect Ingestion, Behavioral Signal Tracking, Deterministic Lead Scoring & Advisor Queue Management

**Project:** PS-21 Conversational Insurance Acquisition & Onboarding Platform  
**Target Directories:** `microproject/backend` & `microproject/frontend`  
**Parent Guidelines:** `microproject/AGENTS.md` & `microproject/docs/Master_prompt.md`  
**Status:** Ready for Execution (Planning Document)  

---

## 1. Executive Summary & Objectives

The primary objective of **Phase 4** is to engineer the end-to-end **Prospect & Lead Acquisition and Management Subsystem** for the PS-21 insurance platform. Building on the core authentication, RBAC, and SQLite models from Phase 2, and the Mistral/LangGraph AI infrastructure from Phase 3, Phase 4 bridges anonymous visitor engagement with structured, auditable sales advisory workflows.

Phase 4 establishes:
1. **Multi-Channel Prospect Ingestion & Source Attribution:** Deterministic capture of inbound prospects across web, mobile, partner referral, and campaign channels, recording UTM parameters (`utm_source`, `utm_campaign`, `utm_medium`, `utm_term`, `utm_content`) and referrer context.
2. **Strict Consent Recording & Privacy Guardrails (DPDP & IRDAI Compliance):** Enforcing the non-negotiable rule that **anonymous behavioral signals must never automatically be treated as permission to identify or contact a person**. Outbound communications and advisor outreach are blocked unless explicit, versioned, timestamped consent is verified in `consent_records`.
3. **Real-Time Behavioral Signal Ingestion:** Asynchronous recording of client-side engagement signals (`page_view`, `time_on_page`, `quote_attempt`, `coverage_calculator_used`, `comparison_viewed`, `faq_opened`, `drop_off_step`, `chat_initiated`) linked securely to prospect or anonymous session tokens.
4. **Deterministic Lead Scoring Service with Explainable Factors:** Calculation of dynamic lead scores (0–100) using configurable criteria stored in the database. Every score is fully auditable through stored contributing factors (`score_factors_json`), rejecting black-box scores and fabricated metrics.
5. **Dynamic Customer Segmentation:** Automatic and rule-based categorization into actionable cohorts (`High Intent`, `Warm Consideration`, `Top-of-Funnel`, `Dormant / Drop-off`, `Price Sensitive`).
6. **Workload-Aware Lead Assignment Engine:** Deterministic distribution of qualified leads to insurance advisors based on advisor availability, current active workload (`max_active_cases`), and product specialization, with manual override capabilities for administrators.
7. **Unified Lead Activity Timeline:** Consolidated chronological feed aggregating creation events, consent grants/revocations, behavioral milestones, AI conversational intent summaries, score recalculations, and advisor notes.
8. **Enterprise UI Implementation (shadcn/ui & Strict White Theme):**
   - **Admin Lead Management Interface (`/admin/leads`):** High-density TanStack data table with multi-dimensional filtering, search, pagination, detailed lead inspector drawer, and manual advisor assignment dialog.
   - **Advisor Assigned-Leads Workspace (`/advisor/leads`):** Focused queue for insurance advisors showing authorized assigned leads, contactability status, score breakdown, recent activity, and quick-action outreach controls.
9. **Mistral AI Prospect Intelligence Agent:** An authorized LangGraph agent that synthesizes unstructured conversation messages and behavioral footprints into a structured prospect intelligence summary without ever hallucinating or inventing customer signals.
10. **Comprehensive Pytest & Integration Test Suite:** 100% verified test coverage for lead ingestion, consent boundaries, deterministic scoring math, advisor workload constraints, and role-based data isolation.

---

## 2. Core Mandates & Non-Negotiable Phase 4 Rules

In strict adherence to `microproject/AGENTS.md` and `microproject/docs/Master_prompt.md`, the following architectural constraints are enforced across all Phase 4 code:

| Mandate | Specification & Constraint | Strict Enforcement Mechanism |
| :--- | :--- | :--- |
| **Consent Precondition** | Anonymous behavioral signals must **never** be treated as permission to contact. | Outbound communication endpoints (SMS, email, phone queue) verify active records in `consent_records` before executing. If consent is absent or revoked, contact actions return HTTP 403 / `ConsentRequiredException`. |
| **Deterministic Scoring** | Lead scores must be calculated via transparent, deterministic math from database-configured rules. | The scoring engine queries rules from the database (`system_settings` or `lead_scoring_rules`). Scores store an itemized JSON breakdown of every positive and negative point factor. |
| **No LLM Fabrication** | Mistral may analyze unstructured text for intent, but must **never** invent customer signals or demographic data. | Prompt guardrails and Pydantic validation reject any hallucinated attributes. Customer signals originate solely from verified HTTP ingestion events. |
| **Advisor Case Scoping** | Insurance advisors must **only** access leads assigned to them. | FastAPI dependency `require_advisor_scope` restricts advisor queries to `prospects.assigned_advisor_id == current_user.advisor.id`. Unassigned queues require supervisor permissions. |
| **Enterprise White Theme** | All frontend interfaces must follow the clean white SaaS aesthetic. | Zero dark mode classes (`dark:`), no black card backgrounds, no gratuitous gradients. Only white surfaces (`bg-white`), slate borders (`border-slate-200`), navy typography (`text-slate-900`), and restrained blue accents (`bg-blue-600`). |
| **Actual shadcn/ui Components** | Use directly imported shadcn/ui primitives. | Tables use `@tanstack/react-table`, dialogs use `@/components/ui/dialog`, sheets use `@/components/ui/sheet`, tabs use `@/components/ui/tabs`. No mock or homemade approximations. |
| **Full Audit Trail** | Every assignment change, status progression, and consent revocation must be logged. | Service layer automatically creates `AuditLog` entries with user ID, IP address, resource type (`Prospect`), and old/new change deltas. |

---

## 3. Technology Stack & Architectural Positioning

```mermaid
flowchart TB
    subgraph Frontend [Next.js 16 App Router - Strict White Theme]
        AdminLeads["/admin/leads (TanStack Table, Filters, Detail Sheet)"]
        AdvisorQueue["/advisor/leads (Assigned Queue, Quick Actions)"]
        TrackerHook["useProspectTracker (Session Beacon & Signal Collector)"]
    end

    subgraph API [FastAPI REST Gateway - /api/v1]
        ProspectRouter["/api/v1/prospects"]
        SignalRouter["/api/v1/signals"]
        ConsentRouter["/api/v1/consent"]
        AdvisorLeadRouter["/api/v1/advisor/leads"]
    end

    subgraph ServiceLayer [Deterministic Business Services]
        LeadService[Lead Management Service]
        ScoringEngine[Deterministic Lead Scoring Service]
        AssignmentEngine[Workload-Aware Assignment Service]
        TimelineAggregator[Activity Timeline Aggregator]
    end

    subgraph AISubstrate [LangGraph & Mistral Substrate (Phase 3)]
        ProspectIntelAgent[Prospect Intelligence Agent]
        StateCheckpointer[(SQLite State Checkpointer)]
    end

    subgraph Database [SQLite Relational Storage via SQLAlchemy 2.0 Async]
        ProspectsTable[(prospects)]
        SignalsTable[(behavioral_signals)]
        ScoresTable[(lead_scores)]
        ConsentTable[(consent_records)]
        SourcesTable[(lead_sources)]
        AuditTable[(audit_logs)]
    end

    TrackerHook -->|Anonymous Beacon| SignalRouter
    AdminLeads -->|Admin RBAC| ProspectRouter
    AdvisorQueue -->|Advisor Scoped| AdvisorLeadRouter

    ProspectRouter --> LeadService
    SignalRouter --> LeadService
    ConsentRouter --> LeadService
    AdvisorLeadRouter --> LeadService

    LeadService --> ScoringEngine
    LeadService --> AssignmentEngine
    LeadService --> TimelineAggregator
    LeadService --> ProspectIntelAgent

    ScoringEngine --> Database
    AssignmentEngine --> Database
    TimelineAggregator --> Database
    ProspectIntelAgent --> StateCheckpointer
```

---

## 4. Database Schema Enhancements & Migration Plan

The initial schema from Phase 2 provides foundational tables (`prospects`, `lead_sources`, `behavioral_signals`, `lead_scores`, `consent_records`, `follow_ups`). Phase 4 introduces precise enhancements required for advisor assignment, segmentation, and deterministic scoring rule storage.

### 4.1 Schema Additions & Modifications

#### 1. `prospects` Table Modifications:
- Add `assigned_advisor_id`: `String(36)`, Nullable, Foreign Key referencing `advisors.id` (`ondelete="SET NULL"`), indexed.
- Add `assigned_at`: `DateTime(timezone=True)`, Nullable.
- Add `segment`: `String(50)`, Default `"top_of_funnel"`, Not Null, indexed (values: `top_of_funnel`, `warm_consideration`, `high_intent`, `price_sensitive`, `dormant`).
- Add `last_activity_at`: `DateTime(timezone=True)`, Default `utc_now`, Not Null, indexed.
- Add `estimated_budget_min`: `Numeric(12, 2)`, Nullable.
- Add `estimated_budget_max`: `Numeric(12, 2)`, Nullable.
- Add `target_insurance_type`: `String(50)`, Nullable (e.g. `term_life`, `health`, `motor`).

#### 2. `lead_scoring_rules` Table (New Deterministic Entity):
Enforces the strict rule against hardcoding scoring criteria in Python code.
```python
class LeadScoringRule(Base, TimestampMixin):
    __tablename__ = "lead_scoring_rules"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    rule_code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    category: Mapped[str] = mapped_column(String(50), nullable=False) # profile, intent, engagement, consent, penalty
    rule_name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(String(255), nullable=False)
    point_value: Mapped[int] = mapped_column(Integer, nullable=False) # positive (e.g. +25) or negative (e.g. -50)
    condition_json: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=False) # evaluation logic parameters
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
```

#### 3. Default Seed Matrix for `lead_scoring_rules`:
- `RULE_PROFILE_PHONE`: +15 points if verified phone number provided.
- `RULE_PROFILE_EMAIL`: +10 points if valid email address provided.
- `RULE_PROFILE_NAME`: +5 points if full legal name provided.
- `RULE_INTENT_QUOTE_STARTED`: +25 points if quote calculation initiated.
- `RULE_INTENT_CALCULATOR_USED`: +15 points if coverage slider interacted with.
- `RULE_INTENT_COMPARISON`: +15 points if 2+ insurance plans compared.
- `RULE_ENGAGEMENT_DWELL_TIME`: +10 points if cumulative dwell time > 120 seconds.
- `RULE_ENGAGEMENT_MULTI_PAGE`: +10 points if 3+ distinct product/policy pages visited.
- `RULE_ENGAGEMENT_RETURN_VISIT`: +15 points if second session within 72 hours.
- `RULE_CONSENT_MARKETING`: +10 points if marketing contact consent explicitly granted.
- `RULE_CONSENT_REVOKED`: -50 points if consent is subsequently revoked.
- `RULE_PENALTY_INACTIVITY_30D`: -20 points if no activity recorded for > 30 days.

### 4.2 Alembic Migration Plan (`versions/xxxx_phase4_lead_management.py`)
- Revision script adds columns `assigned_advisor_id`, `assigned_at`, `segment`, `last_activity_at`, `estimated_budget_min`, `estimated_budget_max`, `target_insurance_type` to `prospects`.
- Creates `lead_scoring_rules` table with unique constraint on `rule_code`.
- Seeds the initial 12 deterministic scoring rules and default `lead_sources` (`web_direct`, `google_organic`, `google_cpc`, `partner_aggregator`, `mobile_referral`).

---

## 5. Backend Directory Structure & Component Inventory

```text
microproject/backend/
├── app/
│   ├── models/
│   │   ├── prospect.py                   # Updated with LeadScoringRule & enhanced Prospect fields
│   │   └── ...
│   │
│   ├── schemas/
│   │   ├── prospect.py                   # Comprehensive Pydantic request/response schemas
│   │   ├── signal.py                     # Signal ingestion schemas & event types
│   │   └── consent.py                    # Consent grant/revocation & verification schemas
│   │
│   ├── repositories/
│   │   ├── prospect_repository.py        # Prospect CRUD, filtered search, pagination, stats
│   │   ├── signal_repository.py          # Behavioral signal batch insertion & session queries
│   │   ├── score_repository.py           # Lead score historical tracking & factors lookup
│   │   ├── scoring_rule_repository.py    # Database-backed scoring rule configuration
│   │   └── consent_repository.py         # Legal consent status checks & revocation
│   │
│   ├── services/
│   │   ├── lead_service.py               # Orchestrates lead lifecycle, updates, and status transitions
│   │   ├── lead_scoring_service.py       # Deterministic scoring calculation engine & factor explainer
│   │   ├── lead_assignment_service.py    # Advisor workload-aware matching & assignment engine
│   │   ├── consent_service.py            # DPDP/IRDAI consent enforcement & validation guardrails
│   │   └── timeline_service.py           # Unified chronological activity timeline aggregator
│   │
│   ├── ai/
│   │   └── agents/definitions/
│   │       └── prospect_intel_agent.py   # LangGraph agent for extracting stated intent from chat transcripts
│   │
│   └── api/v1/
│       ├── prospects.py                  # Admin prospect CRUD, search, filter, segmentation
│       ├── signals.py                    # Client-side behavioral signal ingestion
│       ├── consent.py                    # Consent capture and verification endpoints
│       └── advisor_leads.py              # Advisor-scoped lead queue and action endpoints
│
└── tests/
    └── leads/                            # Dedicated Phase 4 Automated Pytest Suite
        ├── __init__.py
        ├── conftest.py                   # Fixtures for prospects, advisors, rules, and signals
        ├── test_prospect_ingestion.py    # Source tracking, UTM parsing, and deduplication
        ├── test_consent_enforcement.py   # Outbound blocking when consent is absent/revoked
        ├── test_deterministic_scoring.py # Mathematical accuracy and factor explainability
        ├── test_advisor_assignment.py    # Round-robin, specialization, and max capacity limits
        ├── test_prospect_timeline.py     # Aggregated event chronology verification
        ├── test_advisor_rbac_scoping.py  # Isolation: advisors cannot view other advisors' leads
        └── test_prospect_intel_agent.py  # LangGraph unstructured intent extraction (no hallucinations)
```

---

## 6. Detailed Backend Specifications

### 6.1 Pydantic Validation Schemas (`schemas/prospect.py`, `schemas/signal.py`, `schemas/consent.py`)

#### Prospect Creation & Filtering Schemas:
```python
class ProspectCreate(BaseModel):
    name: Optional[str] = Field(None, max_length=100)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, pattern=r"^\+?[1-9]\d{1,14}$")
    source_name: str = Field("web_direct", max_length=50)
    utm_source: Optional[str] = None
    utm_medium: Optional[str] = None
    utm_campaign: Optional[str] = None
    utm_term: Optional[str] = None
    utm_content: Optional[str] = None
    target_insurance_type: Optional[str] = None
    initial_session_id: str = Field(..., min_length=10)

class ProspectUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    status: Optional[str] = None
    target_insurance_type: Optional[str] = None
    estimated_budget_min: Optional[float] = None
    estimated_budget_max: Optional[float] = None

class ProspectFilterParams(BaseModel):
    query: Optional[str] = None
    status: Optional[List[str]] = None
    segment: Optional[List[str]] = None
    source_id: Optional[int] = None
    assigned_advisor_id: Optional[str] = None
    min_score: Optional[float] = None
    max_score: Optional[float] = None
    consented_only: bool = False
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    page: int = Field(1, ge=1)
    page_size: int = Field(20, ge=1, le=100)
    sort_by: str = Field("last_activity_at", pattern=r"^(last_activity_at|created_at|score)$")
    sort_order: str = Field("desc", pattern=r"^(asc|desc)$")
```

#### Behavioral Signal Schemas:
```python
class SignalIngestRequest(BaseModel):
    session_id: str = Field(..., min_length=8)
    prospect_id: Optional[str] = None
    signal_type: str = Field(..., pattern=r"^(page_view|time_on_page|quote_attempt|coverage_calculator_used|comparison_viewed|faq_opened|drop_off_step|chat_initiated)$")
    payload: Dict[str, Any] = Field(default_factory=dict)
    client_timestamp: datetime = Field(default_factory=utc_now)

class BatchSignalIngestRequest(BaseModel):
    events: List[SignalIngestRequest] = Field(..., min_items=1, max_items=50)
```

#### Consent Schemas:
```python
class ConsentGrantRequest(BaseModel):
    prospect_id: str
    consent_type: str = Field(..., pattern=r"^(terms_of_service|privacy_policy|marketing_contact|quote_generation|medical_record_access)$")
    consent_version: str = Field("2026.1", max_length=20)
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None

class ConsentRevokeRequest(BaseModel):
    prospect_id: str
    consent_type: str
    reason: Optional[str] = None
```

#### Read & Detailed DTOs:
```python
class ScoreFactorRead(BaseModel):
    rule_code: str
    rule_name: str
    category: str
    points_awarded: int
    rationale: str

class LeadScoreRead(BaseModel):
    score: float
    calculated_at: datetime
    factors: List[ScoreFactorRead]

class ProspectDetailRead(BaseModel):
    id: str
    name: Optional[str]
    email: Optional[str]
    phone: Optional[str]
    status: str
    segment: str
    target_insurance_type: Optional[str]
    source_name: Optional[str]
    assigned_advisor_id: Optional[str]
    assigned_advisor_name: Optional[str]
    assigned_at: Optional[datetime]
    created_at: datetime
    last_activity_at: datetime
    latest_score: Optional[LeadScoreRead]
    active_consents: List[str]
    can_contact: bool # True only if marketing_contact consent is active
    signals_count: int
```

---

### 6.2 Deterministic Lead Scoring Engine (`services/lead_scoring_service.py`)

The scoring engine implements fully transparent, reproducible scoring without heuristic guesswork or LLM hallucinations.

```mermaid
flowchart TD
    Trigger[Trigger: New Signal / Profile Update / Consent Change] --> FetchRules[Fetch Active Rules from lead_scoring_rules in SQLite]
    FetchRules --> LoadData[Load Prospect, Signals, Consents & Profile Data]
    
    LoadData --> EvalProfile[Evaluate Profile Completeness Factors]
    LoadData --> EvalIntent[Evaluate High-Intent Actions: Quote, Calculator]
    LoadData --> EvalEngage[Evaluate Engagement: Dwell Time, Returning Visits]
    LoadData --> EvalConsent[Evaluate Consent Status & Revocations]

    EvalProfile --> Aggregate[Aggregate Points & Generate Factor Explanations]
    EvalIntent --> Aggregate
    EvalEngage --> Aggregate
    EvalConsent --> Aggregate

    Aggregate --> Clamp[Clamp Score: Math.max(0, Math.min(100, TotalPoints))]
    Clamp --> SegmentRule{Determine Segment}
    SegmentRule -->|Score >= 70 & Consented| SegHigh[High Intent]
    SegmentRule -->|Score 40-69| SegWarm[Warm Consideration]
    SegmentRule -->|Score < 40| SegTop[Top of Funnel]
    SegmentRule -->|Inactive > 14 days| SegDormant[Dormant / Drop-off]

    Clamp --> Persist[Save LeadScore Record with score_factors_json]
    SegHigh --> UpdateProspect[Update Prospect: segment & latest_score]
    SegWarm --> UpdateProspect
    SegTop --> UpdateProspect
    SegDormant --> UpdateProspect
```

#### Explainable Factors JSON Structure:
```json
{
  "total_score": 75.0,
  "factors": [
    {
      "rule_code": "RULE_INTENT_QUOTE_STARTED",
      "rule_name": "Initiated Indicative Quote",
      "category": "intent",
      "points_awarded": 25,
      "rationale": "Visitor initiated quote calculator on Term Life Platinum page"
    },
    {
      "rule_code": "RULE_PROFILE_PHONE",
      "rule_name": "Provided Verified Mobile Number",
      "category": "profile",
      "points_awarded": 15,
      "rationale": "Indian phone number format validated"
    },
    {
      "rule_code": "RULE_CONSENT_MARKETING",
      "rule_name": "Explicit Communication Consent",
      "category": "consent",
      "points_awarded": 10,
      "rationale": "Digital consent recorded for SMS and WhatsApp advisory"
    },
    {
      "rule_code": "RULE_ENGAGEMENT_DWELL_TIME",
      "rule_name": "High Page Dwell Engagement",
      "category": "engagement",
      "points_awarded": 10,
      "rationale": "Active dwell time of 210s across insurance discovery tools"
    },
    {
      "rule_code": "RULE_ENGAGEMENT_MULTI_PAGE",
      "rule_name": "Multi-Product Exploration",
      "category": "engagement",
      "points_awarded": 15,
      "rationale": "Viewed 4 distinct policy comparisons"
    }
  ],
  "calculated_at": "2026-11-06T05:30:00Z"
}
```

---

### 6.3 Workload-Aware Advisor Assignment Engine (`services/lead_assignment_service.py`)

The assignment engine allocates qualified leads to human insurance advisors while protecting customer experience from overloaded advisors.

#### Assignment Constraints:
1. **Advisor Availability:** `advisors.is_available == True`.
2. **Capacity Limit:** Active cases count (`COUNT(customers) + COUNT(assigned_prospects)`) must be strictly less than `advisors.max_active_cases`.
3. **Specialization Match:** Priority given to advisors whose `specializations` string contains the lead's `target_insurance_type` (e.g. `term_life`, `health`).
4. **Least Loaded Balancing:** Among eligible matching advisors, the one with the lowest ratio of `current_active_cases / max_active_cases` receives the assignment.
5. **Supervisor / Manual Override:** Admins can manually assign or reassign any lead to any available advisor. Every manual reassignment generates an explicit `AuditLog` entry.

---

### 6.4 Unified Activity Timeline Aggregator (`services/timeline_service.py`)

A chronological aggregator that synthesizes disparate relational records into a cohesive stream for the lead inspector UI.

#### Event Stream Aggregation:
- **`PROSPECT_CREATED`:** Timestamp, source, initial landing page.
- **`CONSENT_GRANTED` / `CONSENT_REVOKED`:** Consent type, version, IP address.
- **`BEHAVIORAL_SIGNAL`:** Page views, calculators used, plan comparisons.
- **`SCORE_RECALCULATED`:** Old score, new score, key delta factor.
- **`ADVISOR_ASSIGNED`:** Advisor name, license, assignment mechanism (auto vs manual).
- **`AI_INTERACTION_SUMMARY`:** Stated intent and coverage interest extracted from chat messages by the `ProspectIntelligenceAgent`.
- **`ADVISOR_NOTE_ADDED`:** Human advisor notes recorded during phone or email outreach.

---

### 6.5 FastAPI Endpoints Specification

| Method | Endpoint | Authorized Roles | Purpose |
| :--- | :--- | :--- | :--- |
| `POST` | `/api/v1/prospects` | Public / Customer | Create or ingest prospect record with UTM attribution. |
| `GET` | `/api/v1/prospects` | Admin, Owner | Paginated search and filtering of all prospects. |
| `GET` | `/api/v1/prospects/{id}` | Admin, Owner, Advisor (assigned) | Detailed prospect view with score factors, consents, and stats. |
| `PATCH` | `/api/v1/prospects/{id}` | Admin, Owner, Advisor (assigned) | Update prospect details or qualification status. |
| `POST` | `/api/v1/prospects/{id}/assign` | Admin, Owner | Manually assign or reassign lead to a specific advisor. |
| `POST` | `/api/v1/prospects/{id}/recalculate-score` | Admin, Owner | Trigger on-demand deterministic score re-evaluation. |
| `GET` | `/api/v1/prospects/{id}/timeline` | Admin, Owner, Advisor (assigned) | Consolidated chronological activity timeline. |
| `POST` | `/api/v1/signals` | Public / Internal | Ingest client-side behavioral signal (page view, calculator). |
| `POST` | `/api/v1/signals/batch` | Public / Internal | Batch ingestion of queued client-side engagement events. |
| `POST` | `/api/v1/consent` | Public / Customer | Record explicit consent grant with IP and version. |
| `POST` | `/api/v1/consent/revoke` | Customer, Admin | Record explicit consent revocation. |
| `GET` | `/api/v1/advisor/leads` | Advisor | List leads assigned to currently authenticated advisor. |
| `POST` | `/api/v1/advisor/leads/{id}/notes` | Advisor | Add human outreach note to assigned lead. |
| `POST` | `/api/v1/advisor/leads/{id}/status` | Advisor | Transition lead status (`contacted`, `qualified`, `disqualified`). |

---

## 7. Frontend User Experience Specifications (Strict Enterprise White Theme)

In compliance with `AGENTS.md` Sections 7, 8, and 19, the UI operates strictly in a light/white palette with zero dark cards, dark backgrounds, or mock metrics.

### 7.1 Admin Lead Management Interface (`microproject/frontend/src/app/admin/leads/page.tsx`)

```text
┌────────────────────────────────────────────────────────────────────────────────────────┐
│ Prospect & Lead Pipeline                                        [ Filter ] [ Export ]  │
│ Monitor acquisition channels, behavioral engagement scores, and qualification states.   │
├─────────────┬─────────────┬──────────────┬──────────────┬──────────────┬───────────────┤
│ [All (24)]  │ [High Intent│ [Warm Cons.] │ [Top Funnel] │ [Price Sens] │ [Dormant]     │
├─────────────┴─────────────┴──────────────┴──────────────┴──────────────┴───────────────┤
│ [Search by name, email, phone...]   Source: [All Sources ▼]   Status: [All Statuses ▼] │
├────────────────────────────────────────────────────────────────────────────────────────┤
│ LEAD NAME & CONTACT │ SOURCE      │ SEGMENT      │ SCORE    │ ASSIGNED ADVISOR│ STATUS │
├─────────────────────┼─────────────┼──────────────┼──────────┼─────────────────┼────────┤
│ Rajesh Kumar        │ Google Ads  │ High Intent  │  78/100  │ Amit Verma      │ Qual.  │
│ +91 98765 43210     │ (Term Life) │ [● Consented]│ [View]   │ (4/10 cases)    │ [Edit] │
├─────────────────────┼─────────────┼──────────────┼──────────┼─────────────────┼────────┤
│ Priya Sharma        │ Web Direct  │ Warm Cons.   │  52/100  │ Unassigned      │ Engaged│
│ priya.s@example.com │ Organic     │ [● Consented]│ [View]   │ [Assign Advisor]│ [Edit] │
├─────────────────────┼─────────────┼──────────────┼──────────┼─────────────────┼────────┤
│ Anonymous Visitor   │ Aggregator  │ Top Funnel   │  25/100  │ —               │ New    │
│ Session: #ab49-812  │ Partner     │ [No Consent] │ [View]   │ (Unqualified)   │ [Edit] │
└────────────────────────────────────────────────────────────────────────────────────────┘
```

#### Key UI Components for Admin Lead Pipeline:
1. **Interactive TanStack Table:**
   - Multi-column sort (Score, Last Activity, Created Date).
   - Custom cell renderers: `StatusBadge` for qualification state, `SegmentPill` for customer segment, `ScoreIndicator` showing score with color-coded ring (Green >= 70, Amber 40–69, Slate < 40).
   - Consent indicator: Green lock icon for consented contactability; Amber warning icon when contact is legally restricted.
2. **Lead Inspector Sheet (`<Sheet>` component):**
   - Opens smoothly from the right side upon clicking any table row.
   - **Header:** Full name, contact badges, consent status badge, overall score pill.
   - **Tabs:**
     - `Activity Timeline`: Vertical timeline rendering aggregated user actions, page views, calculators, and advisor touches.
     - `Score Breakdown`: Detailed progress bars showing points contributed by Profile, Intent, Engagement, and Consent, with human-readable rationale for every item.
     - `Behavioral Signals`: Raw chronological signal log with JSON payload inspector.
     - `Advisor Assignment`: Current assignment card with re-assignment selector showing advisor active capacity bars.
3. **Manual Advisor Assignment Dialog (`<Dialog>` component):**
   - Displays list of active advisors with their current caseload (e.g. `8/25 active cases`) and specializations.
   - Confirmation step with mandatory note recording why reassignment occurred.

---

### 7.2 Advisor Assigned-Leads Workspace (`microproject/frontend/src/app/advisor/leads/page.tsx`)

The advisor's personalized dashboard view focused entirely on authorized leads.

```text
┌────────────────────────────────────────────────────────────────────────────────────────┐
│ My Assigned Leads                                             [ Availability: Active ] │
│ Prioritized prospective customers assigned to your advisory queue for direct outreach. │
├──────────────────────┬──────────────────────┬─────────────────────┬────────────────────┤
│ Total Assigned: 14   │ Ready to Call: 9     │ Follow-up Today: 3  │ Needs Review: 2    │
├──────────────────────┴──────────────────────┴─────────────────────┴────────────────────┤
│ [Search my leads...]                Priority: [High Intent First ▼]  Type: [All Types ▼│
├────────────────────────────────────────────────────────────────────────────────────────┤
│ CUSTOMER             │ INTENDED COVERAGE    │ SCORE   │ CONTACTABILITY  │ QUICK ACTION │
├──────────────────────┼──────────────────────┼─────────┼─────────────────┼──────────────┤
│ Rajesh Kumar         │ Term Life Platinum   │ 78/100  │ [● Consented]   │ [Call] [Log] │
│ +91 98765 43210      │ ₹1.00 Cr (30 Yrs)    │ High    │ WhatsApp / Call │ [Chat Note]  │
├──────────────────────┼──────────────────────┼─────────┼─────────────────┼──────────────┤
│ Sneha Patil          │ Comprehensive Health │ 68/100  │ [● Consented]   │ [Email] [Log]│
│ sneha.p@example.com  │ Family Floater ₹25L  │ Warm    │ Email Only      │ [Chat Note]  │
├──────────────────────┼──────────────────────┼─────────┼─────────────────┼──────────────┤
│ Vikram Malhotra      │ Motor Comprehensive  │ 45/100  │ [⚠ No Contact]  │ [View Only]  │
│ (Web discovery)      │ Sedan Premium        │ Top     │ In-App Chat Only│ [Request C.] │
└────────────────────────────────────────────────────────────────────────────────────────┘
```

#### Key UI Features for Advisor Queue:
1. **Contactability Enforcement in UI:** If `can_contact == False`, phone and email quick-action buttons are physically disabled with a tooltip explaining: *"Outreach blocked: Customer has not provided marketing contact consent under DPDP guidelines."*
2. **Log Outreach Dialog:** Quickly logs call outcomes (`connected_interested`, `busy_callback_requested`, `unreachable`, `not_interested`) and creates an automated `FollowUp` task in SQLite.
3. **Direct Handoff to Conversational Advisor:** One-click navigation to open the customer's active chat session or initiate a personalized onboarding proposal.

---

## 8. Step-by-Step Implementation Roadmap

### Step 1: Database Migration & Model Extensions
- Update `microproject/backend/app/models/prospect.py`:
  - Add `LeadScoringRule` model.
  - Add `assigned_advisor_id`, `assigned_at`, `segment`, `last_activity_at`, `estimated_budget_min`, `estimated_budget_max`, `target_insurance_type` to `Prospect`.
- Create and execute Alembic migration script `xxxx_phase4_lead_management.py`.
- Seed initial scoring rules and lead sources into SQLite.

### Step 2: Repositories & Data Access Layer
- Create `microproject/backend/app/repositories/prospect_repository.py`:
  - Methods: `create`, `get_by_id`, `get_by_email_or_phone`, `search_and_filter`, `update`, `assign_advisor`.
- Create `microproject/backend/app/repositories/signal_repository.py`:
  - Methods: `record_signal`, `record_batch`, `get_signals_for_prospect`, `get_signals_by_session`.
- Create `microproject/backend/app/repositories/scoring_rule_repository.py`:
  - Methods: `get_active_rules`, `get_rule_by_code`, `update_rule`.
- Create `microproject/backend/app/repositories/consent_repository.py`:
  - Methods: `record_consent`, `revoke_consent`, `get_active_consents`, `has_consent`.

### Step 3: Deterministic Lead Scoring & Segmentation Engine
- Create `microproject/backend/app/services/lead_scoring_service.py`:
  - Calculate exact score based on active database rules.
  - Build `score_factors_json` containing itemized points and rationale.
  - Assign cohort segment (`high_intent`, `warm_consideration`, `top_of_funnel`, `dormant`).
  - Store score in `lead_scores` table and update `prospects.segment`.

### Step 4: Workload-Aware Advisor Assignment Service
- Create `microproject/backend/app/services/lead_assignment_service.py`:
  - Match candidate advisors by availability and specialization.
  - Enforce `max_active_cases` capacity cap.
  - Select least-loaded advisor.
  - Implement manual reassignment with mandatory `AuditLog` recording.

### Step 5: Activity Timeline Aggregator & Lead Service
- Create `microproject/backend/app/services/timeline_service.py`:
  - Aggregate chronological events from prospects, signals, scores, consents, and advisor notes.
- Create `microproject/backend/app/services/lead_service.py`:
  - Core facade coordinating ingestion, score recalculation, signal dispatch, and advisor assignment.

### Step 6: FastAPI Routers & Scoped Authorization
- Create `microproject/backend/app/api/v1/prospects.py`:
  - Implement endpoints for prospect creation, listing with pagination/filters, detail view, advisor assignment, and timeline.
- Create `microproject/backend/app/api/v1/signals.py`:
  - Endpoints for single and batch signal ingestion.
- Create `microproject/backend/app/api/v1/consent.py`:
  - Endpoints for consent recording, status check, and revocation.
- Create `microproject/backend/app/api/v1/advisor_leads.py`:
  - Endpoints for advisor-scoped lead queue, status transitions, and notes.
- Register all routers in `microproject/backend/app/api/v1/api.py`.

### Step 7: LangGraph Prospect Intelligence Agent (Phase 3 Integration)
- Create `microproject/backend/app/ai/agents/definitions/prospect_intel_agent.py`:
  - LangGraph node parsing conversation messages into structured insurance preferences.
  - Enforce strict Pydantic output schema (`ProspectInsightsOutput`).
  - Guardrail: strictly forbid inventing customer information not present in the conversation text.

### Step 8: Frontend Lead API Client & Custom Hooks
- Create `microproject/frontend/src/services/lead-service.ts`:
  - Typed client for prospect retrieval, filtering, advisor assignment, signals, and consents.
- Create `microproject/frontend/src/hooks/use-prospect-tracker.ts`:
  - Client-side hook for automatically emitting behavioral beacons (`page_view`, dwell time, calculator events).

### Step 9: Admin Lead Management Interface Implementation
- Update `microproject/frontend/src/app/admin/leads/page.tsx`:
  - Connect TanStack Table to live FastAPI endpoints.
  - Implement multi-select filter controls (Status, Segment, Source, Advisor).
  - Implement Lead Inspector Sheet with Activity Timeline, Score Factor Explainer, and Advisor Reassignment Dialog.

### Step 10: Advisor Assigned-Leads Workspace Implementation
- Create `microproject/frontend/src/app/advisor/leads/page.tsx`:
  - Connect table to advisor-scoped endpoint (`/api/v1/advisor/leads`).
  - Implement contactability lock enforcement based on DPDP consent status.
  - Implement outreach logging dialog and follow-up scheduling.
- Update advisor sidebar navigation in `microproject/frontend/src/components/navigation/role-nav-config.ts`.

### Step 11: Comprehensive Pytest Verification Suite
- Implement 100% test coverage in `microproject/backend/tests/leads/`:
  - Ingestion, attribution, and deduplication tests.
  - Consent enforcement and outbound blocking tests.
  - Deterministic scoring math and factor explanation tests.
  - Advisor capacity cap and assignment tests.
  - Role-based scoping tests (Advisor cannot see peers' leads).

---

## 9. Automated Test Strategy & Scenarios

| Test File | Test Scenario | Expected Outcome |
| :--- | :--- | :--- |
| `test_prospect_ingestion.py` | Create prospect with full UTM parameters and referrer. | Prospect created with linked `LeadSource`, UTMs stored in JSON/columns, status = `new`. |
| `test_prospect_ingestion.py` | Create prospect with duplicate email. | Associates signals with existing prospect record; prevents orphaned duplicate records. |
| `test_consent_enforcement.py` | Attempt advisor outreach or SMS dispatch without active consent. | Operation blocked with `ConsentRequiredException` (HTTP 403); audit log records block. |
| `test_consent_enforcement.py` | Customer grants marketing consent, then revokes it. | Initial contact permitted; subsequent attempt immediately blocked; score penalised by 50 pts. |
| `test_deterministic_scoring.py` | Ingest quote attempt + dwell time > 120s + valid phone. | Lead score calculated exactly to 65.0; `score_factors_json` contains 3 distinct items. |
| `test_deterministic_scoring.py` | Update a scoring rule's point value in SQLite. | Next recalculation reflects updated rule value deterministically without code changes. |
| `test_advisor_assignment.py` | Auto-assign lead when all advisors are at `max_active_cases`. | Assignment held in `unassigned` queue; notification sent to Admin; no advisor overloaded. |
| `test_advisor_assignment.py` | Multiple eligible advisors available. | Lead assigned to advisor with lowest load ratio matching `target_insurance_type`. |
| `test_advisor_rbac_scoping.py` | Advisor attempts to view another advisor's assigned lead. | Endpoint returns HTTP 403 Forbidden; customer data isolation strictly preserved. |
| `test_prospect_timeline.py` | Ingest multiple signals, consent, score recalculation, and note. | Timeline endpoint returns ordered chronological list of all aggregated events. |
| `test_prospect_intel_agent.py` | Pass chat transcript discussing term life and 2 children. | Agent extracts intent: `term_life`, dependents: `2`; zero hallucinated financial details. |

---

## 10. Acceptance & Completion Criteria

Phase 4 is complete only when all of the following requirements are fulfilled and verified:

1. **Lead Ingestion & Attribution:**
   - Inbound prospects capture UTM campaign data and source attribution accurately.
   - Client-side signals (`page_view`, dwell time, calculator actions) ingest seamlessly.
2. **Consent & Privacy Compliance:**
   - Consent records are immutable, versioned, timestamped, and tied to IP addresses.
   - Outbound contact is physically impossible without verified marketing consent.
3. **Deterministic Scoring:**
   - Scoring criteria reside in SQLite (`lead_scoring_rules`).
   - Lead scores are calculated via deterministic rules and save an itemized factor explanation.
   - No hardcoded scoring logic in application code; no fabricated scores.
4. **Advisor Assignment & Queuing:**
   - Leads are assigned fairly respecting advisor availability, specialization, and capacity caps.
   - Supervisors can manually reassign leads with auditable reason logs.
5. **Role-Based Isolation:**
   - Advisors can only see leads assigned directly to them.
   - Admins and Owners can view and manage all system leads.
   - Customers have zero access to lead management APIs.
6. **Enterprise UI Quality:**
   - Admin pipeline and Advisor queue fully implemented in Next.js 16 App Router.
   - 100% white-themed UI utilizing direct shadcn/ui components (`Table`, `Sheet`, `Dialog`, `Badge`, `Tabs`).
   - Zero mock data or empty placeholder buttons in production runtime paths.
7. **Automated Testing:**
   - Pytest suite in `microproject/backend/tests/leads/` passes with 100% success rate.
