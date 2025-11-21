import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from unittest.mock import patch

from app.api.models.user import User

# 테스트에 사용할 공통 데이터
test_post_data = {
    "title": "Router Test Title",
    "content": "Router Test Content",
    "user_id": "test_router_user" 
}

@pytest.fixture(scope="function")
def setup_user(db_session: Session):
    """게시글 작성을 위해 DB에 유저를 미리 생성하는 Fixture"""
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
    """
    성공 케이스: 
    - 이미지 2장 포함
    - user_id를 Form 데이터로 전송
    """
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

def test_create_post_no_images(client: TestClient, db_session: Session, setup_user):
    """
    성공 케이스: 
    - 이미지가 없는 경우에도 생성되어야 함
    """
    response = client.post(
        "/post/create",
        data=test_post_data
    )

    assert response.status_code == 201
    data = response.json()
    assert data["title"] == test_post_data["title"]
    assert data["image_url"] == []

def test_create_post_user_not_found(client: TestClient, db_session: Session):
    """
    실패 케이스: 
    - 존재하지 않는 user_id 전송 시 404 에러
    """
    
    invalid_data = test_post_data.copy()
    invalid_data["user_id"] = "unknown_user"

    response = client.post(
        "/post/create", 
        data=invalid_data
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "사용자를 찾을 수 없습니다."
def test_create_post_too_many_images(client: TestClient, db_session: Session, setup_user):
    """
    실패 케이스: 
    - 이미지 4장 전송 시 400 에러
    """
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