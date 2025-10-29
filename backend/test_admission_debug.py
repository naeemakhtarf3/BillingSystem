#!/usr/bin/env python3
"""
Debug script to test admission creation
"""

import requests
import json

def test_admission_creation():
    # Login first
    print("1. Logging in...")
    login_response = requests.post('http://localhost:8000/api/v1/auth/login', 
                                 json={'username': 'admin@clinic.com', 'password': 'admin123'})
    print(f"Login status: {login_response.status_code}")
    
    if login_response.status_code != 200:
        print(f"Login failed: {login_response.text}")
        return
    
    token_data = login_response.json()
    token = token_data['access_token']
    print(f"Got token: {token[:50]}...")
    
    # Test admission creation
    print("\n2. Testing admission creation...")
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    # Try with the data from the user's request
    data = {
        "admission_date": "2025-10-25T10:40:00.000Z",
        "staff_id": 5,
        "room_id": 2,
        "patient_id": 1
    }
    
    print(f"Request data: {json.dumps(data, indent=2)}")
    
    response = requests.post('http://localhost:8000/api/v1/admissions/', 
                           headers=headers, json=data)
    
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text}")
    
    # Try with UUIDs
    print("\n3. Testing with UUIDs...")
    data_uuid = {
        "admission_date": "2024-10-25T10:40:00.000Z",
        "staff_id": "b27aba1fdbbb4adebd775304a8f983cf",
        "room_id": 2,
        "patient_id": "019fa9e904834d5cb3ca8d99cd3116a9"
    }
    
    print(f"Request data: {json.dumps(data_uuid, indent=2)}")
    
    response2 = requests.post('http://localhost:8000/api/v1/admissions/', 
                             headers=headers, json=data_uuid)
    
    print(f"Status: {response2.status_code}")
    print(f"Response: {response2.text}")

if __name__ == "__main__":
    test_admission_creation()
