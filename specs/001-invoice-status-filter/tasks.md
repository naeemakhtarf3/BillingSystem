# Tasks: Invoice Status Filter

**Input**: Design documents from `/specs/001-invoice-status-filter/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: Tests are explicitly excluded from this project per constitution. Focus on functional implementation only.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`
- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions
- **Backend**: `backend/app/` for Python FastAPI structure
- **Frontend**: `frontend/src/` for React components
- **Components**: Each feature gets its own component file
- **API Endpoints**: All in backend project only
- Paths shown below assume web app structure - adjust based on plan.md structure

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [ ] T001 Create StatusFilterDropdown component directory structure in frontend/src/components/
- [ ] T002 [P] Verify Material-UI dependencies are available in frontend/package.json
- [ ] T003 [P] Create component props interface types in frontend/src/types/invoice.ts

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [ ] T004 Create StatusFilterDropdown component file in frontend/src/components/StatusFilterDropdown.jsx
- [ ] T005 [P] Create filter state management hooks in frontend/src/hooks/useFilterState.js
- [ ] T006 [P] Create localStorage utility functions in frontend/src/utils/localStorage.js
- [ ] T007 Create filter logic utility functions in frontend/src/utils/filterUtils.js
- [ ] T008 Create error handling utilities in frontend/src/utils/errorHandling.js

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Filter Invoices by Status (Priority: P1) 🎯 MVP

**Goal**: Enable staff to filter invoices by status (All, Paid, Issued) with immediate visual feedback

**Independent Test**: Can be fully tested by selecting different filter options and verifying that only matching invoices are displayed, delivering immediate value for invoice management workflow.

### Implementation for User Story 1

- [ ] T009 [P] [US1] Create StatusFilterDropdown component structure in frontend/src/components/StatusFilterDropdown.jsx
- [ ] T010 [P] [US1] Implement Material-UI Select component with filter options in frontend/src/components/StatusFilterDropdown.jsx
- [ ] T011 [US1] Implement filter state management with useState hook in frontend/src/components/StatusFilterDropdown.jsx
- [ ] T012 [US1] Implement filter application logic with array.filter() in frontend/src/components/StatusFilterDropdown.jsx
- [ ] T013 [US1] Implement onFilterChange callback integration in frontend/src/components/StatusFilterDropdown.jsx
- [ ] T014 [US1] Add immediate filter application on selection change in frontend/src/components/StatusFilterDropdown.jsx
- [ ] T015 [US1] Style component to match existing blue theme in frontend/src/components/StatusFilterDropdown.jsx

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently

---

## Phase 4: User Story 2 - Persist Filter Selection (Priority: P2)

**Goal**: Maintain filter selection across page reloads and navigation to preserve user workflow context

**Independent Test**: Can be fully tested by selecting a filter, navigating away and back, or refreshing the page, and verifying the filter selection is maintained.

### Implementation for User Story 2

- [ ] T016 [P] [US2] Implement localStorage load functionality in frontend/src/components/StatusFilterDropdown.jsx
- [ ] T017 [US2] Implement localStorage save functionality in frontend/src/components/StatusFilterDropdown.jsx
- [ ] T018 [US2] Add filter state persistence on component mount in frontend/src/components/StatusFilterDropdown.jsx
- [ ] T019 [US2] Add filter state persistence on selection change in frontend/src/components/StatusFilterDropdown.jsx
- [ ] T020 [US2] Implement error handling for localStorage failures in frontend/src/components/StatusFilterDropdown.jsx
- [ ] T021 [US2] Add fallback to default filter if localStorage unavailable in frontend/src/components/StatusFilterDropdown.jsx

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently

---

## Phase 5: User Story 3 - Handle Empty Filter Results (Priority: P3)

**Goal**: Provide clear feedback when filter selection results in no matching invoices

**Independent Test**: Can be fully tested by selecting a filter that results in no matches and verifying that an appropriate message is displayed.

