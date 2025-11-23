from pydantic import BaseModel, ConfigDict

class CommentIn(BaseModel):
    user_id: str
    post_id: str
    content: str

class CommentOut(CommentIn):
    name: str
    comment_id: str
    
    model_config = ConfigDict(from_attributes=True)

class CommentBase(BaseModel):
    comment_id: str
    user_id: str
    post_id: str
    content: str

    model_config = ConfigDict(from_attributes=True)