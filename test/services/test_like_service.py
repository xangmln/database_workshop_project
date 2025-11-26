import pytest
from sqlalchemy.orm import Session

from app.api.utils.utils import get_kst_now
from app.api.services.like import create_like, delete_like, get_user_liked_post
from app.api.models.user import User
from app.api.models.post import Post
from app.api.models.like import Like

@pytest.mark.asyncio
async def test_create_like_success(db_session: Session):
    user = User(
        user_id="like_user",
        email="like@test.com",
        hashed_password="pw",
        name="Liker"
    )
    db_session.add(user)
    db_session.commit()

    post = Post(
        post_id="like_post_id",
        title="Test Post",
        content="Test Content",
        user_id=user.user_id,
        created_at=get_kst_now()
    )
    db_session.add(post)
    db_session.commit()

    result = await create_like(
        db=db_session,
        user_id=user.user_id,
        post_id=post.post_id
    )

    assert result.user_id == user.user_id
    assert result.post_id == post.post_id

    db_like = db_session.query(Like).filter(
        Like.user_id == user.user_id,
        Like.post_id == post.post_id
    ).first()
    
    assert db_like is not None

@pytest.mark.asyncio
async def test_delete_like_success(db_session: Session):
    user = User(
        user_id="del_user", 
        email="del@test.com", 
        hashed_password="pw", 
        name="Deleter"
    )
    db_session.add(user)
    db_session.commit()

    post = Post(
        post_id="del_post_id", 
        title="Test Post", 
        content="Content", 
        user_id=user.user_id, 
        created_at=get_kst_now()
    )
    db_session.add(post)
    db_session.commit()

    like = Like(user_id=user.user_id, post_id=post.post_id)
    db_session.add(like)
    db_session.commit()

    await delete_like(db_session, user.user_id, post.post_id)

    deleted_like = db_session.query(Like).filter(
        Like.user_id == user.user_id, 
        Like.post_id == post.post_id
    ).first()
    
    assert deleted_like is None

@pytest.mark.asyncio
async def test_delete_like_not_found(db_session: Session):
    user = User(
        user_id="ghost_user", 
        email="ghost@test.com", 
        hashed_password="pw", 
        name="Ghost"
    )
    db_session.add(user)
    db_session.commit()

    post = Post(
        post_id="ghost_post_id", 
        title="Ghost Post", 
        content="Content", 
        user_id=user.user_id, 
        created_at=get_kst_now()
    )
    db_session.add(post)
    db_session.commit()

    await delete_like(db_session, user.user_id, post.post_id)

    deleted_like = db_session.query(Like).filter(
        Like.user_id == user.user_id, 
        Like.post_id == post.post_id
    ).first()

    assert deleted_like is None

@pytest.mark.asyncio
async def test_get_user_liked_post_success(db_session: Session):
    liker = User(user_id="liker", email="liker@test.com", hashed_password="pw", name="Liker")
    author = User(user_id="author", email="au@test.com", hashed_password="pw", name="Author")
    db_session.add_all([liker, author])
    db_session.commit()

    post = Post(title="Liked Post", content="C", user_id=author.user_id, created_at=get_kst_now())
    db_session.add(post)
    db_session.commit()

    like = Like(user_id=liker.user_id, post_id=post.post_id)
    db_session.add(like)
    db_session.commit()

    result = await get_user_liked_post(db=db_session, user_id=liker.user_id)

    assert len(result) == 1
    assert result[0].title == "Liked Post"
    assert result[0].like_count == 1
    assert result[0].is_liked is True

@pytest.mark.asyncio
async def test_get_user_liked_post_empty(db_session: Session):
    user = User(user_id="new_user", email="new@test.com", hashed_password="pw", name="New")
    author = User(user_id="author", email="author@test.com", hashed_password="pw", name="Author")
    db_session.add_all([user, author])
    db_session.commit()

    post = Post(title="Post", content="Content", user_id=author.user_id)
    db_session.add(post)
    db_session.commit()

    other_like = Like(user_id=author.user_id, post_id=post.post_id)
    db_session.add(other_like)
    db_session.commit()

    result = await get_user_liked_post(db=db_session, user_id=user.user_id)

    assert result == []