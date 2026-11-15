## AGENTS.md

# AI Coding Agent Instructions — PS-21

## 1. Project Identity

You are developing PS-21, a conversational insurance acquisition and onboarding platform.

The application includes:
- Customer Dashboard.
- Admin / Owner Dashboard.
- Advisor / Underwriter Dashboard.
- AI-powered conversational insurance workflows.
- Multi-agent orchestration.
- Insurance recommendation and quotation.
- Application onboarding.
- Document management.
- Human underwriting escalation.
- Analytics and compliance.

Always understand the complete business context before implementing a feature.

## 2. Mandatory Technology Stack

Frontend:
- Next.js 16.
- TypeScript.
- App Router.
- Tailwind CSS.
- shadcn/ui.
- Lucide React.

Backend:
- Python.
- FastAPI.
- SQLAlchemy.
- SQLite.
- Alembic.
- Pydantic.

AI:
- Mistral LLM only.
- LangGraph for agent orchestration.

Do not introduce alternative technologies that conflict with this stack without explicit approval.

## 3. Strict LLM Rules

Mistral is the only permitted LLM provider.

Never:
- Use OpenAI.
- Use Anthropic.
- Use Gemini.
- Use another provider as backup.
- Switch models automatically.
- Generate fake LLM responses.
- Return hardcoded AI answers when Mistral fails.

Load the API key and model configuration from environment variables.

If configuration is missing, fail clearly.

If the API fails, report the error.

Never claim an AI operation succeeded unless it actually succeeded.

All LLM outputs used by the backend must be validated against appropriate schemas.

## 4. LangGraph Rules

Use LangGraph for stateful agent workflows.

Agents must:
- Have clearly defined responsibilities.
- Use structured input and output.
- Operate within explicit permissions.
- Use registered tools.
- Share validated graph state.
- Support appropriate checkpoints.
- Support human-in-the-loop operations.
- Produce observable execution records.

Do not use LangGraph merely as a wrapper around one LLM call.

Do not give agents unrestricted database or system access.

Do not allow agents to bypass backend authorization.

Agentic Architecture Requirement: Build a genuinely agentic, multi-agent system using Mistral and LangGraph. Agents must be capable of contextual reasoning, goal-oriented task execution, dynamic workflow routing, tool selection from authorized tools, inter-agent delegation, shared-state management, and human escalation. Do not implement the platform as a fixed chain of prompts or a collection of ordinary CRUD functions labelled as agents. Use deterministic services for exact calculations, validation, permissions, and regulated business operations. Agents must remain autonomous within explicitly defined permissions and business boundaries.

## 5. No Hardcoding

Never hardcode dynamic business information.

This includes:
- Premiums.
- Product prices.
- Coverage rules.
- Eligibility rules.
- Underwriting thresholds.
- Customer records.
- Lead scores.
- Dashboard metrics.
- Agent execution results.
- Application statuses.
- External API credentials.

Store configurable business data in the database or appropriate configuration sources.

Hardcoded UI labels, fixed application routes, design tokens, and static technical constants are acceptable.

Do not use placeholder records in production runtime paths.

Do not use fabricated data to make dashboards appear populated.

If no data exists, display a proper empty state.

## 6. No Fallback Policy

There must be no silent fallback behavior.

Do not:
- Switch to another LLM.
- Return fake API results.
- Replace failed database queries with static data.
- Return fake quotes.
- Pretend document verification succeeded.
- Pretend notifications were sent.
- Pretend underwriting was completed.
- Silently use in-memory storage instead of SQLite.
- Hide service failures behind generic success responses.

Use explicit, bounded retry handling only for classified transient failures.

If a required dependency is unavailable, report the failure and preserve the workflow state safely.

Test doubles are permitted only in isolated automated tests and must never become runtime fallbacks.

## 7. Frontend Design Rules

The entire application must maintain one professional visual identity.

### Required appearance
- White-only theme.
- White page backgrounds.
- Light-grey secondary surfaces.
- Professional blue accents.
- Dark navy or charcoal typography.
- Subtle borders.
- Consistent spacing.
- Restrained shadows.
- Clear information hierarchy.

### Forbidden
- Dark mode.
- Dark cards.
- Black dashboard sections.
- Random color combinations.
- Excessive gradients.
- Excessive glass effects.
- Inconsistent typography.
- Unnecessary animations.
- Different design styles across dashboards.

### Component rules

Use actual shadcn/ui components directly.

Import components from the project's configured shadcn UI directory.

Examples:

```tsx
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Badge } from "@/components/ui/badge"
import { Dialog, DialogContent } from "@/components/ui/dialog"
```

Do not recreate existing shadcn components.

Do not build unnecessary wrapper components around every shadcn component.

Create reusable business-specific components only where they provide genuine value.

Use Lucide React icons.

Maintain accessibility, keyboard navigation, responsive layouts, and consistent interaction patterns.

## 8. Next.js Rules

Use Next.js 16 App Router.

Prefer Server Components.

Use Client Components only when browser interaction or client-side state requires them.

