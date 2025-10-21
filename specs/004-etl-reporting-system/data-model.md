# Data Model: ETL Reporting System

**Feature**: 004-etl-reporting-system  
**Date**: 2024-12-19  
**Purpose**: Define reporting schema and data relationships

## Reporting Schema Design

### Core Entities

#### Revenue Metrics (Fact Table)
```sql
CREATE TABLE revenue_metrics (
    id SERIAL PRIMARY KEY,
    date_key DATE NOT NULL,
    total_revenue DECIMAL(10,2) NOT NULL,
    payment_count INTEGER NOT NULL,
    average_payment DECIMAL(10,2) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Fields**:
- `id`: Primary key
- `date_key`: Date dimension key for time-based analysis
- `total_revenue`: Aggregated revenue amount
- `payment_count`: Number of payments processed
- `average_payment`: Calculated average payment amount
- `created_at`: Record creation timestamp
- `updated_at`: Record update timestamp

**Validation Rules**:
- `total_revenue` must be >= 0
- `payment_count` must be >= 0
- `average_payment` must be >= 0
- `date_key` cannot be in the future

#### Patient Payment History (Fact Table)
```sql
CREATE TABLE patient_payment_history (
    id SERIAL PRIMARY KEY,
    patient_id VARCHAR(50) NOT NULL,  -- De-identified patient ID
    payment_date DATE NOT NULL,
    amount DECIMAL(10,2) NOT NULL,
    payment_status VARCHAR(20) NOT NULL,
    invoice_id VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Fields**:
- `id`: Primary key
- `patient_id`: De-identified patient identifier (HIPAA compliant)
- `payment_date`: Date of payment
- `amount`: Payment amount
- `payment_status`: Status (paid, pending, failed, refunded)
- `invoice_id`: Reference to original invoice
- `created_at`: Record creation timestamp

**Validation Rules**:
- `amount` must be > 0
- `payment_status` must be one of: paid, pending, failed, refunded
- `patient_id` cannot be null (required for HIPAA compliance)
- `payment_date` cannot be in the future

#### Outstanding Payments (Fact Table)
```sql
CREATE TABLE outstanding_payments (
    id SERIAL PRIMARY KEY,
    patient_id VARCHAR(50) NOT NULL,
    invoice_id VARCHAR(50) NOT NULL,
    amount_due DECIMAL(10,2) NOT NULL,
    days_overdue INTEGER NOT NULL,
    last_payment_date DATE,
    payment_status VARCHAR(20) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Fields**:
- `id`: Primary key
- `patient_id`: De-identified patient identifier
- `invoice_id`: Invoice reference
- `amount_due`: Outstanding amount
- `days_overdue`: Number of days past due
- `last_payment_date`: Date of last payment attempt
- `payment_status`: Current status (overdue, collection, written_off)
- `created_at`: Record creation timestamp
- `updated_at`: Record update timestamp

**Validation Rules**:
- `amount_due` must be > 0
- `days_overdue` must be >= 0
- `payment_status` must be one of: overdue, collection, written_off
- `patient_id` and `invoice_id` cannot be null

#### ETL Process Status (Dimension Table)
```sql
CREATE TABLE etl_process_status (
    id SERIAL PRIMARY KEY,
    process_name VARCHAR(100) NOT NULL,
    status VARCHAR(20) NOT NULL,
    started_at TIMESTAMP NOT NULL,
    completed_at TIMESTAMP,
    records_processed INTEGER DEFAULT 0,
    error_message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Fields**:
- `id`: Primary key
- `process_name`: Name of ETL process
- `status`: Process status (running, completed, failed, stopped)
- `started_at`: Process start time
- `completed_at`: Process completion time
- `records_processed`: Number of records processed
- `error_message`: Error details if process failed
- `created_at`: Record creation timestamp

**Validation Rules**:
- `status` must be one of: running, completed, failed, stopped
- `started_at` cannot be null
- `completed_at` must be after `started_at` if not null

#### Audit Log (Dimension Table)
```sql
CREATE TABLE audit_log (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(50) NOT NULL,
    action VARCHAR(100) NOT NULL,
    resource_type VARCHAR(50) NOT NULL,
    resource_id VARCHAR(50),
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ip_address INET,
    user_agent TEXT
);
```

**Fields**:
- `id`: Primary key
- `user_id`: User who performed the action
- `action`: Action performed (view_report, export_data, etc.)
- `resource_type`: Type of resource accessed
- `resource_id`: Specific resource identifier
- `timestamp`: When the action occurred
- `ip_address`: User's IP address
- `user_agent`: User's browser information

**Validation Rules**:
- `user_id` cannot be null
- `action` cannot be null
- `resource_type` cannot be null
- `timestamp` cannot be null

## Relationships

### Primary Relationships
- **Revenue Metrics** → **Date Dimension**: One-to-many (date_key)
- **Patient Payment History** → **Patient Dimension**: One-to-many (patient_id)
- **Outstanding Payments** → **Patient Dimension**: One-to-many (patient_id)
- **Audit Log** → **User Dimension**: One-to-many (user_id)

### Data Flow
1. **Source Data**: Invoice and payment data from existing SQLite database
2. **ETL Process**: Pandas transformation with SQLAlchemy persistence
3. **Reporting Schema**: Star schema with fact and dimension tables
4. **API Access**: RESTful endpoints with RBAC authentication
5. **Frontend Display**: React components with Recharts visualization

## Indexing Strategy

### Performance Indexes
```sql
-- Revenue metrics indexes
CREATE INDEX idx_revenue_metrics_date ON revenue_metrics(date_key);
CREATE INDEX idx_revenue_metrics_created ON revenue_metrics(created_at);

-- Patient payment history indexes
CREATE INDEX idx_patient_payment_patient ON patient_payment_history(patient_id);
CREATE INDEX idx_patient_payment_date ON patient_payment_history(payment_date);
CREATE INDEX idx_patient_payment_status ON patient_payment_history(payment_status);

-- Outstanding payments indexes
CREATE INDEX idx_outstanding_patient ON outstanding_payments(patient_id);
CREATE INDEX idx_outstanding_days ON outstanding_payments(days_overdue);
CREATE INDEX idx_outstanding_status ON outstanding_payments(payment_status);

-- Audit log indexes
CREATE INDEX idx_audit_user ON audit_log(user_id);
CREATE INDEX idx_audit_timestamp ON audit_log(timestamp);
CREATE INDEX idx_audit_action ON audit_log(action);
```

## Data Retention

### Retention Policy
- **Report Data**: 1 year (as specified in clarifications)
- **Audit Logs**: 1 year (compliance requirement)
- **ETL Status**: 6 months (operational monitoring)
- **Source Data**: Retained in original SQLite database

### Cleanup Process
- Automated cleanup job runs monthly
- Removes data older than retention period
- Maintains referential integrity
- Logs cleanup activities in audit log

## HIPAA Compliance

### De-identification Strategy
- **Patient ID**: Retained for operational use (de-identified)
- **Patient Name**: Removed from all reports
- **SSN**: Removed from all reports
- **Contact Info**: Removed from all reports
- **Medical Data**: Not included in reporting schema

### Access Controls
- Role-based access to different report types
- Audit logging for all data access
- User authentication required for all endpoints
- Data encryption in transit and at rest
