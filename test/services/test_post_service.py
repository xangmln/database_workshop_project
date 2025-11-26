import pytest
from unittest.mock import patch
from fastapi import UploadFile, HTTPException
from sqlalchemy.orm import Session
from io import BytesIO
from datetime import datetime, timedelta

from app.api.utils.utils import get_kst_now
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
async def test_view_post(db_session: Session):
    viewer = User(user_id="viewer", email="view@test.com", hashed_password="pw", name="Viewer")
    author = User(user_id="author_vp", email="au_vp@test.com", hashed_password="pw", name="Author")
    other_user = User(user_id="other", email="other@test.com", hashed_password="pw", name="Other")
    db_session.add_all([viewer, author, other_user])
    db_session.commit()

    post_liked = Post(title="Liked Post", content="C1", user_id=author.user_id, created_at=datetime.utcnow())
    post_not_liked = Post(title="Not Liked Post", content="C2", user_id=author.user_id, created_at=datetime.utcnow() - timedelta(hours=1))
    db_session.add_all([post_liked, post_not_liked])
    db_session.commit()

    l1 = Like(user_id=viewer.user_id, post_id=post_liked.post_id)
    l2 = Like(user_id=other_user.user_id, post_id=post_liked.post_id)
    l3 = Like(user_id=other_user.user_id, post_id=post_not_liked.post_id)
    db_session.add_all([l1, l2, l3])
    db_session.commit()

    result = await view_post(db=db_session, current_user_id=viewer.user_id)

    assert len(result) == 2
    
    assert result[0].title == "Liked Post"
    assert result[0].like_count == 2
    assert result[0].is_liked is True

    assert result[1].title == "Not Liked Post"
    assert result[1].like_count == 1
    assert result[1].is_liked is False

@pytest.mark.asyncio
async def test_view_post_empty(db_session: Session, current_user_id="empty_user"):
    result = await view_post(db=db_session, current_user_id=current_user_id)
    assert result == []