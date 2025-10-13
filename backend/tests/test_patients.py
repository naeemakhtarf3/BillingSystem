import pytest
from fastapi.testclient import TestClient
from app.models.staff import Staff, StaffRole
from app.models.patient import Patient
from app.core.security import get_password_hash

def create_test_staff(test_db):
    """Helper function to create test staff."""
    staff = Staff(
        email="test@clinic.com",
        password_hash=get_password_hash("testpassword"),
        name="Test Staff",
        role=StaffRole.BILLING_CLERK
    )
    test_db.add(staff)
    test_db.commit()
    test_db.refresh(staff)
    return staff

def get_auth_token(client, test_db):
    """Helper function to get authentication token."""
    create_test_staff(test_db)
    
    response = client.post("/api/v1/auth/login", data={
        "username": "test@clinic.com",
        "password": "testpassword"
    })
    
    return response.json()["access_token"]

def test_create_patient(client, test_db, sample_patient_data):
    """Test patient creation."""
    token = get_auth_token(client, test_db)
    
    response = client.post(
        "/api/v1/patients",
        json=sample_patient_data,
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == sample_patient_data["name"]
    assert data["email"] == sample_patient_data["email"]
    assert data["phone"] == sample_patient_data["phone"]
    assert "id" in data

def test_create_patient_unauthorized(client, test_db, sample_patient_data):
    """Test patient creation without authentication."""
    response = client.post("/api/v1/patients", json=sample_patient_data)
    
    assert response.status_code == 401

def test_get_patient(client, test_db, sample_patient_data):
    """Test getting a specific patient."""
    token = get_auth_token(client, test_db)
    
    # Create patient first
    create_response = client.post(
        "/api/v1/patients",
        json=sample_patient_data,
        headers={"Authorization": f"Bearer {token}"}
    )
    patient_id = create_response.json()["id"]
    
    # Get patient
    response = client.get(
        f"/api/v1/patients/{patient_id}",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == patient_id
    assert data["name"] == sample_patient_data["name"]

def test_get_patient_not_found(client, test_db):
    """Test getting a non-existent patient."""
    token = get_auth_token(client, test_db)
    
    response = client.get(
        "/api/v1/patients/123e4567-e89b-12d3-a456-426614174000",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 404
    assert "Patient not found" in response.json()["detail"]

def test_search_patients(client, test_db, sample_patient_data):
    """Test patient search functionality."""
    token = get_auth_token(client, test_db)
    
    # Create patient
    client.post(
        "/api/v1/patients",
        json=sample_patient_data,
        headers={"Authorization": f"Bearer {token}"}
    )
    
    # Search by name
    response = client.get(
        "/api/v1/patients?query=John",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["name"] == sample_patient_data["name"]

def test_search_patients_no_results(client, test_db):
    """Test patient search with no results."""
    token = get_auth_token(client, test_db)
    
    response = client.get(
        "/api/v1/patients?query=Nonexistent",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 0

def test_update_patient(client, test_db, sample_patient_data):
    """Test patient update."""
    token = get_auth_token(client, test_db)
    
    # Create patient
    create_response = client.post(
        "/api/v1/patients",
        json=sample_patient_data,
        headers={"Authorization": f"Bearer {token}"}
    )
    patient_id = create_response.json()["id"]
    
    # Update patient
    update_data = {"name": "Jane Doe", "phone": "+1-555-9999"}
    response = client.put(
        f"/api/v1/patients/{patient_id}",
        json=update_data,
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Jane Doe"
    assert data["phone"] == "+1-555-9999"
    assert data["email"] == sample_patient_data["email"]  # Should remain unchanged
