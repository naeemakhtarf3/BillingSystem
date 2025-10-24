# Data Model: Patient Admission and Discharge Workflow

**Feature**: Patient Admission and Discharge Workflow  
**Date**: 2024-12-19  
**Database**: PostgreSQL with SQLAlchemy ORM

## Entities

### Room
**Purpose**: Represents physical rooms available for patient admission

**Attributes**:
- `id` (Primary Key): Unique identifier
- `room_number` (String, Unique): Human-readable room identifier (e.g., "101A", "ICU-1")
- `type` (Enum): Room type - `standard`, `private`, `icu`
- `status` (Enum): Current status - `available`, `occupied`, `maintenance`
- `daily_rate_cents` (Integer): Daily rate in cents to avoid floating-point precision issues
- `created_at` (DateTime): Record creation timestamp
- `updated_at` (DateTime): Last modification timestamp

**Validation Rules**:
- `room_number` must be unique across all rooms
- `daily_rate_cents` must be positive integer
- `status` transitions: `available` ↔ `occupied` ↔ `maintenance`
- Cannot delete room with active admissions

**Relationships**:
- One-to-many with `Admission` (room can have multiple admissions over time)
- One-to-many with `Invoice` (room charges appear on invoices)

### Admission
**Purpose**: Tracks patient stays in rooms with billing linkage

**Attributes**:
- `id` (Primary Key): Unique identifier
- `room_id` (Foreign Key): Reference to Room
- `patient_id` (Foreign Key): Reference to existing Patient
- `staff_id` (Foreign Key): Reference to existing Staff (who processed admission)
- `admission_date` (DateTime): When patient was admitted
- `discharge_date` (DateTime, Nullable): When patient was discharged
- `invoice_id` (Foreign Key, Nullable): Reference to generated Invoice
- `status` (Enum): Current status - `active`, `discharged`
- `created_at` (DateTime): Record creation timestamp
- `updated_at` (DateTime): Last modification timestamp

**Validation Rules**:
- `admission_date` must be before `discharge_date` (if not null)
- `discharge_date` can only be set when status is `active`
- `invoice_id` must be set when status is `discharged`
- Cannot admit patient to occupied or maintenance room
- Patient cannot have multiple active admissions

**Relationships**:
- Many-to-one with `Room` (admission belongs to one room)
- Many-to-one with `Patient` (admission belongs to one patient)
- Many-to-one with `Staff` (admission processed by one staff member)
- Many-to-one with `Invoice` (admission generates one invoice)

### Patient (Existing)
**Purpose**: Existing entity representing individuals who can be admitted

**Key Attributes** (referenced by Admission):
- `id` (Primary Key): Unique identifier
- `name` (String): Patient name
- `date_of_birth` (Date): Patient date of birth
- Other existing attributes...

**Validation Rules**:
- Must exist before admission can be created
- Cannot be deleted if has active admissions

### Staff (Existing)
**Purpose**: Existing entity representing healthcare workers

**Key Attributes** (referenced by Admission):
- `id` (Primary Key): Unique identifier
- `name` (String): Staff member name
- `role` (String): Staff role for access control
- Other existing attributes...

**Validation Rules**:
- Must exist before admission can be created
- Must have appropriate role for admission/discharge operations

### Invoice (Existing)
**Purpose**: Existing entity representing billing records

**Key Attributes** (linked to Admission):
- `id` (Primary Key): Unique identifier
- `patient_id` (Foreign Key): Reference to Patient
- `total_amount_cents` (Integer): Total amount in cents
- `status` (Enum): Invoice status
- Other existing attributes...

**Validation Rules**:
- Created automatically when admission is discharged
- Linked to admission for billing tracking

## State Transitions

### Room Status Transitions
```
available → occupied (when patient admitted)
occupied → available (when patient discharged)
available → maintenance (when room marked for maintenance)
maintenance → available (when maintenance completed)
```

### Admission Status Transitions
```
active → discharged (when patient discharged)
```

## Database Constraints

### Unique Constraints
- `rooms.room_number` must be unique
- `admissions` can have only one active admission per patient
- `admissions` can have only one active admission per room

### Foreign Key Constraints
- `admissions.room_id` → `rooms.id`
- `admissions.patient_id` → `patients.id`
- `admissions.staff_id` → `staff.id`
- `admissions.invoice_id` → `invoices.id`

### Check Constraints
- `rooms.daily_rate_cents > 0`
- `admissions.admission_date <= discharge_date` (when discharge_date is not null)
- `admissions.status IN ('active', 'discharged')`
- `rooms.status IN ('available', 'occupied', 'maintenance')`

## Indexes

### Performance Indexes
- `rooms.status` - Fast filtering of available rooms
- `rooms.type` - Fast filtering by room type
- `admissions.status` - Fast filtering of active admissions
- `admissions.patient_id` - Fast lookup of patient admissions
- `admissions.room_id` - Fast lookup of room history
- `admissions.admission_date` - Fast date range queries

### Composite Indexes
- `(rooms.status, rooms.type)` - Combined filtering for room availability
- `(admissions.status, admissions.admission_date)` - Active admissions with date sorting

## Migration Strategy

### Phase 1: Create Tables
1. Create `rooms` table with all attributes
2. Create `admissions` table with foreign key constraints
3. Add indexes for performance

### Phase 2: Data Population
1. Insert initial room data (room numbers, types, rates)
2. Set all rooms to `available` status initially

### Phase 3: Validation
1. Test foreign key constraints
2. Test unique constraints
3. Test state transition logic

## Data Integrity Rules

### Business Rules
1. **Room Availability**: Only one active admission per room
2. **Patient Admission**: Only one active admission per patient
3. **Billing Consistency**: Discharged admissions must have associated invoice
4. **Rate Consistency**: Room rates cannot change during active admission
5. **Staff Authorization**: Only authorized staff can process admissions

### Concurrency Control
1. **Optimistic Locking**: Use `updated_at` timestamp for conflict detection
2. **Atomic Operations**: All admission/discharge operations in single transaction
3. **Status Validation**: Check room status before admission, validate no conflicts

## Data Volume Estimates

### Expected Scale
- **Rooms**: 50-100 rooms per facility
- **Admissions**: 100-500 admissions per month
- **Active Admissions**: 10-50 concurrent at any time
- **Historical Data**: 5+ years of admission history

### Performance Targets
- Room availability queries: <100ms
- Admission creation: <500ms
- Discharge processing: <1s
- Real-time updates: <200ms propagation
