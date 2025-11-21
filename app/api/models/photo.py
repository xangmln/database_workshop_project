from uuid import uuid4
from typing import List
from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.db import Base

class Photo(Base):
    __tablename__ = "photos"

    img_url: Mapped[str] = mapped_column(
        String(255),
        primary_key=True,
        default=lambda: str(uuid4())
    )
    post_id: Mapped[str] = mapped_column(
        ForeignKey("posts.post_id"),
        nullable=False
    )
    order: Mapped[int] = mapped_column(
        nullable=False
    )
    
    post = relationship("Post", back_populates="post_photos")