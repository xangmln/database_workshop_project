from uuid import uuid4
from typing import List
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.db import Base

class Tag(Base):
    __tablename__ = "tags"

    tag_id: Mapped[str] = mapped_column(
        String,
        primary_key=True,
        default=lambda: str(uuid4())
    )
    word: Mapped[str] = mapped_column(
        String,
        unique=True,
        index=True,
        nullable=False
    )

    tag_posts: Mapped[List["Hashtag"]] = relationship(
        "Hashtag",
        back_populates="tag",
        cascade="all, delete-orphan"
    )