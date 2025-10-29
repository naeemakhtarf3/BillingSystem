#!/usr/bin/env python3
"""
Debug JWT token creation and verification
"""
import jwt
from app.core.config import settings
from app.core.security import create_access_token, verify_token
from datetime import timedelta

def test_jwt():
    print("=== JWT Debug Test ===")
    print(f"Secret Key: {settings.JWT_SECRET_KEY}")
    print(f"Algorithm: {settings.JWT_ALGORITHM}")
    
    # Test 1: Create a token using our function
    print("\n1. Creating token with our function...")
    token = create_access_token(
        {"sub": "test-user-id", "role": "admin"}, 
        timedelta(minutes=30)
    )
    print(f"Created token: {token}")
    
    # Test 2: Verify the token using our function
    print("\n2. Verifying token with our function...")
    result = verify_token(token)
    print(f"Verification result: {result}")
    
    # Test 3: Decode token manually with jwt library
    print("\n3. Decoding token manually...")
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        print(f"Manual decode result: {payload}")
    except Exception as e:
        print(f"Manual decode error: {e}")
    
    # Test 4: Test with a fresh token from login
    print("\n4. Testing with fresh login token...")
    fresh_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJiMjdhYmExZi1kYmJiLTRhZGUtYmQ3Ny01MzA0YThmOTgzY2YiLCJyb2xlIjoiYWRtaW4iLCJleHAiOjE3NjEzMTE1ODN9.vUCpTG-3nQ64b9pRKE_EMsUferqlGex42Wp7HInvGKc"
    print(f"Fresh token: {fresh_token}")
    
    # Verify fresh token
    fresh_result = verify_token(fresh_token)
    print(f"Fresh token verification: {fresh_result}")
    
    # Manual decode fresh token
    try:
        fresh_payload = jwt.decode(fresh_token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        print(f"Fresh token manual decode: {fresh_payload}")
    except Exception as e:
        print(f"Fresh token manual decode error: {e}")

if __name__ == "__main__":
    test_jwt()
