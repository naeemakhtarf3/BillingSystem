#!/usr/bin/env python3
"""
Test script to test the active admissions endpoint
"""

import urllib.request
import urllib.error
import json

def test_endpoint():
    """Test the active admissions endpoint"""
    url = "http://localhost:8000/api/v1/admissions/active/list"
    
    try:
        print(f"Testing endpoint: {url}")
        
        # Create request
        req = urllib.request.Request(url)
        req.add_header('Accept', 'application/json')
        
        # Make request
        with urllib.request.urlopen(req) as response:
            status_code = response.getcode()
            content = response.read().decode('utf-8')
            
            print(f"Status Code: {status_code}")
            print(f"Response: {content}")
            
            if status_code == 200:
                # Try to parse JSON
                try:
                    data = json.loads(content)
                    print(f"Parsed JSON: {data}")
                    print(f"Number of admissions: {len(data) if isinstance(data, list) else 'Not a list'}")
                except json.JSONDecodeError as e:
                    print(f"JSON parse error: {e}")
            
            return status_code == 200
            
    except urllib.error.HTTPError as e:
        print(f"HTTP Error: {e.code} - {e.reason}")
        try:
            error_content = e.read().decode('utf-8')
            print(f"Error content: {error_content}")
        except:
            pass
        return False
        
    except urllib.error.URLError as e:
        print(f"URL Error: {e.reason}")
        return False
        
    except Exception as e:
        print(f"Unexpected error: {e}")
        return False

if __name__ == "__main__":
    success = test_endpoint()
    print(f"\nTest {'PASSED' if success else 'FAILED'}")
