from pydantic import BaseModel, EmailStr, ConfigDict

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
