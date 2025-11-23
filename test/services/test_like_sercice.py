import pytest
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from app.api.services.like import create_like, delete_like, get_user_liked_post
from app.api.models.user import User
from app.api.models.post import Post
from app.api.models.like import Like
from app.api.models.photo import Photo

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
        created_at=datetime.utcnow()
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
        created_at=datetime.utcnow()
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
        created_at=datetime.utcnow()
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
    target_user = User(user_id="target_user", email="target@test.com", hashed_password="pw", name="Target")
    other_user = User(user_id="other_user", email="other@test.com", hashed_password="pw", name="Other")
    author = User(user_id="author", email="author@test.com", hashed_password="pw", name="Author")
    db_session.add_all([target_user, other_user, author])
    db_session.commit()

    post_liked_by_both = Post(title="Liked By Both", content="C1", user_id=author.user_id, created_at=datetime.utcnow())
    post_liked_by_target = Post(title="Liked By Target", content="C2", user_id=author.user_id, created_at=datetime.utcnow() - timedelta(hours=1))
    post_liked_by_other = Post(title="Liked By Other", content="C3", user_id=author.user_id, created_at=datetime.utcnow() - timedelta(hours=2))
    post_no_likes = Post(title="No Likes", content="C4", user_id=author.user_id, created_at=datetime.utcnow() - timedelta(hours=3))
    
    db_session.add_all([post_liked_by_both, post_liked_by_target, post_liked_by_other, post_no_likes])
    db_session.commit()
    
    db_session.refresh(post_liked_by_both)
    db_session.refresh(post_liked_by_target)

    photo = Photo(post_id=post_liked_by_both.post_id, img_url="http://img.com", order=0)
    db_session.add(photo)

    l1 = Like(user_id=target_user.user_id, post_id=post_liked_by_both.post_id)
    l2 = Like(user_id=other_user.user_id, post_id=post_liked_by_both.post_id)
    
    l3 = Like(user_id=target_user.user_id, post_id=post_liked_by_target.post_id)
    
    l4 = Like(user_id=other_user.user_id, post_id=post_liked_by_other.post_id)

    db_session.add_all([l1, l2, l3, l4])
    db_session.commit()

    result = await get_user_liked_post(db=db_session, user_id=target_user.user_id)

    assert len(result) == 2
    
    assert result[0].title == "Liked By Both"
    assert result[0].like_count == 2
    assert len(result[0].image_url) == 1
    
    assert result[1].title == "Liked By Target"
    assert result[1].like_count == 1

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