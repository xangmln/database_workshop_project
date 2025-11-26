import pytest
from unittest.mock import patch
from fastapi import UploadFile, HTTPException
from sqlalchemy.orm import Session
from io import BytesIO
from datetime import datetime, timedelta

from app.api.utils.utils import get_kst_now
from app.api.services.post import create_new_post, view_post, edit_post, delete_post
from app.api.models.user import User
from app.api.models.post import Post
from app.api.models.photo import Photo
from app.api.models.tag import Tag
from app.api.models.hashtag import Hashtag
from app.api.models.like import Like
from app.api.schemas.posts import PostEdit

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
        created_at=get_kst_now() - timedelta(days=1)
    )
    new_post = Post(
        title="New Post",
        content="New Content",
        user_id=author.user_id,
        created_at=get_kst_now()
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

def create_dummy_file(filename="test.jpg"):
    return UploadFile(filename=filename, file=BytesIO(b"fake_image_content"))

@pytest.mark.asyncio
async def test_edit_post_success(db_session: Session):
    user = User(user_id="edit_user", email="edit@test.com", hashed_password="pw", name="Editor")
    db_session.add(user)
    db_session.commit()

    old_tag = Tag(word="old_tag")
    db_session.add(old_tag)
    db_session.commit()

    post = Post(title="Old Title", content="Old Content", user_id=user.user_id, created_at=get_kst_now())
    db_session.add(post)
    db_session.commit()
    db_session.refresh(post)

    old_photo = Photo(post_id=post.post_id, img_url="http://old.com/img.jpg", order=0)
    db_session.add(old_photo)
    
    old_ht = Hashtag(post_id=post.post_id, tag_id=old_tag.tag_id)
    db_session.add(old_ht)
    db_session.commit()

    new_images = [create_dummy_file("new1.jpg")]
    
    post_edit_data = PostEdit(
        post_id=post.post_id,
        title="New Title",
        content="New Content",
        current_user_id=user.user_id,
        hashtag=["new_tag"]
    )

    with patch("app.api.services.post.upload_img_to_cloudinary") as mock_upload, \
        patch("app.api.services.post.delete_img_from_cloudinary") as mock_delete:
        
        mock_upload.return_value = "http://new.com/img.jpg"

        result = await edit_post(db=db_session, post_edit=post_edit_data, images=new_images)

        mock_delete.assert_called_once_with("http://old.com/img.jpg")
        
        assert result.title == "New Title"
        assert result.content == "New Content"
        assert len(result.image_url) == 1
        assert result.image_url[0] == "http://new.com/img.jpg"
        
        db_photos = db_session.query(Photo).filter(Photo.post_id == post.post_id).all()
        assert len(db_photos) == 1
        assert db_photos[0].img_url == "http://new.com/img.jpg"

        db_tags = db_session.query(Tag).join(Hashtag).filter(Hashtag.post_id == post.post_id).all()
        assert len(db_tags) == 1
        assert db_tags[0].word == "new_tag"

@pytest.mark.asyncio
async def test_edit_post_not_found(db_session: Session):
    post_edit_data = PostEdit(
        post_id="nonexistent_id",
        title="Title",
        content="Content",
        current_user_id="user",
        hashtag=[]
    )
    images = [create_dummy_file()]

    with pytest.raises(HTTPException) as exc:
        await edit_post(db=db_session, post_edit=post_edit_data, images=images)
    
    assert exc.value.status_code == 404
    assert exc.value.detail == "게시글을 찾을 수 없습니다."

@pytest.mark.asyncio
async def test_edit_post_forbidden(db_session: Session):
    owner = User(user_id="owner", email="owner@test.com", hashed_password="pw", name="Owner")
    other = User(user_id="other", email="other@test.com", hashed_password="pw", name="Other")
    db_session.add_all([owner, other])
    db_session.commit()

    post = Post(title="Title", content="Content", user_id=owner.user_id)
    db_session.add(post)
    db_session.commit()

    post_edit_data = PostEdit(
        post_id=post.post_id,
        title="Update",
        content="Update",
        current_user_id=other.user_id, 
        hashtag=[]
    )
    images = [create_dummy_file()]

    with pytest.raises(HTTPException) as exc:
        await edit_post(db=db_session, post_edit=post_edit_data, images=images)

    assert exc.value.status_code == 403
    assert exc.value.detail == "수정 권한이 없습니다."

@pytest.mark.asyncio
async def test_edit_post_image_validation(db_session: Session):
    user = User(user_id="valid_user", email="v@t.com", hashed_password="pw", name="V")
    db_session.add(user)
    db_session.commit()

    post = Post(title="T", content="C", user_id=user.user_id)
    db_session.add(post)
    db_session.commit()

    post_edit_data = PostEdit(
        post_id=post.post_id,
        title="T",
        content="C",
        current_user_id=user.user_id,
        hashtag=[]
    )

    # 0장일 때
    with pytest.raises(HTTPException) as exc_min:
        await edit_post(db=db_session, post_edit=post_edit_data, images=[])
    assert exc_min.value.status_code == 400

    # 4장일 때
    with pytest.raises(HTTPException) as exc_max:
        await edit_post(db=db_session, post_edit=post_edit_data, images=[create_dummy_file() for _ in range(4)])
    assert exc_max.value.status_code == 400

@pytest.mark.asyncio
async def test_delete_post_success(db_session: Session):
    user = User(user_id="del_user", email="del@test.com", hashed_password="pw", name="Deleter")
    db_session.add(user)
    db_session.commit()

    post = Post(title="To Delete", content="Content", user_id=user.user_id)
    db_session.add(post)
    db_session.commit()
    db_session.refresh(post)

    photo = Photo(post_id=post.post_id, img_url="http://del.com/img.jpg", order=0)
    db_session.add(photo)
    db_session.commit()

    with patch("app.api.services.post.delete_img_from_cloudinary") as mock_delete:
        result = await delete_post(db=db_session, post_id=post.post_id, current_user_id=user.user_id)

        assert result is True
        mock_delete.assert_called_once_with("http://del.com/img.jpg")

    deleted_post = db_session.query(Post).filter(Post.post_id == post.post_id).first()
    assert deleted_post is None

@pytest.mark.asyncio
async def test_delete_post_not_found(db_session: Session):
    with pytest.raises(HTTPException) as exc:
        await delete_post(db=db_session, post_id="unknown", current_user_id="user")
    
    assert exc.value.status_code == 404

@pytest.mark.asyncio
async def test_delete_post_forbidden(db_session: Session):
    owner = User(user_id="owner", email="o@t.com", hashed_password="pw", name="O")
    hacker = User(user_id="hacker", email="h@t.com", hashed_password="pw", name="H")
    db_session.add_all([owner, hacker])
    db_session.commit()

    post = Post(title="Secure", content="C", user_id=owner.user_id)
    db_session.add(post)
    db_session.commit()

    with pytest.raises(HTTPException) as exc:
        await delete_post(db=db_session, post_id=post.post_id, current_user_id=hacker.user_id)
    
    assert exc.value.status_code == 403