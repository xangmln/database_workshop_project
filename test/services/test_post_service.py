import pytest
from unittest.mock import patch
from fastapi import UploadFile, HTTPException
from sqlalchemy.orm import Session
from io import BytesIO

from app.api.services.post import create_new_post
from app.api.models.user import User
from app.api.models.post import Post
from app.api.models.photo import Photo

def create_dummy_file(filename="test.jpg"):
    return UploadFile(filename=filename, file=BytesIO(b"fake_image_content"))


@pytest.mark.asyncio
async def test_create_new_post_success(db_session: Session):
    """
    성공 케이스: 
    존재하는 user_id로 요청 시, 
    1. 게시글(Post) 생성
    2. 이미지 업로드(Mock) 및 Photo 생성
    3. PostOut 스키마 반환
    """
    user = User(
        user_id="test_user_id",
        email="test@example.com",
        hashed_password="hashed_pw",
        name="Test User"
    )
    db_session.add(user)
    db_session.commit()

    images = [create_dummy_file("img1.jpg"), create_dummy_file("img2.jpg")]

    with patch("app.api.services.post.upload_img_to_cloudinary") as mock_upload:
        mock_upload.side_effect = ["http://url1.com", "http://url2.com"]

        result = await create_new_post(
            db=db_session,
            title="My New Post",
            content="Hello World",
            images=images,
            user_id="test_user_id"
        )

    assert result.title == "My New Post"
    assert result.user_id == "test_user_id"
    assert len(result.image_url) == 2
    assert result.image_url[0] == "http://url1.com"

    db_post = db_session.query(Post).filter(Post.title == "My New Post").first()
    assert db_post is not None
    assert db_post.user_id == "test_user_id"
    
    db_photos = db_session.query(Photo).filter(Photo.post_id == db_post.post_id).all()
    assert len(db_photos) == 2


@pytest.mark.asyncio
async def test_create_new_post_user_not_found(db_session: Session):
    """
    실패 케이스: 
    존재하지 않는 user_id로 요청 시 404 에러 발생
    (get_user_by_id 함수가 제대로 작동하는지 확인)
    """
    non_existent_user_id = "ghost_user"
    images = [create_dummy_file()]
    with pytest.raises(HTTPException) as exc_info:
        await create_new_post(
            db=db_session,
            title="Fail Post",
            content="Fail Content",
            images=images,
            user_id=non_existent_user_id
        )

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "사용자를 찾을 수 없습니다."


@pytest.mark.asyncio
async def test_create_new_post_too_many_images(db_session: Session):
    """
    실패 케이스:
    이미지가 3장을 초과하면 400 에러 발생
    (유저가 존재하더라도 이미지 개수 검증이 통과해야 함)
    """
    user = User(user_id="valid_user", email="valid@ex.com", hashed_password="pw", name="Valid")
    db_session.add(user)
    db_session.commit()

    images = [create_dummy_file() for _ in range(4)]

    with pytest.raises(HTTPException) as exc_info:
        await create_new_post(
            db=db_session,
            title="Too Many",
            content="Images",
            images=images,
            user_id="valid_user"
        )

    assert exc_info.value.status_code == 400
    assert "이미지는 최대 3장" in exc_info.value.detail