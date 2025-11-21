from sqlalchemy.orm import Session
from fastapi import UploadFile, HTTPException, status
from typing import List

from app.api.models.post import Post
from app.api.models.photo import Photo
from app.api.schemas.posts import PostOut
from app.api.services.user import get_user_by_id
from app.core.image import upload_img_to_cloudinary

async def create_new_post(
    db: Session, 
    title: str, 
    content: str, 
    images: List[UploadFile],
    user_id: str
) -> PostOut:
    
    user = await get_user_by_id(db, user_id)
    if len(images) < 1:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="이미지는 최소 1장 이상 업로드해야 합니다."
        )
    if len(images) > 3:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="이미지는 최대 3장까지만 업로드 가능합니다."
        )
    uploaded_urls = []
    for img in images:
        url = upload_img_to_cloudinary
        uploaded_urls.append(url)

    new_post = Post(
        title=title,
        content=content,
        user_id=user.user_id
    )
    db.add(new_post)
    db.flush()

    
    for index, url in enumerate(uploaded_urls):
        new_photo = Photo(
            post_id=new_post.post_id,
            img_url=url,
            order=index 
        )
        db.add(new_photo)

    db.commit()
    db.refresh(new_post)

    result = PostOut(
        image_url=uploaded_urls,
        title=new_post.title,
        content=new_post.content,
        user_id=new_post.user_id,
        hashtag=None
    )
    return result