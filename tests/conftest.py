import os
os.environ["DATABASE_URL"] = "sqlite:///./test_enterprise_api.db"
os.environ["SECRET_KEY"] = "test-secret-key-change-this"
os.environ["SEED_ADMIN"] = "true"
os.environ["ADMIN_EMAIL"] = "admin@example.com"
os.environ["ADMIN_PASSWORD"] = "ChangeMe123!"

import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.db.session import Base, engine


@pytest.fixture()
def client():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    with TestClient(app) as test_client:
        yield test_client
    Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def admin_token(client):
    response = client.post("/api/v1/auth/login",
                           data={"username": "admin@example.com", "password": "ChangeMe123!"})
    assert response.status_code == 200, response.text
    return response.json()["access_token"]
