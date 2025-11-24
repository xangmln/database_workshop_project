import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from datetime import datetime

from app.api.utils.utils import get_kst_now
from app.api.models.user import User
from app.api.models.post import Post
from app.api.models.tag import Tag
from app.api.models.hashtag import Hashtag

def test_get_posts_by_tag_endpoint_success(client: TestClient, db_session: Session):
    """성공 케이스: 200 OK 및 데이터 반환"""
    user = User(user_id="r_tag_user", email="rt@test.com", hashed_password="pw", name="Router")
    db_session.add(user)
    
    tag = Tag(word="python")
    db_session.add(tag)
    db_session.commit()

    post = Post(title="Python Post", content="C", user_id=user.user_id, created_at=get_kst_now())
    db_session.add(post)
    db_session.commit()

    hashtag = Hashtag(post_id=post.post_id, tag_id=tag.tag_id)
    db_session.add(hashtag)
    db_session.commit()

    response = client.get("/tag/python")

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["title"] == "Python Post"

def test_get_posts_by_tag_endpoint_not_found(client: TestClient, db_session: Session):
    """실패 케이스: 게시글이 없을 경우 404 Not Found 반환"""
    response = client.get("/tag/unknown_tag")

    assert response.status_code == 404
    assert response.json()["detail"] == "해당 태그가 포함된 게시글을 찾을 수 없습니다."