from fastapi import APIRouter, Body

from app.api.utils.deps import SessionDep
from app.api.schemas.users import UserCreate, UserIn, UserOut
from app.api.services.auth import create_user, handle_login

auth = APIRouter(prefix="/auth", tags=["auth"])

@auth.post("/signup", response_model=UserOut, status_code=201)
async def signup(db: SessionDep, user: UserCreate = Body(...)):
    """
    사용자 회원가입용 api
    이미 등록된 이메일일 경우 409 에러 반환
    """
    return await create_user(db=db, user=user)

@auth.post("/login", response_model=UserOut)
async def login(db: SessionDep, user_in: UserIn = Body(...)):
    """
    사용자 로그인용 api
    등록된 이메일이 없거나 비밀번호가 일치하지 않을 경우 401 에러 반환
    """
    return await handle_login(db=db, user_in=user_in)