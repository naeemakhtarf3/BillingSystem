# Feature Specification: Patient Admission and Discharge Workflow

**Feature Branch**: `005-patient-admission-discharge`  
**Created**: 2024-12-19  
**Status**: Draft  
**Input**: User description: "You are a senior software engineer with extensive expertise in designing and implementing healthcare management systems, specifically those involving patient workflows and billing integrations. Your task is to architect and develop a robust Patient Admission and Discharge Workflow within an existing Clinic Billing System built on a FastAPI/PostgreSQL backend and React/Vite frontend."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Admitting a Patient to a Room (Priority: P1)

A healthcare staff member needs to admit a patient to an available room, ensuring proper room assignment and billing setup.

**Why this priority**: This is the core functionality that enables the entire admission workflow. Without this, the system cannot track patient stays or generate appropriate billing.

**Independent Test**: Can be fully tested by creating a new admission record with room assignment and verifying that the room status updates to occupied and billing records are initialized.

**Acceptance Scenarios**:

1. **Given** a patient exists in the system and an available room exists, **When** staff admits the patient to the room, **Then** the admission record is created with proper room assignment and the room status changes to occupied
2. **Given** a patient exists but no rooms are available, **When** staff attempts to admit the patient, **Then** the system displays an error message and prevents admission
3. **Given** a patient and available room exist, **When** staff admits the patient with required information, **Then** the system creates an invoice record linked to the admission for billing purposes

---

### User Story 2 - Viewing Available Rooms (Priority: P1)

Healthcare staff need to view and filter available rooms by type and status to make informed admission decisions.

**Why this priority**: Essential for the admission process - staff must be able to see what rooms are available before admitting patients.

**Independent Test**: Can be fully tested by displaying a list of rooms with their current status and filtering capabilities, without requiring any patient admission functionality.

**Acceptance Scenarios**:

1. **Given** rooms exist in the system with different types and statuses, **When** staff views the room list, **Then** they can see all rooms with their current status and type
2. **Given** rooms exist with different types, **When** staff filters by room type, **Then** only rooms of the selected type are displayed
3. **Given** rooms exist with different statuses, **When** staff filters by available status, **Then** only available rooms are displayed

---

### User Story 3 - Discharging a Patient (Priority: P1)

Healthcare staff need to discharge patients, which triggers billing calculation and updates room availability.

**Why this priority**: Completes the patient workflow and ensures proper billing calculation. Essential for room turnover and financial accuracy.

**Independent Test**: Can be fully tested by discharging an active admission and verifying that billing is calculated correctly, room status is updated, and admission status changes to discharged.

**Acceptance Scenarios**:

1. **Given** a patient is actively admitted to a room, **When** staff discharges the patient, **Then** the system calculates total charges based on room rate and stay duration, updates the admission status to discharged, and marks the room as available
2. **Given** a patient is admitted for multiple days, **When** staff discharges the patient, **Then** the system calculates charges for the full duration of stay
3. **Given** a patient is discharged, **When** the discharge is processed, **Then** the system generates a final invoice with all charges and updates room availability

---

### User Story 4 - Viewing Active Admissions (Priority: P2)

Healthcare staff need to monitor all currently active patient admissions for operational oversight.

**Why this priority**: Important for operational management and patient care coordination, but not critical for the core admission/discharge workflow.

**Independent Test**: Can be fully tested by displaying a list of all active admissions with patient and room information, without requiring admission or discharge actions.

**Acceptance Scenarios**:

1. **Given** multiple patients are admitted, **When** staff views active admissions, **Then** they can see all currently active admissions with patient details and room assignments
2. **Given** active admissions exist, **When** staff views the admissions list, **Then** they can see admission dates and current room assignments
3. **Given** admissions exist with different statuses, **When** staff views active admissions, **Then** only active (non-discharged) admissions are displayed

---

### User Story 5 - Room Management and Maintenance (Priority: P3)

Healthcare staff need to manage room status for maintenance and operational needs.

**Why this priority**: Important for operational efficiency but not essential for the core patient workflow.

**Independent Test**: Can be fully tested by updating room status to maintenance and back to available, without affecting patient admissions.

**Acceptance Scenarios**:

1. **Given** a room is available, **When** staff marks it for maintenance, **Then** the room status changes to maintenance and is excluded from available room listings
2. **Given** a room is in maintenance status, **When** staff completes maintenance, **Then** the room status changes back to available and appears in available room listings

---

### Edge Cases

