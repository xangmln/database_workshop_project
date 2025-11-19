from uuid import uuid4
from typing import List
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.db import Base

class User(Base):
    __tablename__ = "users"

    user_id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    name: Mapped[str] = mapped_column(String(100), index=True, nullable=False)
    email: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(100), nullable=False)
    bio: Mapped[str | None] = mapped_column(String(255), nullable=True)

    posts: Mapped[List["Post"]] = relationship(
        "Post", 
        back_populates="author", 
        cascade="all, delete-orphan"
    )
    user_likes: Mapped[List["Like"]] = relationship(
        "Like", 
        back_populates="user", 
        cascade="all, delete-orphan"
    )
    user_comments: Mapped[List["Comment"]] = relationship(
        "Comment", 
        back_populates="author", 
        cascade="all, delete-orphan"
    )