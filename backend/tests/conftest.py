import pytest
import asyncio
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient
from app.main import app
from app.db.session import get_db, Base
from app.core.config import settings
import os

# Test database URL
TEST_DATABASE_URL = "sqlite:///./test.db"

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="function")
def test_db():
    """Create a test database for each test function."""
    engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    # Create tables
    Base.metadata.create_all(bind=engine)
    
    yield TestingSessionLocal()
    
    # Clean up
    Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def client(test_db):
    """Create a test client with database dependency override."""
    def override_get_db():
        try:
            yield test_db
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(app) as test_client:
        yield test_client
    
    app.dependency_overrides.clear()

@pytest.fixture
def sample_staff_data():
    """Sample staff data for testing."""
    return {
        "email": "test@clinic.com",
        "password": "testpassword123",
        "name": "Test Staff",
        "role": "billing_clerk"
    }

@pytest.fixture
def sample_patient_data():
    """Sample patient data for testing."""
    return {
        "name": "John Doe",
        "email": "john.doe@email.com",
        "phone": "+1-555-0123",
        "dob": "1990-01-01",
        "metadata": {"insurance": "Test Insurance"}
    }

@pytest.fixture
def sample_invoice_data():
    """Sample invoice data for testing."""
    return {
        "patient_id": "123e4567-e89b-12d3-a456-426614174000",
        "currency": "USD",
        "due_date": "2024-12-31",
        "items": [
            {
                "description": "Consultation",
                "quantity": 1,
                "unit_price_cents": 15000,
                "tax_cents": 1200
            }
        ]
    }
