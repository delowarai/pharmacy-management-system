import os
os.environ["DATABASE_URL"] = "sqlite:///./test_pharmacy.db"
from fastapi.testclient import TestClient
from app.main import app

def test_health():
    with TestClient(app) as client:
        assert client.get("/api/health").json()["status"] == "ok"
