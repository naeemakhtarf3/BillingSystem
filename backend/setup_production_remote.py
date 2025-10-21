#!/usr/bin/env python3
"""
Remote production database setup script
This script connects to the production database and sets up tables and data
"""

import os
import sys
import requests
import json

def setup_production_database():
    """Setup production database via API"""
    base_url = "https://billingapi-ntlg.onrender.com"
    
    print("🚀 Setting up production database...")
    print("=" * 50)
    
    # Step 1: Check current health
    print("1. Checking current health...")
    try:
        response = requests.get(f"{base_url}/health")
        health = response.json()
        print(f"Current status: {health.get('status')}")
        print(f"Database: {health.get('database')}")
        print(f"Tables found: {health.get('found', 0)}/4")
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return False
    
    # Step 2: Run production setup
    print("\n2. Running production setup...")
    try:
        response = requests.post(f"{base_url}/api/v1/reports/etl/setup")
        result = response.json()
        print(f"Setup result: {result.get('status')}")
        print(f"Message: {result.get('message')}")
        
        if result.get('status') == 'error':
            print(f"❌ Setup failed: {result.get('message')}")
            return False
            
    except Exception as e:
        print(f"❌ Setup request failed: {e}")
        return False
    
    # Step 3: Verify setup
    print("\n3. Verifying setup...")
    try:
        response = requests.get(f"{base_url}/health")
        health = response.json()
        print(f"Final status: {health.get('status')}")
        print(f"Tables found: {health.get('found', 0)}/4")
        print(f"Tables: {health.get('tables', [])}")
        
        if health.get('status') == 'healthy':
            print("✅ Production database setup completed successfully!")
            return True
        else:
            print("⚠️ Setup completed but some issues remain")
            return False
            
    except Exception as e:
        print(f"❌ Verification failed: {e}")
        return False

def main():
    """Main function"""
    if setup_production_database():
        print("\n🎉 Production database is now ready!")
        print("You can now use the reports API endpoints:")
        print("- GET /api/v1/reports/revenue")
        print("- GET /api/v1/reports/outstanding")
        print("- GET /api/v1/reports/outstanding?format=csv")
    else:
        print("\n❌ Production database setup failed!")
        print("Please check the deployment logs for more details.")

if __name__ == "__main__":
    main()
