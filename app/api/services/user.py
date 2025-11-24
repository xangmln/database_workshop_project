from fastapi import HTTPException, status
from sqlalchemy.orm import joinedload
from sqlalchemy import func

from app.api.utils.deps import SessionDep
from app.api.models.user import User
from app.api.models.post import Post
from app.api.models.like import Like
from app.api.models.hashtag import Hashtag
from app.api.schemas.users import UserOut,UserProfile
from app.api.schemas.posts import PostView

async def get_user_by_id(db: SessionDep, user_id: str) -> UserOut:
    """
    주어진 user_id로 사용자를 조회하는 서비스 함수입니다.
    사용자가 존재하지 않을 경우 404 에러를 발생시킵니다.
    """
    user = db.query(User).filter(User.user_id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="사용자를 찾을 수 없습니다."
        )
    return UserOut.model_validate(user)

async def get_user_profile(db: SessionDep, user_id: str) -> UserProfile:
    """
    주어진 user_id로 사용자의 프로필 정보를 조회하는 서비스 함수입니다.
    """
    user = db.query(User).filter(User.user_id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="사용자를 찾을 수 없습니다."
        )
    posts_query = (
        db.query(
            Post,
            func.count(Like.user_id).label('like_count')
        )
        .outerjoin(Like, Post.post_id == Like.post_id)
        .filter(Post.user_id == user_id)
        .options(
            joinedload(Post.author),
            joinedload(Post.post_photos),
            joinedload(Post.post_hashtags).joinedload(Hashtag.tag)
        )
        .group_by(Post.post_id)
        .order_by(Post.created_at.desc())
        .all()
    )
    user_posts = [
        PostView.from_orm_custom(p, like_count) 
        for p, like_count in posts_query
    ]

    return UserProfile(
        user_id=user.user_id,
        name=user.name,
        bio=user.bio,
        user_post=user_posts
    )

async def change_user_bio(db: SessionDep, user_id: str, new_bio: str) -> UserOut:
    """
    주어진 user_id로 사용자의 바이오를 변경하는 서비스 함수입니다.
    """
    user = db.query(User).filter(User.user_id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="사용자를 찾을 수 없습니다."
        )
    user.bio = new_bio
    db.commit()
    db.refresh(user)
    return UserOut.model_validate(user)

async def change_user_name(db: SessionDep, user_id: str, new_name: str) -> UserOut:
    """
    주어진 user_id로 사용자의 이름을 변경하는 서비스 함수입니다.
    """
    user = db.query(User).filter(User.user_id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="사용자를 찾을 수 없습니다."
        )
    user.name = new_name
    db.commit()
    db.refresh(user)
    return UserOut.model_validate(user)

async def change_user_email(db: SessionDep, user_id: str, new_email: str) -> UserOut:
    """
    주어진 user_id로 사용자의 이메일을 변경하는 서비스 함수입니다.
    """
    user = db.query(User).filter(User.user_id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="사용자를 찾을 수 없습니다."
        )
    existing_user = db.query(User).filter(User.email == new_email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="이미 등록된 이메일입니다."
        )
    user.email = new_email
    db.commit()
    db.refresh(user)
    return UserOut.model_validate(user)