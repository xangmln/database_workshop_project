import pytest
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from app.api.models.user import User
from app.api.models.post import Post
from app.api.models.comment import Comment
from app.api.schemas.comments import CommentIn

from app.api.services.comment import create_comment, get_comments_by_post

def create_test_user(db: Session, user_id: str = "comment_user") -> User:
    user = User(
        user_id=user_id,
        email=f"{user_id}@example.com",
        hashed_password="pw",
        name="Commenter"
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def create_test_post(db: Session, user: User, post_id: str = "comment_post") -> Post:
    post = Post(
        post_id=post_id,
        title="Test Post",
        content="Content",
        user_id=user.user_id,
        created_at=datetime.utcnow()
    )
    db.add(post)
    db.commit()
    db.refresh(post)
    return post

@pytest.mark.asyncio
async def test_create_comment_success(db_session: Session):
    """
    성공 케이스: 댓글 생성
    - DB에 저장되는지 확인
    - 반환된 스키마에 name, comment_id 등이 포함되는지 확인
    """
    user = create_test_user(db_session, "user_1")
    post = create_test_post(db_session, user, "post_1")

    comment_in = CommentIn(
        user_id=user.user_id,
        post_id=post.post_id,
        content="This is a test comment"
    )

    result = await create_comment(db=db_session, comment_in=comment_in)

    assert result.content == "This is a test comment"
    assert result.user_id == user.user_id
    assert result.post_id == post.post_id
    assert result.comment_id is not None

    db_comment = db_session.query(Comment).filter(Comment.comment_id == result.comment_id).first()
    assert db_comment is not None
    assert db_comment.content == "This is a test comment"


@pytest.mark.asyncio
async def test_get_comments_by_post_success(db_session: Session):
    """
    성공 케이스: 특정 게시글의 댓글 조회
    - 댓글이 작성 시간 순서대로 나오는지 확인
    - 작성자 이름(Author Name)이 잘 매핑되는지 확인
    """
    user = create_test_user(db_session, "user_2")
    post = create_test_post(db_session, user, "post_2")

    comment1 = Comment(
        post_id=post.post_id,
        user_id=user.user_id,
        content="First comment",
        created_at=datetime.utcnow() - timedelta(minutes=5)
    )
    comment2 = Comment(
        post_id=post.post_id,
        user_id=user.user_id,
        content="Second comment",
        created_at=datetime.utcnow()
    )
    db_session.add_all([comment1, comment2])
    db_session.commit()

    result = await get_comments_by_post(db=db_session, post_id=post.post_id)

    assert result is not None
    assert len(result) == 2
    
    assert result[0].content == "First comment"
    assert result[1].content == "Second comment"
    
    assert result[0].name == "Commenter"
    assert result[1].name == "Commenter"


@pytest.mark.asyncio
async def test_get_comments_by_post_empty(db_session: Session):
    """
    성공 케이스: 댓글이 없는 게시글 조회 시 None 반환
    """
    user = create_test_user(db_session, "user_3")
    post = create_test_post(db_session, user, "post_3")

    result = await get_comments_by_post(db=db_session, post_id=post.post_id)

    assert result is None