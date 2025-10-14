# Clinic Billing System - Render.com Deployment Guide

## 🚀 Deployment Steps

### 1. Prepare Your Repository
- Ensure all files are committed to your Git repository
- Push your code to GitHub/GitLab

### 2. Create Render.com Account
- Go to [render.com](https://render.com)
- Sign up with your GitHub/GitLab account

### 3. Deploy Backend Service

#### Option A: Using render.yaml (Recommended)
1. Connect your repository to Render
2. Render will automatically detect the `render.yaml` file
3. The service will be configured automatically

#### Option B: Manual Configuration
1. Go to Render Dashboard
2. Click "New" → "Web Service"
3. Connect your repository
4. Configure the service:
   - **Build Command**: `pip install -r backend/requirements.txt && cd backend && alembic upgrade head`
   - **Start Command**: `cd backend && python -m uvicorn app.main:app --host 0.0.0.0 --port $PORT`
   - **Environment**: Python 3

### 4. Set Environment Variables
In your Render dashboard, add these environment variables:

#### Required Variables:
```
DATABASE_URL=postgresql://user:password@host:port/database
JWT_SECRET_KEY=your-super-secret-jwt-key-change-this-in-production
```

#### Optional Variables (set as needed):
```
STRIPE_PUBLISHABLE_KEY=pk_live_your_publishable_key_here
STRIPE_SECRET_KEY=sk_live_your_secret_key_here
STRIPE_WEBHOOK_SECRET=whsec_your_webhook_secret_here
GOOGLE_API_KEY=your_google_api_key_here
SMTP_HOST=sandbox.smtp.mailtrap.io
SMTP_PORT=587
SMTP_USERNAME=your_smtp_username
SMTP_PASSWORD=your_smtp_password
EMAIL_FROM_ADDRESS=no-reply@yourdomain.com
```

### 5. Database Setup
- Render will automatically create a PostgreSQL database
- Database migrations will run during deployment
- Sample data will be created on first deployment

### 6. Deploy Frontend (Optional)
1. Create a new "Static Site" in Render
2. Connect your frontend repository
3. Set build command: `npm install && npm run build`
4. Set publish directory: `dist`
5. Update your frontend API URL to point to your backend URL

## 🔧 Configuration Files Created

### render.yaml
- Defines the web service configuration
- Sets up PostgreSQL database
- Configures environment variables
- Runs database migrations automatically

### backend/requirements.txt
- Updated with production dependencies
- Added `psycopg2-binary` for PostgreSQL
- Added `gunicorn` for production WSGI server

### backend/env.production.example
- Template for production environment variables
- Copy and customize for your deployment

### Procfile
- Alternative deployment method for Heroku-compatible platforms

## 🌐 Post-Deployment

### API Endpoints
- **Base URL**: `https://your-app-name.onrender.com`
- **API Documentation**: `https://your-app-name.onrender.com/docs`
- **Health Check**: `https://your-app-name.onrender.com/api/v1/`

### Default Login Credentials
- **Admin**: `admin@clinic.com` / `admin123`
- **Billing Clerk**: `billing@clinic.com` / `billing123`

### Sample Data
The deployment automatically creates:
- 5 sample patients
- Multiple invoices with various statuses
- Sample payments
- Staff accounts

## 🔍 Troubleshooting

### Common Issues:
1. **Database Connection**: Ensure `DATABASE_URL` is set correctly
2. **CORS Errors**: Update `CORS_ORIGINS` with your frontend domain
3. **Missing Dependencies**: Check that all packages are in `requirements.txt`
4. **Migration Errors**: Ensure database is accessible during build

### Logs
- Check Render dashboard for deployment logs
- Monitor application logs for runtime errors
- Use Render's built-in logging for debugging

## 🔒 Security Notes

1. **Change Default Passwords**: Update admin credentials after deployment
2. **JWT Secret**: Use a strong, unique JWT secret key
3. **Database**: Use Render's managed PostgreSQL for production
4. **HTTPS**: Render provides SSL certificates automatically
5. **Environment Variables**: Never commit sensitive data to repository

## 📊 Monitoring

- Use Render's built-in monitoring
- Set up health checks for your API endpoints
- Monitor database performance
- Track application metrics

## 🔄 Updates

To update your deployment:
1. Push changes to your repository
2. Render will automatically redeploy
3. Database migrations will run automatically
4. No downtime for most updates

## 📞 Support

- Render Documentation: https://render.com/docs
- FastAPI Documentation: https://fastapi.tiangolo.com
- SQLAlchemy Documentation: https://docs.sqlalchemy.org
