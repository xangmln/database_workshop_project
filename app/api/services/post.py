from fastapi import UploadFile, HTTPException, status
from typing import List
from sqlalchemy.orm import joinedload
from sqlalchemy import func, case


from app.api.models.post import Post
from app.api.models.photo import Photo
from app.api.models.hashtag import Hashtag
from app.api.models.like import Like
from app.api.schemas.posts import PostOut, PostView, PostEdit
from app.api.services.user import get_user_by_id
from app.api.services.tag import get_tag_by_word
from app.core.image import upload_img_to_cloudinary, delete_img_from_cloudinary
from app.api.utils.deps import SessionDep

async def create_new_post(
    db: SessionDep, 
    title: str, 
    content: str, 
    images: List[UploadFile],
    user_id: str,
    hashtag: List[str] | None = None
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
        url = upload_img_to_cloudinary(img)
        uploaded_urls.append(url)

    tag = []
    if hashtag:
        for tag_word in hashtag:
            tag_obj = await get_tag_by_word(db, tag_word)
            tag.append(tag_obj)

    new_post = Post(
        title=title,
        content=content,
        user_id=user.user_id
    )
    db.add(new_post)
    db.flush()

    if tag:
        for tag_obj in tag:
            new_hashtag = Hashtag(
                post_id=new_post.post_id,
                tag_id=tag_obj.tag_id
            )
            db.add(new_hashtag)
    
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
        post_id = new_post.post_id,
        image_url = uploaded_urls,
        title = new_post.title,
        content = new_post.content,
        user_id = new_post.user_id,
        hashtag = tag if tag else None
    )
    return result

async def view_post(
    db: SessionDep,
    current_user_id: str
) -> List[PostView]:
    posts = (
        db.query(
            Post,
            func.count(Like.user_id).label('like_count'),
            func.max(
                case(
                    (Like.user_id == current_user_id, 1), 
                    else_=0
                )
            ).label('is_liked_by_me')
        )
        .outerjoin(Like, Post.post_id == Like.post_id)
        .options(
            joinedload(Post.author),
            joinedload(Post.post_photos),
            joinedload(Post.post_hashtags).joinedload(Hashtag.tag)
        )
        .group_by(Post.post_id)
        .order_by(Post.created_at.desc())
        .all()
    )
    
    return [PostView.from_orm_custom(p, like_count, bool(is_liked_val)) for p, like_count, is_liked_val in posts]

async def edit_post(
    db: SessionDep, 
    post_edit: PostEdit, 
    images: List[UploadFile]
) -> PostOut:
    
    post = db.query(Post).filter(Post.post_id == post_edit.post_id).first()
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="게시글을 찾을 수 없습니다."
        )

    if post.user_id != post_edit.current_user_id:
        raise HTTPException(status_code=403, detail="수정 권한이 없습니다.")

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

    post.title = post_edit.title
    post.content = post_edit.content

    current_photos = db.query(Photo).filter(Photo.post_id == post.post_id).all()
    for photo in current_photos:
        delete_img_from_cloudinary(photo.img_url)

    db.query(Photo).filter(Photo.post_id == post.post_id).delete()
    
    uploaded_urls = []
    for index, img in enumerate(images):
        url = upload_img_to_cloudinary(img)
        uploaded_urls.append(url)
        
        new_photo = Photo(
            post_id=post.post_id,
            img_url=url,
            order=index
        )
        db.add(new_photo)
    
    db.query(Hashtag).filter(Hashtag.post_id == post.post_id).delete()

    tag_objects = []
    if post_edit.hashtag:
        for tag_word in post_edit.hashtag:
            tag_obj = await get_tag_by_word(db, tag_word)
            tag_objects.append(tag_obj)
            
            new_hashtag = Hashtag(
                post_id=post.post_id,
                tag_id=tag_obj.tag_id
            )
            db.add(new_hashtag)

    db.commit()
    db.refresh(post)

    return PostOut(
        post_id=post.post_id,
        image_url=uploaded_urls,
        title=post.title,
        content=post.content,
        user_id=post.user_id,
        hashtag=tag_objects if tag_objects else None
    )

async def delete_post(db: SessionDep, post_id: str, current_user_id: str):
    post = db.query(Post).filter(Post.post_id==post_id).first()
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="조건에 해당하는 게시물을 찾지 못했습니다."
        )
    if post.user_id != current_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="해당 유저는 권한이 없습니다"
        )
    if post.post_photos:
        for photo in post.post_photos:
            delete_img_from_cloudinary(photo.img_url)
    db.delete(post)
    db.commit()

    return True