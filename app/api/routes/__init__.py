from fastapi import APIRouter
from .auth import auth
from .post import post
from .comment import comment
from .like import like
from .tag import tag
from .user import user

router = APIRouter()

router.include_router(auth)
router.include_router(post)
router.include_router(comment)
router.include_router(like)
router.include_router(tag)
router.include_router(user)