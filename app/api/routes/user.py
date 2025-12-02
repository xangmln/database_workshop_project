from fastapi import APIRouter, Body
from app.api.utils.deps import SessionDep
from app.api.schemas.users import UserProfile, UserOut
from app.api.services.user import get_user_profile, change_user_bio, change_user_email, change_user_name

user = APIRouter(prefix="/user", tags=["user"])

@user.get("/{user_id}/profile", response_model=UserProfile, responses={404: {"description": "사용자를 찾을 수 없습니다."}})
async def get_user_profile_endpoint(db: SessionDep, user_id: str):
    """
    특정 사용자의 프로필 정보 조회 API\n
    user_id path 파라미터 필요\n
    해당 사용자가 없으면 404 에러 반환
    """
    return await get_user_profile(db=db, user_id=user_id)

@user.patch("/{user_id}/bio", response_model=UserOut, responses={404: {"description": "사용자를 찾을 수 없습니다."}})
async def change_user_bio_endpoint(db: SessionDep, user_id: str, new_bio: str = Body(..., embed=True)):
    """
    특정 사용자의 바이오 변경 API\n
    user_id path 파라미터 필요\n
    new_bio 쿼리 파라미터 필요\n
    해당 사용자가 없으면 404 에러 반환
    """
    return await change_user_bio(db=db, user_id=user_id, new_bio=new_bio)

@user.patch("/{user_id}/email", response_model=UserOut, responses={404: {"description": "사용자를 찾을 수 없습니다."}, 409: {"description": "이미 등록된 이메일입니다."}})
async def change_user_email_endpoint(db: SessionDep, user_id: str, new_email: str = Body(..., embed=True)):
    """
    특정 사용자의 이메일 변경 API\n
    user_id path 파라미터 필요\n
    new_email 쿼리 파라미터 필요\n
    해당 사용자가 없으면 404 에러 반환
    """
    return await change_user_email(db=db, user_id=user_id, new_email=new_email)

@user.patch("/{user_id}/name", response_model=UserOut, responses={404: {"description": "사용자를 찾을 수 없습니다."}})
async def change_user_name_endpoint(db: SessionDep, user_id: str, new_name: str = Body(..., embed=True)):
    """
    특정 사용자의 이름 변경 API\n
    user_id path 파라미터 필요\n
    new_name 쿼리 파라미터 필요\n
    해당 사용자가 없으면 404 에러 반환
    """
    return await change_user_name(db=db, user_id=user_id, new_name=new_name)