#!/usr/bin/env python3
"""
Script to test and fix email configuration for production
"""

import os
import smtplib
import ssl
from email.message import EmailMessage
from app.core.config import settings

def test_smtp_connection():
    """Test SMTP connection with current settings"""
    print("=== TESTING SMTP CONNECTION ===")
    
    try:
        # Test connection
        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT, timeout=10) as smtp:
            print(f"✓ Connected to {settings.SMTP_HOST}:{settings.SMTP_PORT}")
            
            # Test STARTTLS
            smtp.starttls()
            print("✓ STARTTLS successful")
            
            # Test authentication
            if settings.SMTP_USERNAME and settings.SMTP_PASSWORD:
                smtp.login(settings.SMTP_USERNAME, settings.SMTP_PASSWORD)
                print("✓ Authentication successful")
            else:
                print("✗ No SMTP credentials provided")
                return False
                
        return True
        
    except Exception as e:
        print(f"✗ SMTP connection failed: {e}")
        return False

def test_send_email():
    """Test sending a real email"""
    print("\n=== TESTING EMAIL SEND ===")
    
    try:
        from app.services.mailer import get_mailer
        mailer = get_mailer()
        
        # Send test email
        test_email = "test@example.com"  # Change this to a real email for testing
        mailer.send_email(
            to=test_email,
            subject="Test Email from Production",
            body="This is a test email from your production server.",
            html_body="<h1>Test Email</h1><p>This is a test email from your production server.</p>"
        )
        
        print(f"✓ Test email sent to {test_email}")
        return True
        
    except Exception as e:
        print(f"✗ Email send failed: {e}")
        return False

def suggest_fixes():
    """Suggest fixes for common email issues"""
    print("\n=== SUGGESTED FIXES ===")
    
    issues = []
    
    if not settings.SMTP_USERNAME:
        issues.append("SMTP_USERNAME not set")
    if not settings.SMTP_PASSWORD:
        issues.append("SMTP_PASSWORD not set")
    if not settings.EMAIL_FROM_ADDRESS:
        issues.append("EMAIL_FROM_ADDRESS not set")
    
    if issues:
        print("Issues found:")
        for issue in issues:
            print(f"  - {issue}")
        
        print("\nTo fix these issues:")
        print("1. Set environment variables on your deployment platform:")
        print("   - SMTP_USERNAME=your_smtp_username")
        print("   - SMTP_PASSWORD=your_smtp_password")
        print("   - EMAIL_FROM_ADDRESS=no-reply@yourdomain.com")
        
        print("\n2. For production, consider using:")
        print("   - Gmail SMTP: smtp.gmail.com:587")
        print("   - SendGrid: Set SENDGRID_API_KEY")
        print("   - AWS SES: Use AWS credentials")
        
        print("\n3. Update your render.yaml or deployment config:")
        print("   - Add SMTP_USERNAME and SMTP_PASSWORD to envVars")
        print("   - Set sync: false for sensitive credentials")
    else:
        print("✓ All required email settings are configured")

if __name__ == "__main__":
    print("Email Configuration Debug Tool")
    print("=" * 40)
    
    # Test SMTP connection
    smtp_ok = test_smtp_connection()
    
    # Test email sending (only if SMTP is OK)
    if smtp_ok:
        test_send_email()
    
    # Suggest fixes
    suggest_fixes()
