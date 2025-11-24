import pytest
from sqlalchemy.orm import Session
from datetime import datetime

from app.api.utils.utils import get_kst_now
from app.api.services.tag import get_posts_by_tag
from app.api.models.user import User
from app.api.models.post import Post
from app.api.models.tag import Tag
from app.api.models.hashtag import Hashtag
from app.api.models.like import Like

@pytest.mark.asyncio
async def test_get_posts_by_tag_success(db_session: Session):
    """성공 케이스: 태그로 게시글 조회 및 좋아요 수 확인"""
    user = User(user_id="tag_srv_user", email="tag_srv@test.com", hashed_password="pw", name="Tagger")
    liker = User(user_id="liker_user", email="liker@test.com", hashed_password="pw", name="Liker")
    db_session.add_all([user, liker])
    db_session.commit()

    tag = Tag(word="fastapi")
    db_session.add(tag)
    db_session.commit()

    post = Post(title="Tag Post", content="Content", user_id=user.user_id, created_at=get_kst_now())
    db_session.add(post)
    db_session.commit()

    hashtag = Hashtag(post_id=post.post_id, tag_id=tag.tag_id)
    like = Like(user_id=liker.user_id, post_id=post.post_id)
    db_session.add_all([hashtag, like])
    db_session.commit()

    result = await get_posts_by_tag(db=db_session, tag_word="fastapi")

    assert result is not None
    assert len(result) == 1
    assert result[0].title == "Tag Post"
    assert result[0].like_count == 1
    
    tags = [t.word for t in result[0].hashtag]
    assert "fastapi" in tags

@pytest.mark.asyncio
async def test_get_posts_by_tag_not_found(db_session: Session):
    """실패 케이스: 해당 태그의 게시글이 없을 때 None 반환"""
    
    result = await get_posts_by_tag(db=db_session, tag_word="nonexistent")

    assert result is None