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
    viewer = User(user_id="viewer", email="view@test.com", hashed_password="pw", name="Viewer")
    author = User(user_id="author", email="auth@test.com", hashed_password="pw", name="Author")
    db_session.add_all([viewer, author])
    db_session.commit()

    tag = Tag(word="fastapi")
    db_session.add(tag)
    db_session.commit()

    post = Post(title="Tag Post", content="Content", user_id=author.user_id, created_at=get_kst_now())
    db_session.add(post)
    db_session.commit()

    hashtag = Hashtag(post_id=post.post_id, tag_id=tag.tag_id)
    like = Like(user_id=viewer.user_id, post_id=post.post_id)
    db_session.add_all([hashtag, like])
    db_session.commit()

    result = await get_posts_by_tag(db=db_session, tag_word="fastapi", current_user_id=viewer.user_id)

    assert result is not None
    assert len(result) == 1
    assert result[0].title == "Tag Post"
    assert result[0].like_count == 1
    assert result[0].is_liked is True
    
    tags = [t.word for t in result[0].hashtag]
    assert "fastapi" in tags

@pytest.mark.asyncio
async def test_get_posts_by_tag_not_found(db_session: Session):
    result = await get_posts_by_tag(db=db_session, tag_word="nonexistent", current_user_id="any_user")

    assert result is None