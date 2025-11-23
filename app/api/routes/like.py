from fastapi import APIRouter, Body
from app.api.utils.deps import SessionDep
from app.api.schemas.likes import LikeBase
from app.api.schemas.posts import PostView
from app.api.services.like import create_like, delete_like, get_user_liked_post

like = APIRouter(prefix="/like", tags=["like"])

@like.post("", response_model=LikeBase, status_code=201)
async def api_create_like(db: SessionDep, like_in: LikeBase = Body(...)):
    """
    좋아요 생성용 API\n
    user_id, post_id body 파라미터 필요
    """
    return await create_like(db=db, user_id=like_in.user_id, post_id=like_in.post_id)

@like.delete("", status_code=204)
async def api_delete_like(db: SessionDep, like_in: LikeBase = Body(...)):
    """
    좋아요 삭제용 API\n
    user_id, post_id body 파라미터 필요
    """
    await delete_like(db=db, user_id=like_in.user_id, post_id=like_in.post_id)

@like.get("/{user_id}", response_model=list[PostView])
async def api_get_user_liked_post(db: SessionDep, user_id: str):
    """
    사용자가 좋아요한 게시물 목록 조회용 API\n
    user_id path 파라미터 필요
    """
    return await get_user_liked_post(db=db, user_id=user_id)