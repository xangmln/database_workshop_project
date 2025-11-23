from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field
from app.api.schemas.tags import TagOut

class PostOut(BaseModel):
    image_url: List[str]
    title: str
    content: str
    user_id: str
    hashtag: Optional[List[TagOut]] = None

    model_config = ConfigDict(from_attributes=True)

class PostView(PostOut):
    name: str
    like_count: int = Field(default=0)