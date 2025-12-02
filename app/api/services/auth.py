from fastapi import HTTPException, status
import logging

from app.core.security import verify_password, get_password_hash
from app.api.models.user import User
from app.api.utils.deps import SessionDep
from app.api.schemas.users import UserCreate, UserIn, UserOut

logger = logging.getLogger(__name__)

async def create_user(db: SessionDep, user: UserCreate) -> UserOut:
    db_user = db.query(User).filter(User.email == user.email).first()
    if db_user:
        logger.warning(f"User creation failed. Email already registered: {user.email}")
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="이미 등록된 이메일입니다.",
        )
    hashed_password = get_password_hash(user.password)
    db_user = User(
        email=user.email,
        hashed_password=hashed_password,
        name=user.name
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    logger.info(f"User created: {db_user.email}")
    return UserOut.model_validate(db_user)

async def handle_login(db: SessionDep, user_in: UserIn) -> UserOut:
    user = db.query(User).filter(User.email == user_in.email).first()
    if not user:
        logger.warning(f"Login failed for email: {user_in.email}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="등록된 email이 없습니다"
        )
    if not verify_password(user_in.password, user.hashed_password):
        logger.warning(f"Invalid password attempt for email: {user_in.email}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="비밀번호가 일치하지 않습니다"
        )
    logger.info(f"User logged in: {user.email}")
    return UserOut.model_validate(user)

async def change_password(db: SessionDep, user_id: str, old_password: str, new_password: str) -> UserOut:
    user = db.query(User).filter(User.user_id == user_id).first()
    if not user:
        logger.warning(f"Password change failed. User not found: {user_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="사용자를 찾을 수 없습니다."
        )
    if not verify_password(old_password, user.hashed_password):
        logger.warning(f"Password change failed. Incorrect old password for user: {user_id}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="기존 비밀번호가 일치하지 않습니다."
        )
    user.hashed_password = get_password_hash(new_password)
    db.commit()
    db.refresh(user)
    return UserOut.model_validate(user)