- What happens when a patient is admitted to a room that becomes unavailable during their stay?
- How does the system handle concurrent admission attempts to the same room? (First-come-first-served by timestamp, others get "room no longer available" error)
- What happens when discharge is attempted on a patient who is not currently admitted? (Show specific error message with suggested actions)
- How does the system handle billing calculation for partial day stays? (Hourly rate for same-day admission/discharge)
- What happens when a room is marked for maintenance while a patient is still admitted?
- What happens when form validation fails during admission? (Show specific errors immediately, prevent submission)
- How does the system handle network failures during admission processing? (Rollback changes, show retry option)
- What happens when real-time updates fail to reach some user sessions? (Graceful degradation, manual refresh option)

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST allow staff to admit patients to available rooms with proper validation
- **FR-002**: System MUST prevent admission to occupied or maintenance rooms
- **FR-003**: System MUST automatically calculate billing based on room daily rates and admission duration (full day for ≥24 hours, hourly rate for same-day stays)
- **FR-004**: System MUST update room status to occupied when patient is admitted
- **FR-005**: System MUST allow staff to discharge patients and update room status to available
- **FR-006**: System MUST generate invoices linked to patient admissions for billing purposes
- **FR-007**: System MUST display available rooms with filtering by type and status
- **FR-008**: System MUST show active admissions with patient and room information
- **FR-009**: System MUST prevent double booking of rooms through concurrency control (first-come-first-served by timestamp)
- **FR-010**: System MUST maintain transactional integrity across admission, room, and billing operations
- **FR-011**: System MUST validate that only existing patients can be admitted
- **FR-012**: System MUST validate that only existing staff can process admissions
- **FR-013**: System MUST calculate partial day charges for same-day admissions and discharges
- **FR-014**: System MUST support room status management (available/occupied/maintenance)
- **FR-015**: System MUST enforce role-based access controls for admission and discharge operations
- **FR-016**: System MUST validate all admission data on form submission before processing
- **FR-017**: System MUST show specific error messages with suggested actions when operations fail
- **FR-018**: System MUST rollback changes and allow retry when operations fail
- **FR-019**: System MUST provide real-time updates for room availability and active admission status

### Key Entities *(include if feature involves data)*

- **Room**: Represents physical rooms with attributes for room number, type (standard/private/icu), status (available/occupied/maintenance), and daily rate. Central to the admission workflow.
- **Admission**: Represents patient stays with room assignments, staff assignments, admission/discharge dates, and billing linkage. Core entity that connects patients to rooms and billing.
- **Patient**: Existing entity representing individuals who can be admitted. Must exist before admission can occur.
- **Staff**: Existing entity representing healthcare workers who can process admissions and discharges.
- **Invoice**: Existing entity representing billing records that are automatically created and linked to admissions for financial tracking.

### Frontend Components *(include if feature has UI)*

- **Room Management Dashboard**: Displays available rooms with filtering capabilities, shows room status and type information
- **Admission Form**: Allows staff to admit patients by selecting available rooms and entering admission details
- **Active Admissions List**: Shows all currently active patient admissions with patient and room information
- **Discharge Workflow**: Provides interface for discharging patients with billing summary and confirmation
- **Room Status Manager**: Allows staff to update room status for maintenance and operational needs

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Staff can complete patient admission in under 2 minutes from room selection to confirmation
- **SC-002**: System prevents 100% of double booking attempts through concurrency control
- **SC-003**: Billing calculations are accurate to within 1 cent for all admission durations
- **SC-004**: Room availability updates in real-time across all user sessions
- **SC-005**: Staff can view and filter available rooms in under 5 seconds
- **SC-006**: Discharge process completes with billing summary in under 1 minute
- **SC-007**: System maintains data consistency across all admission, room, and billing operations
- **SC-008**: 95% of admission operations complete without requiring manual intervention
- **SC-009**: Room status changes are reflected immediately in all active user sessions
- **SC-010**: Billing integration maintains 99.9% accuracy in charge calculations

## Clarifications

### Session 2024-12-19

- Q: Billing calculation rules for different admission patterns → A: Full day charge for stays ≥24 hours, partial day (hourly rate) for same-day admission/discharge
- Q: Error handling strategy for failed operations → A: Show specific error messages with suggested actions, rollback changes, allow retry
- Q: Room assignment priority for concurrent requests → A: First-come-first-served based on system timestamp, others get "room no longer available"
- Q: Real-time updates scope across user sessions → A: Real-time updates only for room availability and active admission status
- Q: Data validation timing for admission operations → A: Validate on form submission before processing, show errors immediately

## Assumptions

- Patients must exist in the system before admission can occur
- Staff members must be authenticated and authorized to perform admission/discharge operations
- Room daily rates are pre-configured and do not change during patient stays
- Billing calculations use standard business rules (full day charges for multi-day stays, partial day charges for same-day admission/discharge)
- System operates in a single timezone for date/time calculations
- Room maintenance does not affect existing patient admissions
- All financial calculations are performed in cents to avoid floating-point precision issues
- Staff have appropriate permissions based on their role for admission/discharge operations