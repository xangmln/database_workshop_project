from typing import List
from fastapi import APIRouter, status, File, UploadFile, Form

from app.api.utils.deps import SessionDep
from app.api.services.post import create_new_post
from app.api.schemas.posts import PostOut

post = APIRouter(prefix="/post", tags=["post"])

@post.post("/create", status_code=status.HTTP_201_CREATED, response_model=PostOut)
async def create_post_endpoint(
    db: SessionDep,
    title: str = Form(...),
    content: str = Form(...),
    user_id: str = Form(...),
    images: List[UploadFile] = File(default=[]), 
):
    """
    게시글 생성 API (이미지 최소 1장 최대 3장)\n
    hashtag는 추후 구현 예정 일단 none으로 둠\n
    이미지가 3장 초과 시 400 에러 반환\n
    이미지 파일로 업로그 하면 url로 변환 후 반환 추후에도 url로 반환 할 예정\n 
    프론트에서 받아서 리사이징 및 크기 변환 후 사용해주세요 (url에 엔드포인트 형식으로 수정 가능합니다, 용량이 너무 크면 속도가 많이 느려져서 리사이징 필수입니다!!)
    """
    result = await create_new_post(
        db=db,
        title=title,
        content=content,
        images=images,
        user_id=user_id
    )

    return result