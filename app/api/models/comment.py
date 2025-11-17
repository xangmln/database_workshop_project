from uuid import uuid4
from datetime import datetime
from sqlalchemy import String, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from core.db import Base
from api.utils.utils import get_kst_now


class Comment(Base):
    __tablename__ = "comments"

    comment_id: Mapped[str] = mapped_column(
        String,
        primary_key=True,
        default=lambda: str(uuid4())
    )
    content: Mapped[str] = mapped_column(
        String,
        nullable=False
    )
    user_id: Mapped[str] = mapped_column(
        ForeignKey("users.user_id"),
        nullable=False,
        index=True
    )
    post_id: Mapped[str] = mapped_column(
        ForeignKey("posts.post_id"),
        nullable=False,
        index=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=get_kst_now,
        index=True
    )

    author = relationship("User", back_populates="user_comments")
    post = relationship("Post", back_populates="post_comments")
    
