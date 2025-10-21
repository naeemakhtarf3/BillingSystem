# Tasks: ETL Reporting System

**Branch**: `004-etl-reporting-system`
**Spec**: `C:\Projects\AITech\specs\004-etl-reporting-system\spec.md`
**Plan**: `C:\Projects\AITech\specs\004-etl-reporting-system\plan.md`

## Phase 1 — Setup

 - [ ] T001 Configure backend environment variables in `backend/.env` and verify DB connections
 - [X] T002 Create `backend/etl.py` entry script scaffold per plan
 - [ ] T003 Add reporting models file `backend/app/models/report_schema.py`
 - [ ] T004 Add ETL status model `backend/app/models/etl_status.py`
 - [X] T005 Create report services module `backend/app/services/report_service.py`
 - [X] T006 Create ETL service module `backend/app/services/etl_service.py`
 - [X] T007 Add reports API file `backend/app/api/api_v1/endpoints/reports.py`
 - [X] T008 Add report client `frontend/src/services/reportService.js`
 - [X] T009 Add reports page route `frontend/src/pages/staff/Reports.jsx`

## Phase 2 — Foundational

 - [X] T010 Implement reporting schema DDL and migrations in `backend/alembic/versions/*`
 - [X] T011 Implement indexing per data-model in `backend/alembic/versions/*`
- [X] T012 Implement RBAC guard utilities in `backend/app/core/security.py`
- [X] T013 Implement audit logging hooks in `backend/app/services/audit_service.py`
- [X] T014 Wire OpenAPI contract to FastAPI routes in `backend/app/api/api_v1/endpoints/reports.py`

## Phase 3 — [US1] Revenue Analytics Dashboard (P1)

- [X] T015 [US1] Implement revenue ETL aggregation in `backend/app/services/etl_service.py`
- [X] T016 [US1] Implement revenue report query in `backend/app/services/report_service.py`
- [X] T017 [US1] Implement `GET /api/v1/reports/revenue` in `backend/app/api/api_v1/endpoints/reports.py`
 - [X] T018 [US1] Add PDF export for revenue in `backend/app/services/report_service.py`
- [ ] T019 [US1] Create `RevenueCharts.jsx` in `frontend/src/components/reports/RevenueCharts.jsx`
- [ ] T020 [US1] Create filters UI in `frontend/src/components/reports/ReportFilters.jsx`
- [ ] T021 [US1] Integrate revenue view in `frontend/src/pages/staff/Reports.jsx`
 - [X] T019 [US1] Create `RevenueCharts.jsx` in `frontend/src/components/reports/RevenueCharts.jsx`
 - [X] T020 [US1] Create filters UI in `frontend/src/components/reports/ReportFilters.jsx`
 - [X] T021 [US1] Integrate revenue view in `frontend/src/pages/staff/Reports.jsx`

## Phase 4 — [US2] Patient Payment History (P2)

- [X] T022 [US2] Implement patient history ETL in `backend/app/services/etl_service.py`
 - [X] T023 [US2] Implement patient history query in `backend/app/services/report_service.py`
- [X] T024 [US2] Implement `GET /api/v1/reports/patients/{patientId}/history` in `backend/app/api/api_v1/endpoints/reports.py`
- [ ] T025 [US2] Create `PatientSearch.jsx` in `frontend/src/components/reports/PatientSearch.jsx`
- [ ] T026 [US2] Add patient history table in `frontend/src/components/reports/PatientHistoryTable.jsx`
- [ ] T027 [US2] Integrate patient history into `frontend/src/pages/staff/Reports.jsx`

## Phase 5 — [US3] Outstanding Payments (P2)

- [X] T028 [US3] Implement outstanding ETL in `backend/app/services/etl_service.py`
- [X] T029 [US3] Implement outstanding query in `backend/app/services/report_service.py`
- [X] T030 [US3] Implement `GET /api/v1/reports/outstanding` in `backend/app/api/api_v1/endpoints/reports.py`
 - [X] T031 [US3] Create `OutstandingPayments.jsx` in `frontend/src/components/reports/OutstandingPayments.jsx`
 - [X] T032 [US3] Add export controls in `frontend/src/components/common/ExportControls.jsx`
 - [X] T033 [US3] Integrate outstanding view into `frontend/src/pages/staff/Reports.jsx`

## Phase 6 — [US4] Automated Data Processing (P3)

 - [X] T034 [US4] Implement ETL scheduler interface (cron docs) in `backend/etl.py`
 - [X] T035 [US4] Implement ETL status tracking in `backend/app/models/etl_status.py`
 - [X] T036 [US4] Implement stop-and-alert failure handling in `backend/app/services/etl_service.py`
 - [X] T037 [US4] Add admin trigger endpoint `POST /api/v1/reports/etl/run` in `backend/app/api/api_v1/endpoints/reports.py`

## Final Phase — Polish & Cross-Cutting

 - [X] T038 Ensure HIPAA de-identification in all responses in `backend/app/services/report_service.py`
 - [X] T039 Ensure WCAG color usage in UI `frontend/src/*`
 - [X] T040 Add PDF-only export logic in `backend/app/services/report_service.py`
 - [X] T041 Update README quickstart references `specs/004-etl-reporting-system/quickstart.md`

## Dependencies
- US1 → US2, US3 (re-uses ETL + schema)
- US4 independent, but depends on foundational ETL scaffolding

## Parallel Opportunities
- [P] Frontend components (`frontend/src/components/reports/*`) can proceed in parallel with backend services after contracts are defined
- [P] Migrations and model files can proceed in parallel with API scaffolding

## Implementation Strategy (MVP)
- Deliver US1 (Revenue Analytics Dashboard) end-to-end first, including API + UI + PDF export
