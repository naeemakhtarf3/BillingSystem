<!--
Sync Impact Report:
Version change: 1.0.0 → 1.0.0 (initial creation)
Modified principles: N/A (initial creation)
Added sections: Core Principles, Architecture Standards, Development Workflow, Governance
Removed sections: N/A (initial creation)
Templates requiring updates: 
  ✅ plan-template.md (updated for backend/frontend structure)
  ✅ spec-template.md (updated for component-based frontend)
  ✅ tasks-template.md (updated for backend/frontend separation)
Follow-up TODOs: None
-->

# Clinic Billing System Constitution

## Core Principles

### I. Backend-First API Design
All business logic and data operations MUST be implemented in the Python backend. The backend serves as the single source of truth for all data operations, business rules, and API endpoints. Frontend components are purely presentational and MUST NOT contain business logic.

### II. Component-Based Frontend Architecture
Every distinct feature MUST be implemented as a separate React component. Components MUST be self-contained, reusable, and focused on a single responsibility. Material-UI MUST be used for all styling and UI components.

### III. Minimal Dependencies
Dependencies MUST be kept to the absolute minimum required for functionality. Each dependency MUST be justified and documented. Avoid adding libraries for convenience - prefer native solutions or existing dependencies.

### IV. Clean Code Standards
Code MUST be written with clarity, maintainability, and readability as primary concerns. Functions MUST be small, focused, and well-documented. Variable names MUST be descriptive and self-documenting.

### V. No Test Cases
Test cases are explicitly excluded from this project. Focus MUST be on delivering functional features rather than comprehensive testing coverage.

## Architecture Standards

### Backend Structure
- **Language**: Python with FastAPI framework
- **Database**: SQLAlchemy ORM with PostgreSQL
- **Authentication**: JWT-based with role-based access control
- **API Design**: RESTful endpoints with OpenAPI documentation
- **File Organization**: Models, services, and API endpoints in separate modules

### Frontend Structure
- **Framework**: React with Vite build system
- **Styling**: Material-UI components exclusively
- **State Management**: React Context API for global state
- **Component Organization**: One component per feature, organized by domain
- **Routing**: React Router for navigation

### API Endpoint Standards
- All endpoints MUST be implemented in the backend project
- Endpoints MUST follow RESTful conventions
- Authentication MUST be required for all protected endpoints
- Error responses MUST be consistent and informative

## Development Workflow

### Feature Development Process
1. **Backend First**: Implement API endpoints and business logic in Python backend
2. **Frontend Integration**: Create React components to consume backend APIs
3. **Component Isolation**: Each feature component MUST be independently functional
4. **Material-UI Integration**: Use Material-UI components for all UI elements

### Code Organization
- **Backend**: Organize by domain (models, services, API endpoints)
- **Frontend**: Organize by feature with dedicated components
- **Shared Logic**: Keep business logic in backend, presentation logic in frontend
- **Dependencies**: Minimize and justify all external dependencies

### Quality Gates
- Code MUST be clean and readable
- Components MUST be focused and reusable
- APIs MUST be well-documented
- Dependencies MUST be minimal and justified

## Governance

This constitution supersedes all other development practices and MUST be followed for all feature development. Amendments require documentation of the change rationale and impact assessment.

**Version**: 1.0.0 | **Ratified**: 2024-01-15 | **Last Amended**: 2024-01-15