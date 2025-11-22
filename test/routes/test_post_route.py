import pytest
from datetime import datetime, timedelta
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from unittest.mock import patch


from app.api.models.user import User
from app.api.models.post import Post
from app.api.models.photo import Photo
from app.api.models.like import Like
from app.api.utils.utils import get_kst_now

test_post_data = {
    "title": "Router Test Title",
    "content": "Router Test Content",
    "user_id": "test_router_user",
    "tags": ["python", "fastapi"]
}

@pytest.fixture(scope="function")
def setup_user(db_session: Session):
    user = User(
        email="router_test@example.com",
        hashed_password="hashed_pw",
        name="Router Tester",
        user_id=test_post_data["user_id"]
    )
    db_session.add(user)
    db_session.commit()
    return user

def test_create_post_success(client: TestClient, db_session: Session, setup_user):
    with patch("app.api.services.post.upload_img_to_cloudinary") as mock_upload:
        mock_upload.side_effect = ["http://mock.com/1.jpg", "http://mock.com/2.jpg"]

        files = [
            ("images", ("test1.png", b"fake_bytes_1", "image/png")),
            ("images", ("test2.png", b"fake_bytes_2", "image/png"))
        ]

        response = client.post(
            "/post/create",
            data=test_post_data,
            files=files
        )

    assert response.status_code == 201
    data = response.json()
    assert data["title"] == test_post_data["title"]
    assert data["user_id"] == test_post_data["user_id"]
    assert len(data["image_url"]) == 2
    assert data["image_url"][0] == "http://mock.com/1.jpg"
    
    assert "hashtag" in data
    assert len(data["hashtag"]) == 2
    assert data["hashtag"][0]["word"] == "python"
    assert data["hashtag"][1]["word"] == "fastapi"

def test_create_post_too_few_images(client: TestClient, db_session: Session, setup_user):
    response = client.post(
        "/post/create",
        data=test_post_data,
        files=[]
    )

    assert response.status_code == 422 

def test_create_post_too_many_images(client: TestClient, db_session: Session, setup_user):
    files = [
        ("images", (f"test{i}.png", b"data", "image/png")) for i in range(4)
    ]

    response = client.post(
        "/post/create",
        data=test_post_data,
        files=files
    )

    assert response.status_code == 400
    assert "이미지는 최대 3장" in response.json()["detail"]

def test_create_post_user_not_found(client: TestClient, db_session: Session):
    invalid_data = test_post_data.copy()
    invalid_data["user_id"] = "unknown_user"

    files = [
        ("images", ("test1.png", b"fake", "image/png"))
    ]

    response = client.post(
        "/post/create",
        data=invalid_data,
        files=files
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "사용자를 찾을 수 없습니다."

def test_get_all_posts_success(client: TestClient, db_session: Session):
    user = User(
        user_id="api_view_user",
        email="view@example.com",
        hashed_password="pw",
        name="View Tester"
    )
    db_session.add(user)
    db_session.commit()

    post1 = Post(
        title="Old Post",
        content="Content 1",
        user_id=user.user_id,
        created_at=get_kst_now() - timedelta(days=1)
    )
    post2 = Post(
        title="New Post",
        content="Content 2",
        user_id=user.user_id,
        created_at=get_kst_now()
    )
    db_session.add_all([post1, post2])
    db_session.commit()
    db_session.refresh(post1)

    photo = Photo(post_id=post1.post_id, img_url="http://test.com/img.jpg", order=0)
    db_session.add(photo)

    like = Like(user_id=user.user_id, post_id=post1.post_id)
    db_session.add(like)
    db_session.commit()

    response = client.get("/post")

    assert response.status_code == 200
    data = response.json()

    assert len(data) == 2
    assert data[0]["title"] == "New Post"
    assert data[1]["title"] == "Old Post"
    assert data[1]["name"] == "View Tester"
    assert data[1]["like_count"] == 1
    assert len(data[1]["image_url"]) == 1
    assert data[1]["image_url"][0] == "http://test.com/img.jpg"

def test_get_all_posts_empty(client: TestClient, db_session: Session):
    response = client.get("/post")
    
    assert response.status_code == 200
    assert response.json() == []