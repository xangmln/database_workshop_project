from fastapi import APIRouter
from typing import List
from app.api.utils.deps import SessionDep
from app.api.schemas.users import UserProfile
from app.api.services.user import get_user_profile

user = APIRouter(prefix="/user", tags=["user"])

@user.get("/{user_id}/profile", response_model=UserProfile, responses={404: {"description": "사용자를 찾을 수 없습니다."}})
async def get_user_profile_endpoint(db: SessionDep, user_id: str):
    """
    특정 사용자의 프로필 정보 조회 API\n
    user_id path 파라미터 필요\n
    해당 사용자가 없으면 404 에러 반환
    """
    return await get_user_profile(db=db, user_id=user_id)