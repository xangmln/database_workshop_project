from uuid import uuid4
from typing import List
from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.db import Base

class Hashtag(Base):
    __tablename__ = "hashtags"

    post_id: Mapped[str] = mapped_column(
        ForeignKey("posts.post_id"),
        primary_key=True
    )
    tag_id: Mapped[str] = mapped_column(
        ForeignKey("tags.tag_id"),
        primary_key=True
    )

    post = relationship("Post", back_populates="post_hashtags")
    tag = relationship("Tag", back_populates="tag_posts")