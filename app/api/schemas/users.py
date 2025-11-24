from typing import List

from pydantic import BaseModel, EmailStr, ConfigDict

from app.api.schemas.posts import PostView

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    name: str | None = None

class UserIn(BaseModel):
    email: EmailStr
    password: str

class UserOut(BaseModel):
    user_id: str
    email: EmailStr
    name: str
    
    model_config = ConfigDict(from_attributes=True)

class UserProfile(BaseModel):
    user_id: str
    name: str
    bio: str | None = None
    user_post : List[PostView] = []

    model_config = ConfigDict(from_attributes=True)