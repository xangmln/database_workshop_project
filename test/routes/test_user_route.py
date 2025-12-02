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

@pytest.fixture(scope="function")
def setup_user_for_update(db_session: Session):
    user = User(
        user_id="update_tester",
        email="original@test.com",
        hashed_password="pw",
        name="Original Name",
        bio="Original Bio"
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user

def test_change_user_bio_endpoint(client: TestClient, db_session: Session, setup_user_for_update):
    new_bio = "Updated Bio Content"
    
    response = client.patch(
        f"/user/{setup_user_for_update.user_id}/bio",
        json={"new_bio": new_bio}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["bio"] == new_bio
    assert data["user_id"] == setup_user_for_update.user_id

def test_change_user_name_endpoint(client: TestClient, db_session: Session, setup_user_for_update):
    new_name = "Updated Name"

    response = client.patch(
        f"/user/{setup_user_for_update.user_id}/name",
        json={"new_name": new_name}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["name"] == new_name

def test_change_user_email_endpoint_success(client: TestClient, db_session: Session, setup_user_for_update):
    new_email = "new_email@test.com"

    response = client.patch(
        f"/user/{setup_user_for_update.user_id}/email",
        json={"new_email": new_email}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["email"] == new_email

def test_change_user_email_endpoint_duplicate(client: TestClient, db_session: Session, setup_user_for_update):
    existing_user = User(
        user_id="existing_user",
        email="duplicate@test.com",
        hashed_password="pw",
        name="Existing"
    )
    db_session.add(existing_user)
    db_session.commit()

    response = client.patch(
        f"/user/{setup_user_for_update.user_id}/email",
        json={"new_email": "duplicate@test.com"}
    )

    assert response.status_code == 409
    assert response.json()["detail"] == "이미 등록된 이메일입니다."