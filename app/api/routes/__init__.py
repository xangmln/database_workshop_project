from fastapi import APIRouter
from .auth import auth
from .post import post

router = APIRouter()

router.include_router(auth)
router.include_router(post)