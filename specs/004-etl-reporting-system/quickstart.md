# Quickstart: ETL Reporting System

## Prerequisites
- Backend environment variables configured (see backend/env.example)
- Database initialized and migrated
- User with appropriate RBAC role (admin/finance/staff/collections)

## Run ETL

### On-demand
```bash
python backend/etl.py --from "YYYY-MM-DD" --to "YYYY-MM-DD"
```

### Scheduled (cron)
```bash
# Every 4 hours
0 */4 * * * /usr/bin/python /app/backend/etl.py >> /var/log/etl.log 2>&1
```

## API Usage

Base URL: `/api/v1`

### Revenue Report
```http
GET /api/v1/reports/revenue?start_date=2025-01-01&end_date=2025-01-31&granularity=day
Accept: application/json
Authorization: Bearer <token>
```

PDF export:
```http
GET /api/v1/reports/revenue?start_date=2025-01-01&end_date=2025-01-31&granularity=day&format=pdf
Accept: application/pdf
Authorization: Bearer <token>
```

### Patient Payment History
```http
GET /api/v1/reports/patients/{patientId}/history?start_date=2025-01-01&end_date=2025-01-31
Accept: application/json
Authorization: Bearer <token>
```

### Outstanding Payments
```http
GET /api/v1/reports/outstanding?min_days_overdue=30&min_amount=50
Accept: application/json
Authorization: Bearer <token>
```

## Frontend
- Navigate to `/staff/reports`
- Use filters to adjust date range and status
- Export via "Download PDF" controls (PDF only)

## Compliance & Security
- Patient data in reports is partially de-identified (patient ID only)
- All report access is audit-logged
- Data retention: 1 year
- Ensure HTTPS and secure secrets management
