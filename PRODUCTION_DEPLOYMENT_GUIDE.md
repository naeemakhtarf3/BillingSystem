# Production Database Deployment Guide

## Overview
This guide covers the changes made to integrate your local development environment with the production database (Neon PostgreSQL).

## Changes Made

### 1. Model Integration
- **Updated `backend/app/models/__init__.py`**: Added missing model imports for `Room`, `Admission`, `ETLProcessStatus`, and their enums
- **Fixed model inconsistencies**: Updated `Admission` model to use `String` for `invoice_id` to match the `Invoice` model's UUID type

### 2. Database Migration
- **Updated `backend/alembic.ini`**: Commented out hardcoded SQLite URL to use dynamic configuration
- **Created migration `006_fix_model_inconsistencies.py`**: Fixes differences between migration and model definitions
- **Updated `backend/alembic/env.py`**: Already configured to use dynamic database URL from settings

### 3. Configuration
- **Production database URL**: Already configured in `backend/app/core/config.py` for Neon PostgreSQL
- **Environment detection**: Uses `ENVIRONMENT != "local1"` to switch to production database

### 4. Deployment Scripts
Created comprehensive deployment and verification scripts:

#### `backend/migrate_production.py`
- Runs database migrations for production
- Sets environment to production
- Uses alembic to upgrade database schema

#### `backend/verify_production_schema.py`
- Verifies all expected tables exist
- Checks table structures match model definitions
- Tests database connectivity

#### `backend/populate_production_data.py`
- Populates initial room data
- Creates sample rooms (Standard, Private, ICU)
- Sets appropriate daily rates

#### `backend/deploy_to_production.py`
- Master deployment script
- Runs all steps in sequence
- Provides comprehensive error handling

#### `backend/deploy-production.bat`
- Windows batch file for easy deployment
- Sets environment variables
- Runs the deployment script

## How to Deploy

### Option 1: Using the Batch File (Windows)
```bash
cd backend
deploy-production.bat
```

### Option 2: Using Python Script
```bash
cd backend
set ENVIRONMENT=production
python deploy_to_production.py
```

### Option 3: Manual Steps
```bash
cd backend
set ENVIRONMENT=production
python migrate_production.py
python verify_production_schema.py
python populate_production_data.py
```

## Database Schema

### Tables Created/Updated
1. **room** - Patient rooms with types and status
2. **admission** - Patient admission/discharge records
3. **etl_process_status** - ETL process tracking
4. **Existing tables** - staff, patients, invoices, payments, audit_logs

### Room Types
- **STANDARD**: $150/day
- **PRIVATE**: $250/day  
- **ICU**: $500/day

### Room Status
- **AVAILABLE**: Ready for admission
- **OCCUPIED**: Currently occupied
- **MAINTENANCE**: Under maintenance

## Verification

After deployment, verify:
1. All tables exist in production database
2. Room data is populated
3. API endpoints work correctly
4. Frontend can connect to production API

## Troubleshooting

### Common Issues
1. **Missing dependencies**: Ensure all packages are installed
2. **Database connection**: Check Neon database credentials
3. **Migration conflicts**: Check alembic version history
4. **Model mismatches**: Verify all models are imported correctly

### Logs
Check the console output for detailed error messages and success confirmations.

## Next Steps

1. Run the deployment script
2. Test the production API
3. Verify frontend connectivity
4. Monitor database performance
5. Set up monitoring and alerts

## Files Modified/Created

### Modified Files
- `backend/app/models/__init__.py`
- `backend/alembic.ini`
- `backend/app/models/admission.py`

### New Files
- `backend/alembic/versions/006_fix_model_inconsistencies.py`
- `backend/migrate_production.py`
- `backend/verify_production_schema.py`
- `backend/populate_production_data.py`
- `backend/deploy_to_production.py`
- `backend/deploy-production.bat`
- `PRODUCTION_DEPLOYMENT_GUIDE.md`
