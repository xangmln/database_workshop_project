from typing import List

from sqlalchemy.orm import joinedload, aliased
from sqlalchemy import func

from app.api.utils.deps import SessionDep
from app.api.models.like import Like
from app.api.models.post import Post
from app.api.schemas.likes import LikeBase
from app.api.schemas.posts import PostView

async def create_like(db: SessionDep, user_id: str, post_id: str) -> LikeBase:
    new_like = Like(
        user_id=user_id,
        post_id=post_id
    )
    db.add(new_like)
    db.commit()
    db.refresh(new_like)

    return LikeBase.model_validate(new_like)

async def delete_like(db: SessionDep, user_id: str, post_id: str) -> None:
    like = db.query(Like).filter(
        Like.user_id == user_id,
        Like.post_id == post_id
    ).first()
    if like:
        db.delete(like)
        db.commit()

async def get_user_liked_post(db: SessionDep, user_id: str) -> List[PostView]:
    MyLike = aliased(Like)

    posts = (
        db.query(
            Post,
            func.count(Like.user_id).label('like_count')
        )
        .outerjoin(Like, Post.post_id == Like.post_id)
        .join(MyLike, Post.post_id == MyLike.post_id)
        .filter(MyLike.user_id == user_id)
        .options(
            joinedload(Post.author),
            joinedload(Post.post_photos),
            joinedload(Post.post_hashtags)
        )
        .group_by(Post.post_id)
        .order_by(Post.created_at.desc())
        .all()
    )

    return[PostView.from_orm_custom(p, like_count) for p, like_count in posts]
