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

    @classmethod
    def from_orm_custom(cls, post, like_count: int) -> "PostView":
        sorted_photos = sorted(post.post_photos, key=lambda x: x.order)
        image_urls = [photo.img_url for photo in sorted_photos]
        hashtags = [tag for tag in post.post_hashtags]

        return cls(
            image_url=image_urls,
            title=post.title,
            content=post.content,
            user_id=post.user_id,
            hashtag=hashtags,
            name=post.author.name,
            like_count=like_count
        )