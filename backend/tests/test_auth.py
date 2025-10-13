import pytest
from fastapi.testclient import TestClient
from app.core.security import get_password_hash
from app.models.staff import Staff, StaffRole

def test_staff_registration(client, test_db, sample_staff_data):
    """Test staff registration endpoint."""
    response = client.post("/api/v1/auth/register", json=sample_staff_data)
    
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == sample_staff_data["email"]
    assert data["name"] == sample_staff_data["name"]
    assert data["role"] == sample_staff_data["role"]
    assert "id" in data
    assert "password_hash" not in data

def test_staff_registration_duplicate_email(client, test_db, sample_staff_data):
    """Test staff registration with duplicate email."""
    # Create first staff
    client.post("/api/v1/auth/register", json=sample_staff_data)
    
    # Try to create second staff with same email
    response = client.post("/api/v1/auth/register", json=sample_staff_data)
    
    assert response.status_code == 400
    assert "Email already registered" in response.json()["detail"]

def test_staff_login(client, test_db, sample_staff_data):
    """Test staff login endpoint."""
    # Register staff first
    client.post("/api/v1/auth/register", json=sample_staff_data)
    
    # Login
    response = client.post("/api/v1/auth/login", data={
        "username": sample_staff_data["email"],
        "password": sample_staff_data["password"]
    })
    
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"

def test_staff_login_invalid_credentials(client, test_db, sample_staff_data):
    """Test staff login with invalid credentials."""
    # Register staff first
    client.post("/api/v1/auth/register", json=sample_staff_data)
    
    # Login with wrong password
    response = client.post("/api/v1/auth/login", data={
        "username": sample_staff_data["email"],
        "password": "wrongpassword"
    })
    
    assert response.status_code == 401
    assert "Incorrect email or password" in response.json()["detail"]

def test_get_current_staff(client, test_db, sample_staff_data):
    """Test getting current staff information."""
    # Register and login
    client.post("/api/v1/auth/register", json=sample_staff_data)
    login_response = client.post("/api/v1/auth/login", data={
        "username": sample_staff_data["email"],
        "password": sample_staff_data["password"]
    })
    
    token = login_response.json()["access_token"]
    
    # Get current staff
    response = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
    
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == sample_staff_data["email"]
    assert data["name"] == sample_staff_data["name"]

def test_get_current_staff_no_token(client, test_db):
    """Test getting current staff without token."""
    response = client.get("/api/v1/auth/me")
    
    assert response.status_code == 401

def test_get_current_staff_invalid_token(client, test_db):
    """Test getting current staff with invalid token."""
    response = client.get("/api/v1/auth/me", headers={"Authorization": "Bearer invalid_token"})
    
    assert response.status_code == 401
