#!/usr/bin/env python3
"""
Debug script to check email configuration on live server
Run this on your live server to diagnose email issues
"""

import os
import sys
from app.core.config import settings

def debug_email_config():
    print("=== EMAIL CONFIGURATION DEBUG ===")
    print(f"Environment: {settings.ENVIRONMENT}")
    print(f"Mail Provider: {settings.MAIL_PROVIDER}")
    print(f"SMTP Host: {settings.SMTP_HOST}")
    print(f"SMTP Port: {settings.SMTP_PORT}")
    print(f"SMTP Username: {settings.SMTP_USERNAME}")
    print(f"SMTP Password: {'*' * len(settings.SMTP_PASSWORD) if settings.SMTP_PASSWORD else 'NOT SET'}")
    print(f"Email From: {settings.EMAIL_FROM_ADDRESS}")
    print(f"SendGrid API Key: {'*' * len(settings.SENDGRID_API_KEY) if settings.SENDGRID_API_KEY else 'NOT SET'}")
    
    print("\n=== ENVIRONMENT VARIABLES ===")
    email_vars = [
        'MAIL_PROVIDER', 'SMTP_HOST', 'SMTP_PORT', 'SMTP_USERNAME', 
        'SMTP_PASSWORD', 'EMAIL_FROM_ADDRESS', 'SENDGRID_API_KEY'
    ]
    
    for var in email_vars:
        value = os.getenv(var, 'NOT SET')
        if 'PASSWORD' in var or 'KEY' in var:
            value = '*' * len(value) if value != 'NOT SET' else 'NOT SET'
        print(f"{var}: {value}")
    
    print("\n=== MAILER TEST ===")
    try:
        from app.services.mailer import get_mailer
        mailer = get_mailer()
        print(f"Selected Mailer: {type(mailer).__name__}")
        print(f"Is Real Mailer: {mailer.is_real}")
        
        if hasattr(mailer, 'host'):
            print(f"SMTP Host: {mailer.host}")
            print(f"SMTP Port: {mailer.port}")
            print(f"SMTP Username: {mailer.username}")
            
    except Exception as e:
        print(f"Error getting mailer: {e}")

if __name__ == "__main__":
    debug_email_config()
