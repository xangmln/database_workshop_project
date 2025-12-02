import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from datetime import datetime

from app.api.utils.utils import get_kst_now
from app.api.models.user import User
from app.api.models.post import Post
from app.api.models.like import Like
from app.api.models.tag import Tag
from app.api.models.hashtag import Hashtag

def test_get_posts_by_tag_with_like_status(client: TestClient, db_session: Session):
    viewer = User(user_id="tag_viewer", email="tv@ex.com", hashed_password="pw", name="TagViewer")
    author = User(user_id="author", email="au@ex.com", hashed_password="pw", name="Author")
    db_session.add_all([viewer, author])
    db_session.commit()

    tag = Tag(word="python")
    db_session.add(tag)
    db_session.commit()

    post = Post(title="Python Post", content="C", user_id=author.user_id, created_at=get_kst_now())
    db_session.add(post)
    db_session.commit()

    hashtag = Hashtag(post_id=post.post_id, tag_id=tag.tag_id)
    db_session.add(hashtag)

    like = Like(user_id=viewer.user_id, post_id=post.post_id)
    db_session.add(like)
    db_session.commit()

    response = client.get(f"/tag/python/{viewer.user_id}")

    assert response.status_code == 200
    data = response.json()
    
    assert len(data) == 1
    assert data[0]["title"] == "Python Post"
    assert data[0]["is_liked"] is True
    assert data[0]["like_count"] == 1
    
    tag_words = [t["word"] for t in data[0]["hashtag"]]
    assert "python" in tag_words

def test_get_posts_by_tag_not_found(client: TestClient, db_session: Session):
    response = client.get("/tag/unknown_tag/any_user_id")

    assert response.status_code == 404
    assert response.json()["detail"] == "해당 태그가 포함된 게시글을 찾을 수 없습니다."