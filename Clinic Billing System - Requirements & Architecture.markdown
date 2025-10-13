# Clinic Billing System — Requirements & Implementation Guide (Local Deployment)

**Purpose:** A clear, execution-ready requirements document to build a secure, scalable Billing System for a clinic, designed to run on a local system. Backend is a Python microservice (business logic, SQLAlchemy, JWT auth). Frontend is a Vite + React application for staff and patients, with a modern, accessible design. Payments are handled via Stripe Payment Links / Checkout Sessions to ensure PCI compliance.

## 1. High-level Overview

**Goal:** Enable clinic staff to create and manage invoices and let patients securely pay online using Stripe-managed payment flows. The clinic system must never accept or store raw card data; all card processing occurs on Stripe. Backend and frontend are strictly separated into two repositories or two top-level folders in a mono-repo, deployed on a local server.

**Principles:** 
- **Security-first:** JWT-based auth, TLS for external communication (e.g., Stripe), limited data retention, least privilege.
- **Compliance:** Avoid handling card data; use Stripe Checkout or Payment Links + webhooks; follow PCI DSS guidance for outsourced payment processors.
- **Scalability:** Stateless backend service, database with proper indexing, suitable for single-server deployment with potential for future scaling.
- **Observable:** Structured logs, request tracing, and payment/audit trails for local debugging and monitoring.
- **Design:** Modern, minimalist, accessible UI with a healthcare-focused aesthetic to ensure usability and trust.

## 2. Actors & Roles

- **Clinic Staff** (roles: Admin, Billing Clerk) — create invoices, issue refunds, view patient payment history, reconcile payments.
- **Patient** — view invoices, receive email/text with secure payment link, complete payment using Stripe-hosted page.
- **System (Stripe)** — processes card payments, returns success/failure via webhooks.
- **Operator / DevOps** — set up and maintain the local system, manage backups, and respond to incidents.

## 3. Scope & Out of Scope

**In Scope:**
- Staff registration & login (JWT auth).
- Patient invoice creation, retrieval, listing, filtering, PDF export.
- Payment processing via Stripe Payment Links or Checkout Sessions and webhook handling.
- Payment status synchronization, refunds, and audit logs.
- Frontend (React/Vite) for staff and patients with responsive, accessible UI.
- Secure storage of PII and PHI according to local laws (encryption at rest/in transit).

**Out of Scope for Initial Release:**
- Tokenized card storage on clinic systems (use Stripe only).
- Complex insurance claim processing (can be layered later).

## 4. Non-Functional Requirements

- **Security:** HTTPS/TLS for external APIs (e.g., Stripe); sensitive config stored in environment variables or local secret files. Use security headers for web interfaces. Rate-limit sensitive endpoints if exposed externally.
- **Authentication & Authorization:** JWT access tokens + optional refresh tokens, RBAC for staff roles. Short-lived access tokens (e.g., 15m) and refresh tokens stored securely.
- **Performance:** Backend stateless, optimized for single-server performance. DB connection pooling. 95th percentile API latency < 300ms under normal load.
- **Availability:** High reliability on local system with manual failover and recovery processes.
- **Compliance:** PCI scope minimized by using Stripe Checkout/Payment Links. Webhook signatures verified. Audit trails immutable.
- **Observability:** Structured logs (JSON) stored locally, request IDs, basic metrics for debugging.
- **Testing:** Unit tests for business logic, integration tests for DB and Stripe interactions (use Stripe test keys), E2E for critical user flows.
- **Frontend Design:** Clean, professional, WCAG-compliant UI with a healthcare-focused aesthetic, mobile-first responsiveness, and intuitive navigation.

## 5. System Architecture (Logical)

```
 +--------------+        HTTPS        +-----------------+        SQL        +------------+
 |  React/Vite  | <-----------------> | Python Backend  | <---------------> | PostgreSQL |
 |  Frontend    |                     | (FastAPI/Flask) |                   | (SQLAlchemy)|
 +--------------+                     +-----------------+                   +------------+
            |                                   |
            |                                   +---> Stripe (Checkout / Links)
            |                                           (Webhook -> Backend)
            +-- Email/SMS service (SendGrid/Twilio) ------>
```

