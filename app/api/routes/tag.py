from fastapi import APIRouter, HTTPException, status
from typing import List
from app.api.utils.deps import SessionDep
from app.api.schemas.posts import PostView
from app.api.services.tag import get_posts_by_tag

tag = APIRouter(prefix="/tag", tags=["tag"])

@tag.get("/{tag_word}", response_model=List[PostView], responses={404: {"description": "해당 태그가 포함된 게시글을 찾을 수 없습니다."}})
async def get_posts_by_tag_endpoint(db: SessionDep, tag_word: str):
    """
    특정 태그가 포함된 게시글 조회 API\n
    tag_word path 파라미터 필요\n
    해당 태그가 포함된 게시글이 없으면 404 에러 반환
    """
    posts = await get_posts_by_tag(db=db, tag_word=tag_word)
    
    if posts is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="해당 태그가 포함된 게시글을 찾을 수 없습니다."
        )
        
    return posts