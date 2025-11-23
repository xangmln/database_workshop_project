import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from datetime import datetime

from app.api.models.user import User
from app.api.models.post import Post
from app.api.models.comment import Comment

@pytest.fixture(scope="function")
def setup_data(db_session: Session):
    user = User(
        user_id="comment_tester",
        email="comment@test.com",
        hashed_password="pw",
        name="Commenter Name"
    )
    db_session.add(user)
    db_session.commit()

    post = Post(
        post_id="test_post_id",
        title="Test Title",
        content="Test Content",
        user_id=user.user_id,
        created_at=datetime.utcnow()
    )
    db_session.add(post)
    db_session.commit()
    
    return {"user": user, "post": post}

def test_api_create_comment(client: TestClient, db_session: Session, setup_data):
    payload = {
        "user_id": setup_data["user"].user_id,
        "post_id": setup_data["post"].post_id,
        "content": "This is a new comment"
    }

    response = client.post("/comment/", json=payload)

    assert response.status_code == 201
    data = response.json()
    assert data["content"] == "This is a new comment"
    assert data["user_id"] == setup_data["user"].user_id
    assert data["post_id"] == setup_data["post"].post_id
    assert "comment_id" in data

def test_api_get_comments_by_post(client: TestClient, db_session: Session, setup_data):
    comment1 = Comment(
        user_id=setup_data["user"].user_id,
        post_id=setup_data["post"].post_id,
        content="First comment"
    )
    comment2 = Comment(
        user_id=setup_data["user"].user_id,
        post_id=setup_data["post"].post_id,
        content="Second comment"
    )
    db_session.add_all([comment1, comment2])
    db_session.commit()

    response = client.get(f"/comment/post/{setup_data['post'].post_id}")

    assert response.status_code == 200
    data = response.json()
    
    assert len(data) == 2
    assert data[0]["content"] == "First comment"
    assert data[0]["name"] == "Commenter Name"
    assert data[1]["content"] == "Second comment"

def test_api_get_comments_empty(client: TestClient, db_session: Session, setup_data):
    response = client.get(f"/comment/post/{setup_data['post'].post_id}")

    assert response.status_code == 200
    assert response.json() is None