from typing import List
from fastapi import APIRouter, status, File, UploadFile, Form, Body

from app.api.utils.deps import SessionDep
from app.api.services.post import create_new_post, view_post, edit_post, delete_post
from app.api.schemas.posts import PostOut, PostView, PostEdit

post = APIRouter(prefix="/post", tags=["post"])

@post.get("", response_model=List[PostView])
async def get_all_posts(db: SessionDep):
    """
    전체 게시글 조회 API
    """
    posts = await view_post(db=db)

    return [PostView.model_validate(post) for post in posts]

@post.post("/create", status_code=status.HTTP_201_CREATED, response_model=PostOut)
async def create_post_endpoint(
    db: SessionDep,
    title: str = Form(...),
    content: str = Form(...),
    user_id: str = Form(...),
    tags: List[str] = Form(...),
    images: List[UploadFile] = File(...)
):
    """
    게시글 생성 API (이미지 최소 1장 최대 3장)\n
    hashtag는 추후 구현 예정 일단 none으로 둠\n
    이미지가 3장 초과 시 400 에러 반환\n
    이미지 파일로 업로드 하면 url로 변환 후 반환 추후에도 url로 반환 할 예정\n 
    프론트에서 받아서 리사이징 및 크기 변환 후 사용해주세요 (url에 엔드포인트 형식으로 수정 가능합니다, 용량이 너무 크면 속도가 많이 느려져서 리사이징 필수입니다!! 자세한 방법 https://squarelab.co/blog/get-started-with-cloudinary/ 참고)
    """
    result = await create_new_post(
        db=db,
        title=title,
        content=content,
        images=images,
        user_id=user_id,
        hashtag=tags
    )

    return result

@post.put("",status_code=status.HTTP_200_OK,response_model=PostOut, responses={400:{"description":"이미지 수가 맞지 않을 때"}, 403:{"description":"유저가 삭제할 권한이 없을 때"}, 404:{"description":"해당 게시물이 없을때"}})
async def edit_post_endpoint(
    db:SessionDep, 
    post_id: str = Form(...),
    title: str = Form(...),
    content: str = Form(...),
    current_user_id: str = Form(...),
    hashtag: List[str] = Form([]), 
    images: List[UploadFile] = File(...)
):
    """
    이거 수정하는거만 보내는게 아니라 바뀌고 난 후의 데이터를 다 보내면 됩니다.
    """
    post_edit = PostEdit(
        post_id=post_id,
        title=title,
        content=content,
        current_user_id=current_user_id,
        hashtag=hashtag
    )
    return await edit_post(db, post_edit, images)

@post.delete("",status_code=status.HTTP_204_NO_CONTENT, responses={403:{"description":"유저가 삭제할 권한이 없을 때"}, 404:{"description":"해당 게시물이 없을때"}})
async def delete_post_endpoint(db:SessionDep, post_id : str = Body(...), current_user_id : str = Body(...)):
    """
    body에 담아서 보내주면 됩니다.
    """
    return await delete_post(db, post_id, current_user_id)