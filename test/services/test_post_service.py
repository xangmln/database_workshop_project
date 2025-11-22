import pytest
from unittest.mock import patch
from fastapi import UploadFile, HTTPException
from sqlalchemy.orm import Session
from io import BytesIO
from datetime import datetime, timedelta

from app.api.services.post import create_new_post, view_post
from app.api.models.user import User
from app.api.models.post import Post
from app.api.models.photo import Photo
from app.api.models.tag import Tag
from app.api.models.hashtag import Hashtag
from app.api.models.like import Like

def create_dummy_file(filename="test.jpg"):
    return UploadFile(filename=filename, file=BytesIO(b"fake_image_content"))

@pytest.mark.asyncio
async def test_create_new_post_with_hashtags(db_session: Session):
    user = User(user_id="tag_user", email="tag@ex.com", hashed_password="pw", name="Tagger")
    db_session.add(user)
    
    existing_tag = Tag(word="existing_tag")
    db_session.add(existing_tag)
    db_session.commit()

    images = [create_dummy_file("img1.jpg")]
    input_hashtags = ["existing_tag", "new_tag"]

    with patch("app.api.services.post.upload_img_to_cloudinary") as mock_upload:
        mock_upload.return_value = "http://url.com/img1.jpg"

        result = await create_new_post(
            db=db_session,
            title="Hashtag Post",
            content="Content",
            images=images,
            user_id="tag_user",
            hashtag=input_hashtags
        )

    assert result.title == "Hashtag Post"
    
    new_tag_in_db = db_session.query(Tag).filter(Tag.word == "new_tag").first()
    assert new_tag_in_db is not None
    
    existing_tags = db_session.query(Tag).filter(Tag.word == "existing_tag").all()
    assert len(existing_tags) == 1

    db_post = db_session.query(Post).filter(Post.title == "Hashtag Post").first()
    
    linked_hashtags = db_session.query(Hashtag).filter(Hashtag.post_id == db_post.post_id).all()
    assert len(linked_hashtags) == 2 

    linked_tag_ids = [h.tag_id for h in linked_hashtags]
    assert existing_tag.tag_id in linked_tag_ids
    assert new_tag_in_db.tag_id in linked_tag_ids


@pytest.mark.asyncio
async def test_create_new_post_no_hashtags(db_session: Session):
    user = User(user_id="no_tag_user", email="no@ex.com", hashed_password="pw", name="NoTag")
    db_session.add(user)
    db_session.commit()

    images = [create_dummy_file()]

    with patch("app.api.services.post.upload_img_to_cloudinary") as mock_upload:
        mock_upload.return_value = "url"

        result = await create_new_post(
            db=db_session,
            title="No Tag Post",
            content="Content",
            images=images,
            user_id="no_tag_user",
            hashtag=None
        )

    assert result.title == "No Tag Post"
    
    db_post = db_session.query(Post).filter(Post.title == "No Tag Post").first()
    count = db_session.query(Hashtag).filter(Hashtag.post_id == db_post.post_id).count()
    assert count == 0


@pytest.mark.asyncio
async def test_create_new_post_too_few_images(db_session: Session):
    user = User(user_id="img_user", email="img@ex.com", hashed_password="pw", name="Img")
    db_session.add(user)
    db_session.commit()

    images = []

    with pytest.raises(HTTPException) as exc_info:
        await create_new_post(
            db=db_session,
            title="Fail Post",
            content="Content",
            images=images,
            user_id="img_user"
        )

    assert exc_info.value.status_code == 400
    assert "이미지는 최소 1장" in exc_info.value.detail


@pytest.mark.asyncio
async def test_create_new_post_too_many_images(db_session: Session):
    user = User(user_id="img_user_2", email="img2@ex.com", hashed_password="pw", name="Img2")
    db_session.add(user)
    db_session.commit()

    images = [create_dummy_file() for _ in range(4)]

    with pytest.raises(HTTPException) as exc_info:
        await create_new_post(
            db=db_session,
            title="Fail Post",
            content="Content",
            images=images,
            user_id="img_user_2"
        )

    assert exc_info.value.status_code == 400
    assert "이미지는 최대 3장" in exc_info.value.detail


@pytest.mark.asyncio
async def test_view_post_success(db_session: Session):
    author = User(
        user_id="author_id",
        email="author@test.com",
        hashed_password="pw",
        name="Kim Author"
    )
    liker = User(
        user_id="liker_id",
        email="liker@test.com",
        hashed_password="pw",
        name="Lee Liker"
    )
    db_session.add_all([author, liker])
    db_session.commit()

    old_post = Post(
        title="Old Post",
        content="Old Content",
        user_id=author.user_id,
        created_at=datetime.utcnow() - timedelta(days=1)
    )
    new_post = Post(
        title="New Post",
        content="New Content",
        user_id=author.user_id,
        created_at=datetime.utcnow()
    )
    db_session.add_all([old_post, new_post])
    db_session.commit()
    
    db_session.refresh(old_post)
    db_session.refresh(new_post)

    photo2 = Photo(post_id=old_post.post_id, img_url="http://img2.com", order=1)
    photo1 = Photo(post_id=old_post.post_id, img_url="http://img1.com", order=0)
    db_session.add_all([photo2, photo1])

    like = Like(user_id=liker.user_id, post_id=old_post.post_id)
    db_session.add(like)
    
    db_session.commit()

    result = await view_post(db=db_session)

    assert len(result) == 2
    assert result[0].title == "New Post"
    assert result[1].title == "Old Post"
    assert result[0].name == "Kim Author"
    assert result[1].like_count == 1
    assert result[0].like_count == 0
    assert len(result[1].image_url) == 2
    assert result[1].image_url[0] == "http://img1.com"
    assert result[1].image_url[1] == "http://img2.com"

@pytest.mark.asyncio
async def test_view_post_empty(db_session: Session):
    result = await view_post(db=db_session)
    assert result == []