from app.api.utils.deps import SessionDep

from app.api.models.comment import Comment
from app.api.schemas.comments import CommentIn, CommentOut, CommentBase

async def create_comment(db: SessionDep, comment_in: CommentIn) -> CommentOut:
    new_comment = Comment(
        post_id=comment_in.post_id,
        user_id=comment_in.user_id,
        content=comment_in.content
    )
    db.add(new_comment)
    db.commit()
    db.refresh(new_comment)

    return CommentBase.model_validate(new_comment)

async def get_comments_by_post(db: SessionDep, post_id: str) -> list[CommentOut] | None:
    comments = db.query(Comment).filter(Comment.post_id == post_id).order_by(Comment.created_at).all()
    result = []
    for c in comments:
        comment_out = CommentOut(
            comment_id=c.comment_id,
            post_id=c.post_id,
            user_id=c.user_id,
            content=c.content,
            name = c.author.name
        )
        result.append(comment_out)
    return result if result else None
