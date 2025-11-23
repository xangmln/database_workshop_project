from fastapi import APIRouter
from .auth import auth
from .post import post
from .comment import comment
from .like import like

router = APIRouter()

router.include_router(auth)
router.include_router(post)
router.include_router(comment)
router.include_router(like)