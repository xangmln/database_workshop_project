from pydantic import BaseModel, ConfigDict

class TagOut(BaseModel):
    tag_id: str
    word: str

    model_config = ConfigDict(from_attributes=True)

class HashtagOut(BaseModel):
    tag_id: str
    post_id: str

    model_config = ConfigDict(from_attributes=True)