Keep components small and focused.

Do not place all business logic inside React components.

Use a dedicated service layer for API communication.

Validate forms with Zod.

Handle:
- Loading states.
- Empty states.
- Error states.
- Unauthorized states.
- Success states.

Do not show a success notification before the backend confirms success.

Never expose server secrets to the browser.

## 9. Backend Rules

Use a clean layered architecture:

```text
API Router
    ↓
Authentication / Authorization
    ↓
Pydantic Validation
    ↓
Service Layer
    ↓
Repository Layer
    ↓
SQLite Database
```

Use:
- Pydantic schemas.
- SQLAlchemy models.
- Repository classes.
- Business services.
- Explicit transaction handling.
- Centralized exception handling.
- Structured logging.

Do not put business logic inside API route handlers.

Do not allow frontend clients to directly access the database.

## 10. Database Rules

SQLite is the initial required database.

Use SQLAlchemy and Alembic.

Requirements:
- Foreign keys.
- Appropriate indexes.
- Unique constraints.
- Non-null constraints where necessary.
- Explicit relationships.
- Created and updated timestamps.
- Migration scripts.
- Transaction-safe operations.

Do not create duplicate entities for the same business concept.

Do not store structured relational data in one large JSON field without justification.

Sensitive information must be handled with appropriate access controls and encryption where required.

## 11. Insurance Business Rules

The platform supports insurance acquisition and onboarding.

Never treat an AI-generated recommendation as a formal underwriting decision.

Never let an LLM independently calculate premiums.

Never invent:
- Product benefits.
- Exclusions.
- Policy terms.
- Pricing.
- Eligibility.
- Insurer approval.
- Policy issuance.

Use actual configured product information.

Use approved pricing logic or authorized insurer APIs.

Human underwriting and formal policy issuance remain within the authorized insurer process.

Clearly distinguish:
- Recommendation.
- Indicative quote.
- Proposal submission.
- Underwriting review.
- Insurer decision.
- Policy issuance.

## 12. Security and Permissions

Implement role-based and permission-based access control.

Roles:
- Customer.
- Advisor.
- Underwriter.
- Admin.
- Owner.

Every protected operation must verify authorization on the backend.

Never rely only on hidden frontend navigation to protect data.

Customers must only access their own records.

Advisors and underwriters must only access authorized cases.

Sensitive medical and financial information must have restricted access.

Record sensitive document access and important business operations in audit logs.

## 13. Agent Design Standards

Every agent must have:
- Unique identifier.
- Clear name.
- Description.
- Purpose.
- Input schema.
- Output schema.
- Tools.
- Permissions.
- Graph entry and exit conditions.
- Error handling.
- Logging.
- Execution history.

Use ordinary backend services for deterministic tasks.

Use LLMs only when language understanding, reasoning, extraction, summarization, or conversational generation adds value.

Do not create agents unnecessarily.

## 14. API Standards

Use consistent REST API naming.

Version APIs appropriately.

Validate all request payloads.

Use consistent response structures.

Return meaningful HTTP status codes.

Never expose internal stack traces or secrets.

Document important endpoints.

## 15. Testing Standards

Write tests for:
- Authentication.
- Authorization.
- Customer data isolation.
- Database operations.
- Business rules.
- Quote calculations.
- Agent execution.
- LangGraph routing.
- Human review.
- Document permissions.
- API errors.
- Critical user journeys.

Do not claim tests passed without running them.

Clearly distinguish mocked integration tests from real external-service tests.

## 16. Code Quality

Maintain:
- Small modules.
- Clear naming.
- Type safety.
- Reusable functions.
- Explicit dependencies.
- Consistent formatting.
- Useful documentation.

Avoid:
- Giant files.
- Duplicated logic.
- Unnecessary abstractions.
- Unused dependencies.
- Dead code.
- Silent exceptions.
- Empty placeholder handlers.
- Unimplemented buttons.

Do not suppress errors merely to make the application appear functional.

## 17. Documentation

Keep these documents updated:

- README.md.
- Architecture documentation.
- Database schema documentation.
- API documentation.
- Agent workflow documentation.
- Environment setup.
- Deployment instructions.
- Known limitations.

Every significant architecture change must be documented.

## 18. Development Workflow

Before beginning any task:

1. Read this AGENTS.md.
2. Inspect the relevant existing code.
3. Understand dependencies.
4. Identify affected modules.
5. Plan the implementation.
6. Implement the smallest complete solution.
7. Run relevant tests.
8. Inspect the final changes.
9. Update documentation.
10. Report completion honestly.

Never mark incomplete functionality as complete.

Never skip error handling.

Never silently violate the technology requirements.

## 19. Definition of Done

A feature is complete only when:

- The backend implementation exists.
- The frontend is connected to the real backend.
- Data persists correctly.
- Authorization is enforced.
- Validation works.
- Loading and error states work.
- Tests have been executed.
- Documentation is updated.
- No fake runtime behavior exists.
- The feature follows the shared UI design system.

**These instructions apply to every development task in this repository.**