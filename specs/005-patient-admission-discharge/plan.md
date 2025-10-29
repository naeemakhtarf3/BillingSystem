# Implementation Plan: Patient Admission and Discharge Workflow

**Branch**: `005-patient-admission-discharge` | **Date**: 2024-12-19 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/005-patient-admission-discharge/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Implement a comprehensive patient admission and discharge workflow system that enables healthcare staff to manage room assignments, track patient stays, and automate billing calculations. The system will provide real-time room availability, prevent double booking, and integrate seamlessly with existing billing infrastructure.

## Technical Context

**Language/Version**: Python 3.11, JavaScript ES6+  
**Primary Dependencies**: FastAPI, SQLAlchemy, Alembic, React 18, Material-UI, Vite  
**Storage**: PostgreSQL (existing), SQLite for development  
**Testing**: pytest (backend), Jest (frontend)  
**Target Platform**: Web application (Linux server deployment)  
**Project Type**: Web application (backend + frontend)  
**Performance Goals**: <2 minutes admission completion, <5 seconds room filtering, 100% concurrency control  
**Constraints**: Real-time updates for room status, transactional integrity, role-based access  
**Scale/Scope**: Multi-user healthcare facility, 50+ rooms, concurrent admissions

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- **Backend-First**: All business logic MUST be implemented in Python backend
- **Component-Based**: Frontend features MUST be separate React components
- **Material-UI**: All frontend styling MUST use Material-UI components
- **Minimal Dependencies**: Each dependency MUST be justified
- **Clean Code**: Code MUST be readable and well-documented
- **No Tests**: Test cases are explicitly excluded from this project

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
│   ├── models/           # Database models (Room, Admission)
│   ├── services/          # Business logic (admission, billing)
│   ├── api/
│   │   └── api_v1/
│   │       └── endpoints/  # REST endpoints (/admissions)
│   ├── schemas/           # Pydantic schemas
│   └── core/              # Configuration
├── alembic/               # Database migrations
└── tests/                 # Backend tests

frontend/
├── src/
│   ├── components/        # React components
│   │   ├── admissions/    # Admission-specific components
│   │   └── rooms/         # Room management components
│   ├── pages/             # Page components
│   ├── services/          # API client services
│   └── contexts/          # React contexts
└── tests/                 # Frontend tests
```

**Structure Decision**: Web application structure with separate backend and frontend directories. Backend uses FastAPI with SQLAlchemy models, frontend uses React with Material-UI components. Database migrations handled by Alembic.

## Phase 0: Research Complete ✅

**Research Document**: [research.md](./research.md)

**Key Decisions Made**:
- PostgreSQL with SQLAlchemy ORM for data persistence
- Optimistic locking for concurrency control
- RESTful API with FastAPI for backend
- WebSocket for real-time updates
- React with Material-UI for frontend
- Context API for state management
- Direct database integration for billing
- Transactional billing calculation
- Structured error responses
- Role-based access control
- Service layer pattern for business logic

## Phase 1: Design Complete ✅

**Generated Artifacts**:
- **Data Model**: [data-model.md](./data-model.md) - Complete database schema with entities, relationships, constraints, and indexes
- **API Contracts**: [contracts/openapi.yaml](./contracts/openapi.yaml) - Full OpenAPI specification for all endpoints
- **Quickstart Guide**: [quickstart.md](./quickstart.md) - Step-by-step setup and testing instructions

**Design Decisions**:
- Room and Admission entities with proper relationships
- Optimistic locking using updated_at timestamps
- Comprehensive API with filtering and validation
- Real-time updates via WebSocket
- Transactional integrity across all operations
- Performance-optimized database indexes

## Complexity Tracking

*No Constitution Check violations - all design decisions align with project constraints*

| Design Choice | Justification | Alternative Considered |
|---------------|----------------|-------------------------|
| WebSocket for real-time | Essential for room availability updates | Polling (inefficient), SSE (limited) |
| Optimistic locking | Prevents double booking with clear errors | Pessimistic locking (deadlock risk) |
| Service layer pattern | Separates business logic from API | Fat controllers (tight coupling) |
| Material-UI components | Consistent with existing frontend | Custom CSS (time-consuming) |