### Implementation for User Story 3

- [ ] T022 [P] [US3] Create NoResultsMessage component in frontend/src/components/NoResultsMessage.jsx
- [ ] T023 [US3] Implement empty state detection logic in frontend/src/components/StatusFilterDropdown.jsx
- [ ] T024 [US3] Add NoResultsMessage display when no invoices match filter in frontend/src/components/StatusFilterDropdown.jsx
- [ ] T025 [US3] Style NoResultsMessage to match existing theme in frontend/src/components/NoResultsMessage.jsx
- [ ] T026 [US3] Add proper accessibility attributes to NoResultsMessage in frontend/src/components/NoResultsMessage.jsx

**Checkpoint**: All user stories should now be independently functional

---

## Phase 6: Integration & Polish

**Purpose**: Integration with existing invoice management system and final polish

- [ ] T027 [P] Integrate StatusFilterDropdown with existing invoice table in frontend/src/pages/staff/InvoicesPage.jsx
- [ ] T028 [P] Update invoice table to use filtered data in frontend/src/pages/staff/InvoicesPage.jsx
- [ ] T029 Add component documentation and comments in frontend/src/components/StatusFilterDropdown.jsx
- [ ] T030 Add error boundary handling for component failures in frontend/src/components/StatusFilterDropdown.jsx
- [ ] T031 [P] Add performance optimization with useMemo for large datasets in frontend/src/components/StatusFilterDropdown.jsx
- [ ] T032 [P] Add accessibility improvements and ARIA labels in frontend/src/components/StatusFilterDropdown.jsx
- [ ] T033 Validate component works with existing invoice data structure in frontend/src/pages/staff/InvoicesPage.jsx
- [ ] T034 Add console logging for debugging in development mode in frontend/src/components/StatusFilterDropdown.jsx

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3+)**: All depend on Foundational phase completion
  - User stories can then proceed in parallel (if staffed)
  - Or sequentially in priority order (P1 → P2 → P3)
- **Polish (Final Phase)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P2)**: Can start after Foundational (Phase 2) - May integrate with US1 but should be independently testable
- **User Story 3 (P3)**: Can start after Foundational (Phase 2) - May integrate with US1/US2 but should be independently testable

### Within Each User Story

- Backend models before services
- Backend services before API endpoints
- Backend API endpoints before frontend components
- Frontend components before integration
- Story complete before moving to next priority

### Parallel Opportunities

- All Setup tasks marked [P] can run in parallel
- All Foundational tasks marked [P] can run in parallel (within Phase 2)
- Once Foundational phase completes, all user stories can start in parallel (if team capacity allows)
- All tests for a user story marked [P] can run in parallel
- Models within a story marked [P] can run in parallel
- Different user stories can be worked on in parallel by different team members

---

## Parallel Example: User Story 1

```bash
# Launch all backend models for User Story 1 together:
Task: "Create StatusFilterDropdown component structure in frontend/src/components/StatusFilterDropdown.jsx"
Task: "Implement Material-UI Select component with filter options in frontend/src/components/StatusFilterDropdown.jsx"

# Launch all frontend components for User Story 1 together:
Task: "Implement filter state management with useState hook in frontend/src/components/StatusFilterDropdown.jsx"
Task: "Implement filter application logic with array.filter() in frontend/src/components/StatusFilterDropdown.jsx"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1
4. **STOP and VALIDATE**: Test User Story 1 independently
5. Deploy/demo if ready

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → Deploy/Demo (MVP!)
3. Add User Story 2 → Test independently → Deploy/Demo
4. Add User Story 3 → Test independently → Deploy/Demo
5. Each story adds value without breaking previous stories

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Developer A: User Story 1
   - Developer B: User Story 2
   - Developer C: User Story 3
3. Stories complete and integrate independently

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Verify backend API endpoints work before frontend integration
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Avoid: vague tasks, same file conflicts, cross-story dependencies that break independence
