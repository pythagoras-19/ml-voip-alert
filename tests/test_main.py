import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.deps import load_model

# Load model before testing
try:
    load_model()
except Exception:
    pass  # Model might not be available in test environment

client = TestClient(app)


def test_root():
    """Test root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    assert "endpoints" in response.json()


def test_health_check():
    """Test health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "model_loaded" in data


def test_score_endpoint_with_model():
    """Test score endpoint with loaded model"""
    # Only run if model is loaded
    try:
        from app.deps import get_model
        model = get_model()
        
        sample_data = {
            "patient_ref_token": "test_patient_123",
            "features": {
                "age": 65,
                "sex": 1,
                "cp": 3,
                "trestbps": 145,
                "chol": 233,
                "fbs": 1,
                "restecg": 0,
                "thalach": 150,
                "exang": 0,
                "oldpeak": 2.3,
                "slope": 0,
                "ca": 0,
                "thal": 1
            }
        }
        
        response = client.post("/score", json=sample_data)
        assert response.status_code == 200
        data = response.json()
        assert "risk" in data
        assert "top_factors" in data
        assert "alerted" in data
        assert 0 <= data["risk"] <= 1
        
    except RuntimeError:
        pytest.skip("Model not loaded, skipping score test")


def test_case_not_found():
    """Test case endpoint with non-existent token"""
    response = client.get("/case/nonexistent")
    assert response.status_code == 404


