from typing import List, Optional

from pydantic import BaseModel, ConfigDict

class PostOut(BaseModel):
    image_url: List[str]
    title: str
    content: str
    user_id: str
    hashtag: Optional[List[str]] = None

    model_config = ConfigDict(from_attributes=True)
    