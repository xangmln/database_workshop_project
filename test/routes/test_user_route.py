import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from datetime import datetime

from app.api.models.user import User
from app.api.models.post import Post

def test_get_user_profile_endpoint_success(client: TestClient, db_session: Session):
    user = User(
        user_id="profile_tester",
        email="profile@test.com",
        hashed_password="pw",
        name="Profile Name",
        bio="My Bio"
    )
    db_session.add(user)
    db_session.commit()

    post = Post(
        title="User Post",
        content="Content",
        user_id=user.user_id,
        created_at=datetime.utcnow()
    )
    db_session.add(post)
    db_session.commit()

    response = client.get(f"/user/{user.user_id}/profile")

    assert response.status_code == 200
    data = response.json()
    
    assert data["user_id"] == user.user_id
    assert data["name"] == user.name
    assert data["bio"] == user.bio
    assert len(data["user_post"]) == 1
    assert data["user_post"][0]["title"] == "User Post"

def test_get_user_profile_endpoint_not_found(client: TestClient, db_session: Session):
    response = client.get("/user/unknown_user/profile")

    assert response.status_code == 404
    assert response.json()["detail"] == "사용자를 찾을 수 없습니다."