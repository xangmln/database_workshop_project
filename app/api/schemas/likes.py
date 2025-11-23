from pydantic import BaseModel, ConfigDict

class LikeBase(BaseModel):
    user_id: str
    post_id: str

    model_config = ConfigDict(from_attributes=True)