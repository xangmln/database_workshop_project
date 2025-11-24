from typing import List
from sqlalchemy.orm import joinedload
from sqlalchemy import func

from app.api.utils.deps import SessionDep
from app.api.models.tag import Tag
from app.api.models.hashtag import Hashtag
from app.api.models.like import Like
from app.api.models.post import Post
from app.api.schemas.tags import TagOut
from app.api.schemas.posts import PostView

async def get_tag_by_word(db: SessionDep, word: str) -> TagOut:
    tag = db.query(Tag).filter(Tag.word == word).first()
    if tag:
        return TagOut.model_validate(tag)
    else:
        new_tag = Tag(word=word)
        db.add(new_tag)
        db.flush()
        return TagOut.model_validate(new_tag)
    
async def get_posts_by_tag(db: SessionDep, tag_word: str) -> List[PostView]|None:
    posts = (
        db.query(
            Post,
            func.count(Like.user_id).label('like_count')
        )
        .join(Hashtag, Post.post_id == Hashtag.post_id)
        .join(Tag, Hashtag.tag_id == Tag.tag_id)
        .outerjoin(Like, Post.post_id == Like.post_id)
        .filter(Tag.word == tag_word)
        .options(
            joinedload(Post.author),
            joinedload(Post.post_photos),
            joinedload(Post.post_hashtags).joinedload(Hashtag.tag)
        )
        .group_by(Post.post_id)
        .order_by(Post.created_at.desc())
        .all()
    )
    if not posts:
        return None
        
    return [PostView.from_orm_custom(p, like_count) for p, like_count in posts]