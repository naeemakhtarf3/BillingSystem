# Clinic Billing System

A modern, secure billing system for clinics with Stripe payment integration, built with FastAPI (Python) backend and React frontend.

## Features

- **Staff Management**: Admin and Billing Clerk roles with JWT authentication
- **Patient Management**: Patient records and invoice creation
- **Invoice System**: Create, issue, and track invoices with line items
- **Payment Processing**: Stripe Checkout Sessions (PCI-compliant)
- **Audit Trail**: Complete audit logging for compliance
- **Responsive UI**: Modern, accessible design for both staff and patients

## Architecture

- **Backend**: Python FastAPI with SQLAlchemy ORM and PostgreSQL
- **Frontend**: React + Vite with Material-UI components
- **Payment**: Stripe Checkout Sessions with webhook handling
- **Database**: PostgreSQL with Alembic migrations
- **Authentication**: JWT tokens with role-based access control

## Prerequisites

- Python 3.8+
- Node.js 16+
- PostgreSQL 12+
- Stripe account (for payment processing)

## Quick Start

### Option 1: Automated Setup (Recommended)

**Windows:**
```bash
# Run the automated setup script
setup.bat
```

**Linux/Mac:**
```bash
# Run the automated setup script
python setup.py
```

### Option 2: Manual Setup

### 1. Database Setup

Create a PostgreSQL database:

```sql
CREATE DATABASE clinic_billing;
CREATE USER clinic_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE clinic_billing TO clinic_user;
```

### 2. Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp env.example .env
# Edit .env with your database and Stripe credentials

# Run database setup script
python scripts/setup_database.py

# Start the backend server
uvicorn app.main:app --reload
```

The backend API will be available at `http://localhost:8000`
API documentation: `http://localhost:8000/docs`

### 3. Frontend Setup

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Start the development server
npm run dev
```

The frontend will be available at `http://localhost:5173`

## Configuration

### Environment Variables

Create a `.env` file in the backend directory:

```env
# Database Configuration
DATABASE_URL=postgresql://clinic_user:your_password@localhost:5432/clinic_billing

# JWT Configuration
JWT_SECRET_KEY=your-super-secret-jwt-key-change-this-in-production
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# Stripe Configuration
STRIPE_PUBLISHABLE_KEY=pk_test_your_stripe_publishable_key
STRIPE_SECRET_KEY=sk_test_your_stripe_secret_key
STRIPE_WEBHOOK_SECRET=whsec_your_webhook_secret

# Application Configuration
APP_NAME=Clinic Billing System
APP_VERSION=1.0.0
DEBUG=True
CORS_ORIGINS=http://localhost:3000,http://localhost:5173
```

### Stripe Setup

1. Create a Stripe account at https://stripe.com
2. Get your test API keys from the Stripe Dashboard
3. Set up a webhook endpoint pointing to `http://your-domain/api/v1/payments/webhooks/stripe`
4. Configure the webhook to listen for `checkout.session.completed` events

## Sample Data

The system includes sample data for development:

**Staff Accounts:**
- Admin: `admin@clinic.com` / `admin123`
- Billing Clerk: `billing@clinic.com` / `billing123`

**Sample Patients and Invoices:**
- 5 sample patients with contact information
- Multiple invoices with various statuses
- Sample payment records

## API Endpoints

### Authentication
- `POST /api/v1/auth/register` - Staff registration
- `POST /api/v1/auth/login` - Staff login
- `POST /api/v1/auth/refresh` - Refresh access token
- `GET /api/v1/auth/me` - Get current staff info

### Patients
- `POST /api/v1/patients` - Create patient
- `GET /api/v1/patients/{id}` - Get patient
- `GET /api/v1/patients?query=` - Search patients
- `PUT /api/v1/patients/{id}` - Update patient

### Invoices
- `POST /api/v1/invoices` - Create invoice
- `GET /api/v1/invoices/{id}` - Get invoice
- `GET /api/v1/invoices` - List invoices with filters
- `POST /api/v1/invoices/{id}/issue` - Issue invoice
- `POST /api/v1/invoices/{id}/cancel` - Cancel invoice

### Payments
- `POST /api/v1/payments/invoices/{id}/create-payment-link` - Create Stripe payment link
- `GET /api/v1/payments/invoices/{id}/payments` - Get invoice payments
- `POST /api/v1/payments/{payment_id}/refund` - Process refund
- `POST /api/v1/payments/webhooks/stripe` - Stripe webhook endpoint

### Audit
- `GET /api/v1/audit` - Get audit logs (admin only)

## Frontend Routes

### Staff Interface
- `/staff/login` - Staff login
- `/staff/dashboard` - Dashboard with KPIs
- `/staff/patients` - Patient management
- `/staff/invoices` - Invoice management
- `/staff/payments` - Payment tracking
- `/staff/audit` - Audit logs (admin only)

### Patient Interface
- `/patient/invoice/{id}` - View invoice and pay
- `/patient/payment/success` - Payment success page
- `/patient/payment/cancelled` - Payment cancelled page

## Development

### Running Tests

```bash
# Backend tests
cd backend
python run_tests.py

# Or run specific test suites
pytest tests/test_auth.py -v
pytest tests/test_patients.py -v
pytest tests/test_invoices.py -v
pytest tests/test_payments.py -v

# Run tests with coverage
pytest tests/ --cov=app --cov-report=html

# Frontend tests (when implemented)
cd frontend
npm test
```

### Database Migrations

```bash
# Create new migration
alembic revision --autogenerate -m "Description of changes"

# Apply migrations
alembic upgrade head

# Rollback migration
alembic downgrade -1
```

## Security Features

- JWT-based authentication with short-lived access tokens
- Role-based access control (Admin, Billing Clerk)
- Stripe webhook signature verification
- Input validation and sanitization
- Audit logging for all critical operations
- No card data stored locally (PCI compliant)

## Deployment

### Production Considerations

1. **Environment Variables**: Use secure secret management
2. **Database**: Use connection pooling and proper indexing
3. **HTTPS**: Enable TLS for all external communication
4. **Monitoring**: Set up logging and error tracking
5. **Backups**: Regular database backups
6. **Updates**: Keep dependencies updated

### Local Production Setup

```bash
# Build frontend
cd frontend
npm run build

# Serve with a production server (e.g., nginx)
# Or use a static file server

# Run backend in production mode
cd backend
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## Support

For issues and questions:
1. Check the API documentation at `/docs`
2. Review the audit logs for error tracking
3. Check Stripe dashboard for payment issues

## License

This project is for educational and development purposes.
