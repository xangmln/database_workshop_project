from uuid import uuid4
from typing import List
from datetime import datetime
from sqlalchemy import String, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.db import Base
from app.api.utils.utils import get_kst_now

class Post(Base):
    __tablename__ = "posts"

    post_id: Mapped[str] = mapped_column(
        String, 
        primary_key=True, 
        default=lambda: str(uuid4())
    )
    user_id: Mapped[str] = mapped_column(
        ForeignKey("users.user_id"), 
        nullable=False, 
        index=True
    )
    title: Mapped[str] = mapped_column(
        String, 
        index=True, 
        nullable=False
    )
    content: Mapped[str] = mapped_column(
        String, 
        nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        default=get_kst_now,
        index=True
    )

    author = relationship("User", back_populates="posts")

    post_liked: Mapped[List["Like"]] = relationship(
        "Like", 
        back_populates="post", 
        cascade="all, delete-orphan"
    )
    post_comments: Mapped[List["Comment"]] = relationship(
        "Comment", 
        back_populates="post", 
        cascade="all, delete-orphan"
    )
    post_hashtags: Mapped[List["Hashtag"]] = relationship(
        "Hashtag",
        back_populates="post",
        cascade="all, delete-orphan"
    )
    post_photos: Mapped[List["Photo"]] = relationship(
        "Photo", 
        back_populates="post", 
        cascade="all, delete-orphan"
    )