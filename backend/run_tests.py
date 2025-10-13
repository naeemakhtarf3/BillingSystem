#!/usr/bin/env python3
"""
Test runner script for Clinic Billing System
"""

import subprocess
import sys
import os

def run_command(command, description):
    """Run a command and return the result"""
    print(f"\n🧪 {description}")
    print(f"Running: {command}")
    print("-" * 50)
    
    try:
        result = subprocess.run(command, shell=True, check=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed with exit code {e.returncode}")
        return False

def main():
    """Main test runner function"""
    print("🏥 Clinic Billing System - Test Runner")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not os.path.exists("requirements.txt"):
        print("❌ Please run this script from the backend directory")
        sys.exit(1)
    
    # Run tests
    test_commands = [
        ("pytest tests/ -v", "Running all tests"),
        ("pytest tests/test_auth.py -v", "Running authentication tests"),
        ("pytest tests/test_patients.py -v", "Running patient tests"),
        ("pytest tests/test_invoices.py -v", "Running invoice tests"),
        ("pytest tests/test_payments.py -v", "Running payment tests"),
        ("pytest tests/ --cov=app --cov-report=html", "Running tests with coverage"),
    ]
    
    success_count = 0
    total_count = len(test_commands)
    
    for command, description in test_commands:
        if run_command(command, description):
            success_count += 1
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {success_count}/{total_count} test suites passed")
    
    if success_count == total_count:
        print("🎉 All tests passed!")
        return 0
    else:
        print("⚠️  Some tests failed. Please check the output above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
