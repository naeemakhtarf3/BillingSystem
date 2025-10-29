# Quick Start: Patient Admission and Discharge Workflow

**Feature**: Patient Admission and Discharge Workflow  
**Date**: 2024-12-19  
**Purpose**: Get the feature running quickly for development and testing

## Prerequisites

- Python 3.11+
- Node.js 18+
- PostgreSQL (or SQLite for development)
- Existing Clinic Billing System running

## Backend Setup

### 1. Database Migration

```bash
# Navigate to backend directory
cd backend

# Create and run migration for new tables
alembic revision --autogenerate -m "add rooms and admissions"
alembic upgrade head
```

### 2. Install Dependencies

```bash
# Install Python dependencies (if not already installed)
pip install -r requirements.txt

# Additional dependencies for this feature
pip install websockets  # For real-time updates
```

### 3. Environment Configuration

Add to your `.env` file:
```env
# WebSocket configuration for real-time updates
WEBSOCKET_ENABLED=true
WEBSOCKET_PORT=8001
```

### 4. Start Backend Server

```bash
# Start FastAPI server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Frontend Setup

### 1. Install Dependencies

```bash
# Navigate to frontend directory
cd frontend

# Install additional dependencies
npm install @mui/material @emotion/react @emotion/styled
npm install @mui/icons-material
npm install socket.io-client  # For real-time updates
```

### 2. Environment Configuration

Add to your `.env` file:
```env
# API configuration
VITE_API_BASE_URL=http://localhost:8000/api/v1
VITE_WEBSOCKET_URL=ws://localhost:8001
```

### 3. Start Frontend Server

```bash
# Start development server
npm run dev
```

## Database Setup

### 1. Create Sample Rooms

```python
# Run this script to create sample room data
python -c "
from app.db.session import SessionLocal
from app.models.room import Room

db = SessionLocal()

# Create sample rooms
rooms = [
    Room(room_number='101A', type='standard', status='available', daily_rate_cents=15000),
    Room(room_number='102A', type='standard', status='available', daily_rate_cents=15000),
    Room(room_number='201B', type='private', status='available', daily_rate_cents=25000),
    Room(room_number='202B', type='private', status='available', daily_rate_cents=25000),
    Room(room_number='ICU-1', type='icu', status='available', daily_rate_cents=50000),
    Room(room_number='ICU-2', type='icu', status='available', daily_rate_cents=50000),
]

for room in rooms:
    db.add(room)

db.commit()
db.close()
print('Sample rooms created successfully!')
"
```

## API Testing

### 1. Test Room Endpoints

```bash
# List all rooms
curl -X GET "http://localhost:8000/api/v1/rooms"

# List available rooms only
curl -X GET "http://localhost:8000/api/v1/rooms?status=available"

# List ICU rooms only
curl -X GET "http://localhost:8000/api/v1/rooms?type=icu"
```

### 2. Test Admission Endpoints

```bash
# Admit a patient (replace IDs with actual values)
curl -X POST "http://localhost:8000/api/v1/admissions" \
  -H "Content-Type: application/json" \
  -d '{
    "room_id": 1,
    "patient_id": 1,
    "staff_id": 1,
    "admission_date": "2024-12-19T10:00:00Z"
  }'

# List active admissions
curl -X GET "http://localhost:8000/api/v1/admissions?status=active"

# Discharge a patient
curl -X POST "http://localhost:8000/api/v1/admissions/1/discharge" \
  -H "Content-Type: application/json" \
  -d '{
    "discharge_date": "2024-12-19T18:00:00Z"
  }'
```

## Frontend Testing

### 1. Access the Application

Open your browser and navigate to:
- Frontend: http://localhost:5173
- Backend API docs: http://localhost:8000/docs

### 2. Test Core Workflows

1. **View Available Rooms**
   - Navigate to Rooms page
   - Filter by room type and status
   - Verify real-time updates

2. **Admit a Patient**
   - Select an available room
   - Choose a patient from the system
   - Complete admission form
   - Verify room status changes to occupied

3. **View Active Admissions**
   - Navigate to Admissions page
   - View list of active admissions
   - Verify patient and room information

4. **Discharge a Patient**
   - Select an active admission
   - Confirm discharge details
   - Verify billing calculation
   - Confirm room becomes available

## Real-time Updates Testing

### 1. WebSocket Connection

```javascript
// Test WebSocket connection in browser console
const ws = new WebSocket('ws://localhost:8001');
ws.onopen = () => console.log('Connected to WebSocket');
ws.onmessage = (event) => console.log('Received:', JSON.parse(event.data));
```

### 2. Test Concurrent Operations

1. Open two browser windows
2. In window 1: Start admitting a patient to room 101A
3. In window 2: Try to admit another patient to room 101A
4. Verify second admission fails with appropriate error
5. Verify real-time updates in both windows

## Troubleshooting

### Common Issues

1. **Database Connection Errors**
   ```bash
   # Check database connection
   python -c "from app.db.session import SessionLocal; print('DB connected:', SessionLocal().execute('SELECT 1').scalar())"
   ```

2. **Migration Issues**
   ```bash
   # Reset migrations (development only)
   alembic downgrade base
   alembic upgrade head
   ```

3. **WebSocket Connection Issues**
   ```bash
   # Check if WebSocket port is available
   netstat -an | grep 8001
   ```

4. **Frontend Build Issues**
   ```bash
   # Clear cache and reinstall
   rm -rf node_modules package-lock.json
   npm install
   ```

### Performance Testing

```bash
# Test room availability query performance
time curl -X GET "http://localhost:8000/api/v1/rooms?status=available"

# Test concurrent admission attempts
for i in {1..10}; do
  curl -X POST "http://localhost:8000/api/v1/admissions" \
    -H "Content-Type: application/json" \
    -d '{"room_id": 1, "patient_id": '$i', "staff_id": 1, "admission_date": "2024-12-19T10:00:00Z"}' &
done
wait
```

## Next Steps

1. **Integration Testing**: Test with existing patient and staff data
2. **Performance Optimization**: Monitor query performance with larger datasets
3. **Error Handling**: Test various error scenarios and edge cases
4. **User Acceptance Testing**: Validate workflows with healthcare staff
5. **Production Deployment**: Follow deployment procedures for production environment

## Development Notes

- All financial calculations use cents to avoid floating-point precision issues
- Real-time updates are limited to room availability and admission status
- Concurrency control uses optimistic locking with timestamp validation
- Error messages provide specific guidance for resolution
- All operations are transactional to maintain data consistency
