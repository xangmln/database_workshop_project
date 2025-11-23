from fastapi import APIRouter
from .auth import auth
from .post import post
from .comment import comment

router = APIRouter()

router.include_router(auth)
router.include_router(post)
router.include_router(comment)