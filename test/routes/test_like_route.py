import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from datetime import datetime

from app.api.models.user import User
from app.api.models.post import Post
from app.api.models.like import Like

@pytest.fixture(scope="function")
def setup_data(db_session: Session):
    user = User(
        user_id="like_tester",
        email="like_test@example.com",
        hashed_password="pw",
        name="Liker Name"
    )
    db_session.add(user)
    db_session.commit()

    post = Post(
        post_id="test_post_for_like",
        title="Test Post",
        content="Test Content",
        user_id=user.user_id,
        created_at=datetime.utcnow()
    )
    db_session.add(post)
    db_session.commit()
    
    return {"user": user, "post": post}

def test_api_create_like(client: TestClient, db_session: Session, setup_data):
    payload = {
        "user_id": setup_data["user"].user_id,
        "post_id": setup_data["post"].post_id
    }

    response = client.post("/like", json=payload)

    assert response.status_code == 201
    data = response.json()
    assert data["user_id"] == setup_data["user"].user_id
    assert data["post_id"] == setup_data["post"].post_id

    db_like = db_session.query(Like).filter_by(
        user_id=setup_data["user"].user_id,
        post_id=setup_data["post"].post_id
    ).first()
    assert db_like is not None

def test_api_delete_like(client: TestClient, db_session: Session, setup_data):
    like = Like(
        user_id=setup_data["user"].user_id,
        post_id=setup_data["post"].post_id
    )
    db_session.add(like)
    db_session.commit()

    payload = {
        "user_id": setup_data["user"].user_id,
        "post_id": setup_data["post"].post_id
    }

    response = client.request("DELETE", "/like", json=payload)

    assert response.status_code == 204
    
    db_like = db_session.query(Like).filter_by(
        user_id=setup_data["user"].user_id,
        post_id=setup_data["post"].post_id
    ).first()
    assert db_like is None

def test_api_get_user_liked_post(client: TestClient, db_session: Session, setup_data):
    like = Like(
        user_id=setup_data["user"].user_id,
        post_id=setup_data["post"].post_id
    )
    db_session.add(like)
    db_session.commit()

    response = client.get(f"/like/{setup_data['user'].user_id}")

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1