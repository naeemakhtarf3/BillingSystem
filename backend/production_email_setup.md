# Production Email Setup Guide

## Current Issue
Email works locally but fails on live server. This is typically due to:
1. Missing environment variables on production
2. SMTP credentials not configured
3. Network/firewall restrictions
4. SSL/TLS certificate issues

## Quick Fixes

### 1. Check Environment Variables on Render.com
Go to your Render dashboard → Service → Environment tab and ensure these are set:

```
MAIL_PROVIDER=smtp
SMTP_HOST=sandbox.smtp.mailtrap.io
SMTP_PORT=587
SMTP_USERNAME=your_mailtrap_username
SMTP_PASSWORD=your_mailtrap_password
EMAIL_FROM_ADDRESS=no-reply@yourdomain.com
```

### 2. Update render.yaml
Add the missing environment variables to your render.yaml:

```yaml
envVars:
  - key: SMTP_USERNAME
    value: your_mailtrap_username
  - key: SMTP_PASSWORD
    value: your_mailtrap_password
```

### 3. Test Email Configuration
Run the debug script on your live server:
```bash
python debug_email_config.py
```

## Production Email Service Options

### Option 1: Gmail SMTP (Recommended for small scale)
```yaml
envVars:
  - key: SMTP_HOST
    value: smtp.gmail.com
  - key: SMTP_PORT
    value: 587
  - key: SMTP_USERNAME
    value: your-gmail@gmail.com
  - key: SMTP_PASSWORD
    value: your-app-password
```

### Option 2: SendGrid (Recommended for production)
```yaml
envVars:
  - key: MAIL_PROVIDER
    value: sendgrid
  - key: SENDGRID_API_KEY
    value: your_sendgrid_api_key
  - key: EMAIL_FROM_ADDRESS
    value: no-reply@yourdomain.com
```

### Option 3: AWS SES (For high volume)
```yaml
envVars:
  - key: SMTP_HOST
    value: email-smtp.us-east-1.amazonaws.com
  - key: SMTP_PORT
    value: 587
  - key: SMTP_USERNAME
    value: your_aws_ses_username
  - key: SMTP_PASSWORD
    value: your_aws_ses_password
```

## Debugging Steps

1. **Check logs** on your live server for email errors
2. **Run debug script** to verify configuration
3. **Test SMTP connection** manually
4. **Check firewall** settings on your deployment platform
5. **Verify credentials** are correct

## Common Issues & Solutions

### Issue: "Authentication failed"
- **Solution**: Check SMTP_USERNAME and SMTP_PASSWORD are correct
- **Gmail**: Use App Password, not regular password

### Issue: "Connection timeout"
- **Solution**: Check if your deployment platform allows outbound SMTP
- **Alternative**: Use SendGrid API instead of SMTP

### Issue: "SSL certificate verify failed"
- **Solution**: The code already handles this with enhanced SSL error handling

### Issue: "Mailtrap sandbox only"
- **Solution**: Mailtrap sandbox is for testing only. Use production SMTP for live emails

## Testing

Run the test script to verify email configuration:
```bash
python fix_email_production.py
```

This will:
1. Test SMTP connection
2. Test email sending
3. Suggest fixes for any issues found
