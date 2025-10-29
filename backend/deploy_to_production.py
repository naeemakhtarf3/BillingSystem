#!/usr/bin/env python3
"""
Production Deployment Script

This script handles the complete deployment process for production:
1. Runs database migrations
2. Verifies schema
3. Populates initial data
"""

import os
import sys
import subprocess
from pathlib import Path

def run_script(script_name, description):
    """Run a Python script and return success status."""
    print(f"\n{'='*60}")
    print(f"Running: {description}")
    print(f"{'='*60}")
    
    backend_dir = Path(__file__).parent
    script_path = backend_dir / script_name
    
    try:
        result = subprocess.run([
            sys.executable, str(script_path)
        ], cwd=backend_dir, capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"✅ {description} completed successfully!")
            if result.stdout:
                print(result.stdout)
        else:
            print(f"❌ {description} failed!")
            if result.stdout:
                print("STDOUT:", result.stdout)
            if result.stderr:
                print("STDERR:", result.stderr)
            return False
            
    except Exception as e:
        print(f"❌ Error running {script_name}: {e}")
        return False
    
    return True

def main():
    print("🚀 Starting Production Deployment")
    print("=" * 60)
    
    # Set environment to production
    os.environ["ENVIRONMENT"] = "production"
    
    # Step 1: Run database migrations
    if not run_script("migrate_production.py", "Database Migrations"):
        print("\n❌ Deployment failed at migration step!")
        return 1
    
    # Step 2: Verify schema
    if not run_script("verify_production_schema.py", "Schema Verification"):
        print("\n❌ Deployment failed at schema verification step!")
        return 1
    
    # Step 3: Populate initial data
    if not run_script("populate_production_data.py", "Data Population"):
        print("\n❌ Deployment failed at data population step!")
        return 1
    
    print("\n" + "="*60)
    print("🎉 Production deployment completed successfully!")
    print("="*60)
    print("\nNext steps:")
    print("1. Start your production server")
    print("2. Test the API endpoints")
    print("3. Verify the frontend can connect")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
