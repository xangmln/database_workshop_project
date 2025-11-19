from uuid import uuid4
from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.db import Base

class Like(Base):
    __tablename__ = "likes"

    user_id: Mapped[str] = mapped_column(
        ForeignKey("users.user_id"), 
        primary_key=True
    )
    post_id: Mapped[str] = mapped_column(
        ForeignKey("posts.post_id"), 
        primary_key=True
    )

    user = relationship("User", back_populates="user_likes")
    post = relationship("Post", back_populates="post_liked")