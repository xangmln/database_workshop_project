from fastapi import HTTPException, status

from app.api.models.user import User
from app.api.schemas.users import UserOut

async def get_user_by_id(db, user_id: str) -> UserOut:
    """
    주어진 user_id로 사용자를 조회하는 서비스 함수입니다.
    사용자가 존재하지 않을 경우 404 에러를 발생시킵니다.
    """
    user = db.query(User).filter(User.user_id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="사용자를 찾을 수 없습니다."
        )
    return UserOut.model_validate(user)