- **Backend**: Python microservice built with FastAPI (recommended) or Flask. Uses SQLAlchemy ORM, Alembic for migrations, Uvicorn/Gunicorn for ASGI, running on a local server.
- **Database**: PostgreSQL installed locally. Use dedicated tables for staff, patients, invoices, invoice_items, payments, audit_logs.
- **Stripe**: Create Checkout Sessions or Payment Links per invoice. Use webhooks to record payment_intent.succeeded, checkout.session.completed, charge.refunded.
- **Email/SMS**: Service to send invoice notifications with secure links (link contains a short-lived token or link tied to invoice id — not the JWT).
- **Frontend**: Vite + React with a modern, accessible design for staff and patient interfaces.

## 6. Data Model (Core Tables)

- **staff** 
  - id (uuid, pk)
  - email (unique)
  - password_hash
  - name
  - role (enum: admin, billing_clerk)
  - created_at, updated_at
- **patients** 
  - id (uuid, pk)
  - name
  - email
  - phone
  - dob (nullable)
  - metadata/json (optional)
  - created_at, updated_at
- **invoices** 
  - id (uuid, pk)
  - invoice_number (string, unique)
  - patient_id (fk)
  - staff_id (fk)
  - currency (ISO code)
  - total_amount_cents (int)
  - status (enum: draft, issued, paid, partially_paid, cancelled)
  - issued_at, due_date
  - stripe_payment_link_id (nullable)
  - stripe_checkout_session_id (nullable)
  - created_at, updated_at
- **invoice_items** 
  - id (uuid)
  - invoice_id (fk)
  - description
  - quantity
  - unit_price_cents
  - tax_cents
- **payments** 
  - id (uuid, pk)
  - invoice_id (fk)
  - stripe_payment_id
  - amount_cents
  - currency
  - status (succeeded, failed, refunded)
  - received_at
  - raw_event json (for audit)
- **audit_logs** 
  - id (uuid)
  - actor_type (staff, system)
  - actor_id (nullable)
  - action (create_invoice, mark_paid, refund, etc.)
  - target_type, target_id
  - details json
  - created_at

## 7. API Surface (Representative Endpoints)

**Auth**
- POST /api/v1/auth/register — staff registration (admin only in production).
- POST /api/v1/auth/login — returns access_token, refresh_token.
- POST /api/v1/auth/refresh — exchange refresh token for new access token.

**Patients**
- POST /api/v1/patients — create patient (staff).
- GET /api/v1/patients/{id} — get patient.
- GET /api/v1/patients?query= — search.

**Invoices**
- POST /api/v1/invoices — create invoice with items.
- GET /api/v1/invoices/{id} — retrieve invoice (include items & payment summary).
- GET /api/v1/invoices?patient_id=&status=&from=&to= — list & filter.
- POST /api/v1/invoices/{id}/issue — issue invoice (creates Stripe payment link/checkout session).
- POST /api/v1/invoices/{id}/cancel — cancel invoice.

**Payments & Stripe**
- POST /api/v1/invoices/{id}/create-payment-link — create a Stripe Payment Link or Checkout Session; store link/session IDs.
- POST /api/v1/webhooks/stripe — Stripe webhook endpoint (verify signature).
- GET /api/v1/invoices/{id}/payments — list payments for invoice.
- POST /api/v1/payments/{payment_id}/refund — refund via Stripe API (admin/billing role).

**Admin / Audit**
- GET /api/v1/audit?target_type=&actor_id= — read-only audit logs.

**Security Notes on APIs:**
- All protected endpoints require Authorization: Bearer <JWT>.
- Public endpoints (e.g., patient invoice links) use short-lived signed tokens or Stripe-hosted checkout.

## 8. Authentication & Session Management

**JWT Tokens**
- Access Token: JWT signed with HS256 (local secret key). Lifetime: 10–30 minutes.
- Refresh Token: Stored securely in httpOnly cookies or local storage. Lifetime: 7–30 days.
- Token Revocation: Maintain a local token blacklist/refresh token store to revoke tokens for disabled staff.
- Claims: sub (staff id), role, iat, exp, jti.

**Public Invoice Payment Links**
- Use short-lived HMAC-signed tokens or Stripe-hosted checkout referencing invoice ID, validated via webhook.

## 9. Stripe Integration (Detailed)

**Strategy:** Use Stripe Checkout Sessions or Payment Links. Each invoice maps to a Checkout Session or Payment Link with invoice ID in metadata.

