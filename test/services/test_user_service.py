import pytest
from sqlalchemy.orm import Session
from fastapi import HTTPException
from datetime import datetime, timedelta

from app.api.utils.utils import get_kst_now
from app.api.services.user import get_user_profile, change_user_bio, change_user_name, change_user_email
from app.api.models.user import User
from app.api.models.post import Post
from app.api.models.photo import Photo
from app.api.models.like import Like
from app.api.models.tag import Tag
from app.api.models.hashtag import Hashtag

@pytest.mark.asyncio
async def test_get_user_profile_success(db_session: Session):
    target_user = User(user_id="profile_target", email="p@test.com", hashed_password="pw", name="Profile Target", bio="Hello World")
    liker = User(user_id="liker", email="l@test.com", hashed_password="pw", name="Liker")
    db_session.add_all([target_user, liker])
    db_session.commit()

    tag = Tag(word="profile_tag")
    db_session.add(tag)
    db_session.commit()

    post1 = Post(title="Latest Post", content="C1", user_id=target_user.user_id, created_at=get_kst_now())
    post2 = Post(title="Old Post", content="C2", user_id=target_user.user_id, created_at=get_kst_now() - timedelta(days=1))
    db_session.add_all([post1, post2])
    db_session.commit()
    db_session.refresh(post1)
    db_session.refresh(post2)

    photo = Photo(post_id=post1.post_id, img_url="http://img.com/1.jpg", order=0)
    db_session.add(photo)
    
    like = Like(user_id=liker.user_id, post_id=post1.post_id)
    db_session.add(like)

    self_like = Like(user_id=target_user.user_id, post_id=post1.post_id)
    db_session.add(self_like)

    ht = Hashtag(post_id=post1.post_id, tag_id=tag.tag_id)
    db_session.add(ht)
    
    db_session.commit()

    result = await get_user_profile(db=db_session, user_id="profile_target")

    assert result.user_id == "profile_target"
    assert result.name == "Profile Target"
    assert result.bio == "Hello World"

    assert len(result.user_post) == 2
    
    latest_post_view = result.user_post[0]
    assert latest_post_view.title == "Latest Post"
    assert latest_post_view.like_count == 2
    assert latest_post_view.is_liked is True
    assert latest_post_view.image_url[0] == "http://img.com/1.jpg"
    assert latest_post_view.hashtag[0].word == "profile_tag"

    old_post_view = result.user_post[1]
    assert old_post_view.title == "Old Post"
    assert old_post_view.like_count == 0
    assert old_post_view.is_liked is False

@pytest.mark.asyncio
async def test_get_user_profile_no_posts(db_session: Session):
    user = User(user_id="clean_user", email="clean@test.com", hashed_password="pw", name="Clean")
    db_session.add(user)
    db_session.commit()

    result = await get_user_profile(db=db_session, user_id="clean_user")

    assert result.user_id == "clean_user"
    assert result.user_post == []

@pytest.mark.asyncio
async def test_get_user_profile_not_found(db_session: Session):
    with pytest.raises(HTTPException) as exc:
        await get_user_profile(db=db_session, user_id="ghost_user")
    
    assert exc.value.status_code == 404
    assert exc.value.detail == "사용자를 찾을 수 없습니다."

@pytest.mark.asyncio
async def test_change_user_bio_success(db_session: Session):
    user = User(
        user_id="bio_user", 
        email="bio@test.com", 
        hashed_password="pw", 
        name="Bio User", 
        bio="Old Bio"
    )
    db_session.add(user)
    db_session.commit()

    result = await change_user_bio(db_session, user.user_id, "New Bio")

    assert result.bio == "New Bio"
    
    db_user = db_session.query(User).filter(User.user_id == user.user_id).first()
    assert db_user.bio == "New Bio"

@pytest.mark.asyncio
async def test_change_user_bio_not_found(db_session: Session):
    with pytest.raises(HTTPException) as exc:
        await change_user_bio(db_session, "unknown_user", "New Bio")
    
    assert exc.value.status_code == 404
    assert exc.value.detail == "사용자를 찾을 수 없습니다."

@pytest.mark.asyncio
async def test_change_user_name_success(db_session: Session):
    user = User(
        user_id="name_user", 
        email="name@test.com", 
        hashed_password="pw", 
        name="Old Name"
    )
    db_session.add(user)
    db_session.commit()

    result = await change_user_name(db_session, user.user_id, "New Name")

    assert result.name == "New Name"

    db_user = db_session.query(User).filter(User.user_id == user.user_id).first()
    assert db_user.name == "New Name"

@pytest.mark.asyncio
async def test_change_user_name_not_found(db_session: Session):
    with pytest.raises(HTTPException) as exc:
        await change_user_name(db_session, "unknown_user", "New Name")
    
    assert exc.value.status_code == 404


@pytest.mark.asyncio
async def test_change_user_email_success(db_session: Session):
    user = User(user_id="email_u", email="old@test.com", hashed_password="pw", name="EmailUser")
    db_session.add(user)
    db_session.commit()

    result = await change_user_email(db_session, user.user_id, "new@test.com")
    
    assert result.email == "new@test.com"

@pytest.mark.asyncio
async def test_change_user_email_duplicate(db_session: Session):
    user1 = User(user_id="user1", email="exist@test.com", hashed_password="pw", name="User1")
    user2 = User(user_id="user2", email="change@test.com", hashed_password="pw", name="User2")
    db_session.add_all([user1, user2])
    db_session.commit()

    with pytest.raises(HTTPException) as exc:
        await change_user_email(db_session, user2.user_id, "exist@test.com")
    
    assert exc.value.status_code == 409
    assert exc.value.detail == "이미 등록된 이메일입니다."

@pytest.mark.asyncio
async def test_change_user_email_not_found(db_session: Session):
    with pytest.raises(HTTPException) as exc:
        await change_user_email(db_session, "unknown_user", "new@test.com")
    
    assert exc.value.status_code == 404