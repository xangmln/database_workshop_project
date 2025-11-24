import pytest
from sqlalchemy.orm import Session
from fastapi import HTTPException
from datetime import datetime, timedelta

from app.api.utils.utils import get_kst_now
from app.api.services.user import get_user_profile
from app.api.models.user import User
from app.api.models.post import Post
from app.api.models.photo import Photo
from app.api.models.like import Like
from app.api.models.tag import Tag
from app.api.models.hashtag import Hashtag

@pytest.mark.asyncio
async def test_get_user_profile_success(db_session: Session):
    """
    성공 케이스: 유저 정보와 해당 유저가 쓴 게시글(좋아요, 사진, 태그 포함) 조회
    """
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

    ht = Hashtag(post_id=post1.post_id, tag_id=tag.tag_id)
    db_session.add(ht)
    
    db_session.commit()

    result = await get_user_profile(db=db_session, user_id="profile_target")

    assert result.user_id == "profile_target"
    assert result.name == "Profile Target"
    assert result.bio == "Hello World"

    assert len(result.user_post) == 2
    
    assert result.user_post[0].title == "Latest Post"
    assert result.user_post[1].title == "Old Post"

    latest_post_view = result.user_post[0]
    assert latest_post_view.like_count == 1
    assert latest_post_view.image_url[0] == "http://img.com/1.jpg"
    assert latest_post_view.hashtag[0].word == "profile_tag"

@pytest.mark.asyncio
async def test_get_user_profile_no_posts(db_session: Session):
    """
    성공 케이스: 유저는 존재하지만 게시글이 없는 경우
    """
    user = User(user_id="clean_user", email="clean@test.com", hashed_password="pw", name="Clean")
    db_session.add(user)
    db_session.commit()

    result = await get_user_profile(db=db_session, user_id="clean_user")

    assert result.user_id == "clean_user"
    assert result.user_post == []

@pytest.mark.asyncio
async def test_get_user_profile_not_found(db_session: Session):
    """
    실패 케이스: 존재하지 않는 유저 ID 조회 시 404 에러
    """
    with pytest.raises(HTTPException) as exc:
        await get_user_profile(db=db_session, user_id="ghost_user")
    
    assert exc.value.status_code == 404
    assert exc.value.detail == "사용자를 찾을 수 없습니다."