**Approach:**
1. Backend creates a Stripe Checkout Session with line_items matching invoice items.
2. Set metadata.invoice_id and metadata.clinic_id on the session.
3. Send the Checkout URL to the patient via email/SMS or display in the patient portal.
4. Implement POST /api/v1/webhooks/stripe to handle events, verifying signatures with Stripe’s webhook secret.
5. On checkout.session.completed or payment_intent.succeeded, mark invoice as paid (idempotent via stripe_payment_id). Store event payload in payments.raw_event.
6. For refunds, use Stripe Refund API, update payments.status, and log in audit_logs.

**Security & PCI Notes:**
- No card data collection/processing locally; rely on Stripe Checkout.
- Verify webhook signatures server-side.
- Secure webhook endpoint with a secret; use TLS for external communication.

**Idempotency & Reliability:**
- Use Stripe event IDs for idempotent webhook processing.
- Save events to DB before returning 200 to Stripe.

## 10. Frontend (Vite + React) Requirements

**App Structure:**
- **/staff/*** — Authenticated portal with sidebar navigation: Dashboard, Patient Management, Invoice Builder/List, Payments & Refunds, Audit & Ledger.
- **/patient/*** — Public-facing, no sidebar: View Invoice (via secure link), Pay Invoice (Stripe redirect), Payment Receipt.

**Design Guidelines:**
- **Theme:** Modern, minimalist, healthcare-focused with whitespace, rounded corners (8px radius), subtle shadows.
- **Colors:** 
  - Primary: Soft blue (#4A90E2) for buttons/links.
  - Secondary: Teal green (#00BFA5) for success states.
  - Neutral: White (#FFFFFF) background, light gray (#F4F6F8) panels, dark gray (#333333) text.
  - Alerts: Red (#FF6B6B) for errors, yellow (#FFD700) for warnings.
- **Typography:** Roboto/Inter sans-serif; H1: 24px bold, H2: 18px bold, Body: 14px, Labels: 12px semi-bold; 1.5 line height.
- **Icons:** Line icons (Font Awesome/Material Icons) in primary colors.
- **Animations:** Subtle 0.3s transitions for hovers, modals, loading.
- **Responsiveness:** Mobile-first, breakpoints at 480px, 768px, 1024px.
- **Accessibility:** WCAG-compliant (4.5:1 contrast, keyboard navigation, ARIA labels).

**Staff Pages & Components:**
- **Login/Register:** Centered form with white-to-light-blue gradient, large inputs, blue "Login" button, error messages in red.
- **Dashboard:** Sidebar (collapsible on mobile), KPI cards (Outstanding Invoices, Recent Payments) in 4-column grid, bar/line charts, recent activity table. Blue action buttons, green status badges.
- **Patient Management:** Search bar, table/card list, "Add Patient" modal with editable fields.
- **Invoice Builder/List:** Filterable list with status badges (green "Paid", red "Overdue"), stepper modal (Patient > Items > Review), PDF export.
- **Payments & Refunds:** Payment list with timeline, refund modal with reason dropdown.
- **Audit & Ledger:** Searchable table with expandable rows for JSON details.

**Patient Pages:**
- **Invoice View:** Centered invoice (number, date, items, total), "Pay Now" button (Stripe redirect), PDF export, print-friendly.
- **Payment Result/Receipt:** Green checkmark for success with confetti animation, receipt details, download button; red error page for failures.

**Security (Frontend):**
- Store JWTs in httpOnly cookies or memory, CSRF protection, strict CORS (localhost).
- Use Material-UI or similar for consistent components (cards, modals, tables).

**Development Notes:**
- Use React Router for navigation, Axios for API calls.
- Test responsiveness and accessibility (keyboard nav, screen readers).

## 11. Project Organization (Suggested Repo Layout)

**Backend (Python Microservice)**

```
backend/
├─ app/
│  ├─ api/  (routers)
│  ├─ core/ (config, security, jwt)
│  ├─ models/ (sqlalchemy models)
│  ├─ schemas/ (pydantic schemas)
│  ├─ services/ (business logic: invoice_service, payment_service)
│  ├─ db/ (session, migrations)
│  └─ main.py
├─ tests/
├─ alembic/
├─ Dockerfile
├─ requirements.txt
└─ .env.example
```

**Frontend (Vite + React)**

```
frontend/
├─ src/
│  ├─ pages/ (Staff, Patient)
│  ├─ components/
│  ├─ services/ (api wrappers)
│  ├─ styles/
│  └─ main.jsx
├─ public/
├─ package.json
├─ vite.config.js
└─ Dockerfile
```

## 12. Deployment & DevOps (Local System)

- **Environment:** Single local server (Windows/Linux) running Docker or direct Python/Node.js.
- **Database:** PostgreSQL installed locally with local backups.
- **Secrets:** Store Stripe API keys, DB credentials, and JWT secrets in .env files (chmod 600) or local secret manager.
- **Setup Process:**
  1. Install Docker or Python/Node.js locally.
  2. Set up PostgreSQL with a dedicated user and database.
  3. Run Alembic migrations for DB schema.
  4. Start backend (Uvicorn/Gunicorn) and frontend (Vite dev server or build).
- **Backups:** Manual or cron-based PostgreSQL backups (pg_dump) to local storage.
- **Network:** Localhost or LAN access; external Stripe calls require internet.

## 13. Testing Strategy

- **Unit Tests:** Business logic (invoice calculations), auth flows.
- **Integration Tests:** DB interactions (local test DB), Stripe interactions (test keys, mocked webhooks).
- **E2E Tests:** Simulate staff creating invoices and patients paying (Playwright/Cypress).
- **Security Tests:** Static code analysis, dependency scanning, verify JWT config.

## 14. Monitoring & Alerting

- **Metrics:** Local logging of request rates, errors, and latencies (viewable via logs or simple scripts).
- **Logging:** JSON logs stored in local files with request IDs.
- **Alerts:** Manual monitoring of logs for payment failures or webhook errors.

## 15. Operational & Business Rules

- **Invoice Numbering:** CLINIC-YYYYMM-0001 format.
- **Partial Payments:** Support partial payments if Stripe allows; track outstanding balance.
- **Refund Policy:** Refunds via Stripe API with admin approval.
- **Retention:** Retain records per local regulations; archive old invoices to local storage.

## 16. Security Checklist (Minimum)

- TLS for external Stripe/email APIs.
- JWT secret rotation (manual process).
- Webhook signature verification.
- No card data stored locally.
- RBAC for staff roles.
- Input validation & output encoding.
- Rate limiting for auth endpoints if externally accessible.
- Regular dependency vulnerability scanning (local tools like pip-audit).

## 17. Deliverables & Milestones

1. **MVP (2–4 sprints)**
   - Backend: auth, invoice CRUD, Stripe payment link creation, webhook processing, DB schema & migrations.
   - Frontend: staff login, patient & invoice creation, issue invoice, patient invoice view & Stripe redirect.
   - Tests: unit & integration for core flows.
2. **v1 (1–2 sprints)**
   - Refunds, PDF export, audit logs, payments reconciliation UI, role management.
   - Local deployment scripts, monitoring setup, documentation.
3. **Hardening**
   - Local security tests, compliance review, backup verification.

## 18. Example Implementation Notes & Tips

- Use **FastAPI** + **SQLAlchemy** + **Alembic** for rapid backend development.
- Use **python-jose** or **PyJWT** for JWT; HS256 with local secret for simplicity.
- Prefer **Stripe Checkout Sessions** for minimal PCI scope.
- Store audit logs as append-only in the local database.
- Ensure email notifications exclude sensitive data beyond invoice ID and payment link.
- Use Material-UI or similar for frontend components to align with design guidelines.

## 19. Appendix — Example Stripe Webhook Processing Pseudocode

```python
from stripe import Webhook

payload = request.body
sig_header = request.headers['Stripe-Signature']

try:
    event = Webhook.construct_event(payload, sig_header, STRIPE_WEBHOOK_SECRET)
except ValueError:
    return 400
except SignatureVerificationError:
    return 400

if event['type'] == 'checkout.session.completed':
    session = event['data']['object']
    invoice_id = session['metadata'].get('invoice_id')
    payment_intent_id = session['payment_intent']
    # Idempotency: if payment exists, ignore
    upsert_payment(invoice_id, payment_intent_id, session)
    mark_invoice_paid_if_full(invoice_id)

return 200
```

## 20. Next Steps & Recommendations

1. Set up a local PostgreSQL instance and test connectivity.
2. Implement a backend spike: auth, invoice creation, Stripe Checkout integration (test keys).
3. Run Alembic migrations for DB schema.
4. Build minimal React flows (staff login, create invoice, generate payment link) using design guidelines.
5. Test webhook handler with Stripe test card numbers.