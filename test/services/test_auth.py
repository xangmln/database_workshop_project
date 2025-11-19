import pytest
from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.api.services.auth import create_user, handle_login
from app.api.schemas.users import UserCreate, UserIn

test_user_payload = {
    "email": "test@example.com",
    "password": "password123",
    "name": "Test User",
}

@pytest.mark.asyncio
async def test_create_user_success(db_session: Session):
    user_to_create = UserCreate(**test_user_payload)
    created_user = await create_user(db=db_session, user=user_to_create)

    assert created_user.email == test_user_payload["email"]
    assert created_user.name == test_user_payload["name"]
    assert created_user.user_id is not None

@pytest.mark.asyncio
async def test_create_user_duplicate_email_fails(db_session: Session):
    user_to_create = UserCreate(**test_user_payload)
    await create_user(db=db_session, user=user_to_create)

    with pytest.raises(HTTPException) as exc_info:
        await create_user(db=db_session, user=user_to_create)

    assert exc_info.value.status_code == 409
    assert exc_info.value.detail == "이미 등록된 이메일입니다."

@pytest.mark.asyncio
async def test_login_success(db_session: Session):
    await create_user(db=db_session, user=UserCreate(**test_user_payload))
    
    login_data = UserIn(email=test_user_payload["email"], password=test_user_payload["password"])
    logged_in_user = await handle_login(db=db_session, user_in=login_data)

    assert logged_in_user.email == test_user_payload["email"]

@pytest.mark.asyncio
async def test_login_user_not_found_fails(db_session: Session):
    login_data = UserIn(email="nonexistent@example.com", password="some_password")

    with pytest.raises(HTTPException) as exc_info:
        await handle_login(db=db_session, user_in=login_data)

    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "등록된 email이 없습니다"

@pytest.mark.asyncio
async def test_login_wrong_password_fails(db_session: Session):
    await create_user(db=db_session, user=UserCreate(**test_user_payload))
    
    login_data = UserIn(email=test_user_payload["email"], password="this_is_a_wrong_password")
    
    with pytest.raises(HTTPException) as exc_info:
        await handle_login(db=db_session, user_in=login_data)

    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "비밀번호가 일치하지 않습니다"