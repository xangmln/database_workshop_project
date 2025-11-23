from fastapi import APIRouter, Body

from app.api.utils.deps import SessionDep

from app.api.schemas.comments import CommentIn, CommentOut, CommentBase
from app.api.services.comment import create_comment, get_comments_by_post

comment = APIRouter(prefix="/comment", tags=["comment"])

@comment.post("/", response_model=CommentBase, status_code=201)
async def api_create_comment(db: SessionDep, comment_in: CommentIn = Body(...)):
    """
    댓글 생성용 API\n
    user_id, post_id, content body 파라미터 필요
    """
    return await create_comment(db=db, comment_in=comment_in)

@comment.get("/post/{post_id}", response_model=list[CommentOut] | None)
async def api_get_comments_by_post(db: SessionDep, post_id: str):
    """
    특정 게시글의 댓글 조회용 API\n
    post_id path 파라미터 필요
    """
    return await get_comments_by_post(db=db, post_id=post_id)