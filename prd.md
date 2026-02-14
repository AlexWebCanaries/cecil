# PRD: Lightweight LLM Cost & Cache Analytics SDK

## 1. Overview
This product has two deliverables with different distribution models:
- Open-source SDK for local LLM observability and optional telemetry export.
- Private SaaS for aggregated analytics, dashboards, and operational controls.

The SDK must:
- Not be in the production request path to LLM providers.
- Require minimal integration effort (1-2 lines of code).
- Be enterprise-safe by default (privacy-first telemetry).

---

## 2. Product Model

### 2.1 Open-Source vs Private Boundaries
Open-source:
- Python SDK package and telemetry contracts.
- Local analysis logic (cache/cost estimation).
- Public docs for SDK onboarding and privacy model.

Private (not open-source):
- SaaS frontend and backend services.
- Cloud infrastructure, auth configuration, and operational runbooks.
- Internal admin workflows and multi-tenant operations.

### 2.2 Repository Strategy
- Public SDK repository: standalone, SDK-only codebase.
- Private SaaS repository: frontend + backend + cloud infrastructure.
- Shared API/schema contract versioned explicitly between repos.

---

## 3. Problem Statement
Organizations using OpenAI, Anthropic, and similar providers often:
- Lack visibility into prompt structure inefficiencies.
- Cannot estimate missed prompt caching opportunities.
- Overpay due to dynamic prefixes or repeated static prompt blocks.

---

## 4. Goals
Primary goals:
- Frictionless SDK onboarding.
- Accurate cache and cost analytics.
- Clear separation of open-source SDK from private SaaS implementation.

Secondary goals:
- Aggregated benchmarking and operational insights in SaaS.
- Actionable recommendations and alerts.

Non-goals (MVP):
- LLM gateway proxying.
- Automatic prompt rewriting.
- Open-sourcing SaaS/backend infrastructure.

---

## 5. Product Requirements

### 5.1 SDK Behavior
Default mode:
- Local analysis only.
- No telemetry leaves environment.

Telemetry mode (opt-in):
- Enabled with `LLM_OBSERVER_ENABLED=true` and `LLM_OBSERVER_API_KEY`.
- Sends hashed/metadata telemetry only by default.

### 5.2 Local Analysis Features
SDK provides:
- Estimated cost per request.
- Prefix similarity and cache opportunity estimation.
- Cache-breaker detection (timestamp/UUID/randomness patterns).

### 5.3 SaaS Features (Private)
When telemetry is enabled:
- Aggregated dashboards.
- Savings and cache trend analytics.
- Prompt inefficiency alerts.
- Admin controls for org/project/key lifecycle.

---

## 6. Platform Architecture Requirements

### 6.1 Frontend
- Next.js frontend hosted on Vercel.
- User-facing dashboard and admin UI only.
- Frontend calls private AWS backend APIs.

### 6.2 Backend
- Backend runs on AWS (API + compute + storage + auth).
- Recommended MVP stack:
  - API Gateway + Lambda (or ECS/Fargate if long-running needs emerge)
  - RDS Postgres (or Aurora Postgres)
  - Cognito for user auth and JWT issuance
  - Secrets Manager + CloudWatch for operations
- SDK ingest contract remains `Authorization: Bearer lok_<prefix>.<secret>`.

---

## 7. User Experience

### 7.1 SDK Onboarding (Open Source)
1. `pip install llm-observer`
2. `import llm_observer`
3. `llm_observer.patch()`

### 7.2 Telemetry Onboarding
Set:
- `LLM_OBSERVER_ENABLED=true`
- `LLM_OBSERVER_API_KEY=xxx`
- `LLM_OBSERVER_ENDPOINT=https://<aws-api-domain>`

### 7.3 SaaS Onboarding
1. User signs in to Next.js app on Vercel.
2. Frontend obtains Cognito-backed session/JWT.
3. Backend enforces role-based access for admin actions.

---

## 8. Security & Privacy Requirements
SDK:
- Never send raw prompts by default.
- Keep telemetry fail-open.
- Allow full telemetry disable.

SaaS:
- JWT-based auth for dashboard/admin users (Cognito).
- API keys hashed at rest, revocable, org-scoped.
- Audit logging for admin mutations.
- No backend secrets in client bundles.

---

## 9. Risks
Technical risks:
- Contract drift between public SDK repo and private SaaS repo.
- Tokenization estimation variance.
- AWS integration complexity for small team.

Business risks:
- Vendor/cost dependency on AWS and Vercel.
- Security review delays for multi-cloud setup.

Mitigations:
- Versioned shared contract and compatibility tests.
- Explicit repo ownership boundaries.
- Hardened CI/CD and environment isolation.

---

## 10. Success Metrics
- SDK onboarding time < 5 minutes.
- Telemetry opt-in rate > 20%.
- Cache savings detected per customer > 20%.
- Zero incidents of raw prompt leakage in default mode.
- No unauthorized cross-tenant data access.
