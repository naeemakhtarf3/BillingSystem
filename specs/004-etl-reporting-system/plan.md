# Implementation Plan: ETL Reporting System

**Branch**: `004-etl-reporting-system` | **Date**: 2024-12-19 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/004-etl-reporting-system/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Implement ETL reporting system with automated data aggregation, role-based report access, and WCAG-compliant dashboard. System aggregates invoice/payment data into reporting schema, provides revenue/patient/outstanding payment reports via REST API, and delivers staff dashboard with Recharts visualizations.

## Technical Context

**Language/Version**: Python 3.11, React 18+  
**Primary Dependencies**: FastAPI, SQLAlchemy, Pandas, React, Recharts, Material-UI  
**Storage**: PostgreSQL with reporting schema, existing SQLite for source data  
**Testing**: pytest for backend, Jest for frontend (excluded per constitution)  
**Target Platform**: Web application (Linux server backend, modern browsers)  
**Project Type**: Web application (backend + frontend)  
**Performance Goals**: 3-second report generation, 50 concurrent users, 2-second query response  
**Constraints**: HIPAA compliance, WCAG 2.1 AA, 1-year data retention, PDF export only  
**Scale/Scope**: 10,000+ records ETL processing, 50 concurrent users, 3 report types

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- **Backend-First**: ✅ All business logic implemented in Python backend (ETL, report generation, RBAC)
- **Component-Based**: ✅ Frontend features as separate React components (Reports Dashboard, Revenue Charts, etc.)
- **Material-UI**: ✅ All frontend styling uses Material-UI components (specified in requirements)
- **Minimal Dependencies**: ✅ Justified dependencies (FastAPI, SQLAlchemy, Pandas, React, Recharts, Material-UI)
- **Clean Code**: ✅ Code will be readable and well-documented
- **No Tests**: ✅ Test cases explicitly excluded per constitution

## Project Structure

### Documentation (this feature)

```
specs/[###-feature]/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)

```
backend/
├── app/
│   ├── models/
│   │   ├── report_schema.py      # Reporting schema models
│   │   └── etl_status.py         # ETL process tracking
│   ├── services/
│   │   ├── etl_service.py        # ETL data processing
│   │   ├── report_service.py     # Report generation logic
│   │   └── audit_service.py      # Audit logging
│   ├── api/
│   │   └── api_v1/
│   │       └── endpoints/
│   │           └── reports.py     # Report API endpoints
│   └── core/
│       └── security.py           # RBAC implementation
├── etl.py                         # ETL script entry point
└── requirements.txt               # Backend dependencies

frontend/
├── src/
│   ├── components/
│   │   ├── reports/
│   │   │   ├── ReportsDashboard.jsx
│   │   │   ├── RevenueCharts.jsx
│   │   │   ├── PatientSearch.jsx
│   │   │   ├── OutstandingPayments.jsx
│   │   │   └── ReportFilters.jsx
│   │   └── common/
│   │       └── ExportControls.jsx
│   ├── pages/
│   │   └── staff/
│   │       └── Reports.jsx        # Main reports page
│   ├── services/
│   │   └── reportService.js       # API integration
│   └── contexts/
│       └── AuthContext.jsx       # Authentication context
└── package.json                   # Frontend dependencies
```

**Structure Decision**: Web application structure with backend-first API design and component-based frontend. Backend handles all business logic (ETL, report generation, RBAC) while frontend provides presentation layer with Material-UI components.

## Complexity Tracking

*Fill ONLY if Constitution Check has violations that must be justified*

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| [e.g., 4th project] | [current need] | [why 3 projects insufficient] |
| [e.g., Repository pattern] | [specific problem] | [why direct DB access insufficient] |

## Phase Outputs

- research.md created at `C:\Projects\AITech\specs\004-etl-reporting-system\research.md`
- data-model.md created at `C:\Projects\AITech\specs\004-etl-reporting-system\data-model.md`
- contracts/reports.openapi.yaml created at `C:\Projects\AITech\specs\004-etl-reporting-system\contracts\reports.openapi.yaml`
- quickstart.md created at `C:\Projects\AITech\specs\004-etl-reporting-system\quickstart.md`
- Agent context updated for `cursor-agent`

## Constitution Check (Post-Design)

- **Backend-First**: ✅ Confirmed — ETL, RBAC, and report generation in backend
- **Component-Based**: ✅ Confirmed — dedicated React components for reports
- **Material-UI**: ✅ Confirmed — specified for all UI
- **Minimal Dependencies**: ✅ Confirmed — all dependencies justified
- **Clean Code**: ✅ Confirmed — plan enforces readability
- **No Tests**: ✅ Confirmed — tests excluded

## Stop Report

- **Branch**: `004-etl-reporting-system`
- **IMPL_PLAN**: `C:\Projects\AITech\specs\004-etl-reporting-system\plan.md`
- **Artifacts Generated**:
  - `research.md`
  - `data-model.md`
  - `contracts/reports.openapi.yaml`
  - `quickstart.md`
- Phase 2 tasks to be created via `/speckit.tasks`.

