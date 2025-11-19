import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

test_user_payload = {
    "email": "test.signup@example.com",
    "password": "a_very_secure_password_123",
    "name": "Test User",
}

def test_signup_success(client: TestClient, db_session: Session):
    response = client.post(
        "/auth/signup",
        json=test_user_payload,
    )
    data = response.json()

    assert response.status_code == 201
    assert data["email"] == test_user_payload["email"]
    assert data["name"] == test_user_payload["name"]
    assert "user_id" in data
    assert "password" not in data

def test_signup_duplicate_email_fails(client: TestClient, db_session: Session):
    client.post("/auth/signup", json=test_user_payload)
    response = client.post("/auth/signup", json=test_user_payload)

    assert response.status_code == 409
    assert response.json()["detail"] == "이미 등록된 이메일입니다."

def test_signup_invalid_email_fails(client: TestClient, db_session: Session):
    invalid_payload = test_user_payload.copy()
    invalid_payload["email"] = "not-a-valid-email"

    response = client.post("/auth/signup", json=invalid_payload)

    assert response.status_code == 422

def test_login_success(client: TestClient, db_session: Session):
    client.post("/auth/signup", json=test_user_payload)

    login_payload = {
        "email": test_user_payload["email"],
        "password": test_user_payload["password"],
    }
    response = client.post("/auth/login", json=login_payload)
    data = response.json()

    assert response.status_code == 200
    assert data["email"] == login_payload["email"]

def test_login_user_not_found_fails(client: TestClient, db_session: Session):
    login_payload = {
        "email": "nonexistent@example.com",
        "password": "some_password",
    }
    response = client.post("/auth/login", json=login_payload)
    
    assert response.status_code == 401
    assert response.json()["detail"] == "등록된 email이 없습니다"

def test_login_wrong_password_fails(client: TestClient, db_session: Session):
    client.post("/auth/signup", json=test_user_payload)

    login_payload = {
        "email": test_user_payload["email"],
        "password": "this_is_a_wrong_password",
    }
    response = client.post("/auth/login", json=login_payload)

    assert response.status_code == 401
    assert response.json()["detail"] == "비밀번호가 일치하지 않습니다"