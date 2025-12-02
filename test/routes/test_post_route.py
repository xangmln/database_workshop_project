import pytest
from datetime import datetime, timedelta
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from unittest.mock import patch


from app.api.models.user import User
from app.api.models.post import Post
from app.api.models.photo import Photo
from app.api.models.like import Like
from app.api.models.hashtag import Hashtag
from app.api.models.tag import Tag
from app.api.utils.utils import get_kst_now

test_post_data = {
    "title": "Router Test Title",
    "content": "Router Test Content",
    "user_id": "test_router_user",
    "tags": ["python", "fastapi"]
}

@pytest.fixture(scope="function")
def setup_user(db_session: Session):
    user = User(
        email="router_test@example.com",
        hashed_password="hashed_pw",
        name="Router Tester",
        user_id=test_post_data["user_id"]
    )
    db_session.add(user)
    db_session.commit()
    return user

def test_create_post_success(client: TestClient, db_session: Session, setup_user):
    with patch("app.api.services.post.upload_img_to_cloudinary") as mock_upload:
        mock_upload.side_effect = ["http://mock.com/1.jpg", "http://mock.com/2.jpg"]

        files = [
            ("images", ("test1.png", b"fake_bytes_1", "image/png")),
            ("images", ("test2.png", b"fake_bytes_2", "image/png"))
        ]

        response = client.post(
            "/post/create",
            data=test_post_data,
            files=files
        )

    assert response.status_code == 201
    data = response.json()
    assert data["title"] == test_post_data["title"]
    assert data["user_id"] == test_post_data["user_id"]
    assert len(data["image_url"]) == 2
    assert data["image_url"][0] == "http://mock.com/1.jpg"
    
    assert "hashtag" in data
    assert len(data["hashtag"]) == 2
    assert data["hashtag"][0]["word"] == "python"
    assert data["hashtag"][1]["word"] == "fastapi"

def test_create_post_too_few_images(client: TestClient, db_session: Session, setup_user):
    response = client.post(
        "/post/create",
        data=test_post_data,
        files=[]
    )

    assert response.status_code == 422 

def test_create_post_too_many_images(client: TestClient, db_session: Session, setup_user):
    files = [
        ("images", (f"test{i}.png", b"data", "image/png")) for i in range(4)
    ]

    response = client.post(
        "/post/create",
        data=test_post_data,
        files=files
    )

    assert response.status_code == 400
    assert "이미지는 최대 3장" in response.json()["detail"]

def test_create_post_user_not_found(client: TestClient, db_session: Session):
    invalid_data = test_post_data.copy()
    invalid_data["user_id"] = "unknown_user"

    files = [
        ("images", ("test1.png", b"fake", "image/png"))
    ]

    response = client.post(
        "/post/create",
        data=invalid_data,
        files=files
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "사용자를 찾을 수 없습니다."

def test_get_all_posts_with_like_status(client: TestClient, db_session: Session):
    viewer = User(user_id="viewer", email="view@ex.com", hashed_password="pw", name="Viewer")
    author = User(user_id="author", email="auth@ex.com", hashed_password="pw", name="Author")
    db_session.add_all([viewer, author])
    db_session.commit()

    post_liked = Post(
        title="Liked Post",
        content="Content 1",
        user_id=author.user_id,
        created_at=get_kst_now()
    )
    post_not_liked = Post(
        title="Not Liked Post",
        content="Content 2",
        user_id=author.user_id,
        created_at=get_kst_now() - timedelta(hours=1)
    )
    db_session.add_all([post_liked, post_not_liked])
    db_session.commit()
    db_session.refresh(post_liked)

    photo = Photo(post_id=post_liked.post_id, img_url="http://img.com", order=0)
    db_session.add(photo)

    like = Like(user_id=viewer.user_id, post_id=post_liked.post_id)
    db_session.add(like)
    db_session.commit()

    response = client.get(f"/post/{viewer.user_id}")

    assert response.status_code == 200
    data = response.json()

    assert len(data) == 2
    
    assert data[0]["title"] == "Liked Post"
    assert data[0]["is_liked"] is True
    assert data[0]["like_count"] == 1
    
    assert data[1]["title"] == "Not Liked Post"
    assert data[1]["is_liked"] is False
    assert data[1]["like_count"] == 0

def test_get_all_posts_empty(client: TestClient, db_session: Session):
    response = client.get("/post/any_user_id")
    
    assert response.status_code == 200
    assert response.json() == []

@pytest.fixture(scope="function")
def setup_data_for_edit(db_session: Session):
    user = User(
        user_id="edit_tester",
        email="edit@test.com",
        hashed_password="pw",
        name="Edit Tester"
    )
    db_session.add(user)
    
    other_user = User(
        user_id="other_user",
        email="other@test.com",
        hashed_password="pw",
        name="Other"
    )
    db_session.add(other_user)
    db_session.commit()

    tag = Tag(word="old_tag")
    db_session.add(tag)
    db_session.commit()

    post = Post(
        title="Original Title",
        content="Original Content",
        user_id=user.user_id,
        created_at=datetime.utcnow()
    )
    db_session.add(post)
    db_session.commit()
    db_session.refresh(post)

    photo = Photo(post_id=post.post_id, img_url="http://old.com/img.jpg", order=0)
    db_session.add(photo)

    ht = Hashtag(post_id=post.post_id, tag_id=tag.tag_id)
    db_session.add(ht)
    
    db_session.commit()

    return {"user": user, "other_user": other_user, "post": post}

def test_edit_post_endpoint_success(client: TestClient, db_session: Session, setup_data_for_edit):
    post = setup_data_for_edit["post"]
    user = setup_data_for_edit["user"]

    update_data = {
        "post_id": post.post_id,
        "title": "Updated Title",
        "content": "Updated Content",
        "current_user_id": user.user_id,
        "hashtag": ["new_tag", "python"]
    }

    files = [
        ("images", ("new.jpg", b"new_content", "image/jpeg"))
    ]

    with patch("app.api.services.post.upload_img_to_cloudinary") as mock_upload, \
        patch("app.api.services.post.delete_img_from_cloudinary") as mock_delete:
        
        mock_upload.return_value = "http://new.com/img.jpg"

        response = client.put(
            "/post", 
            data=update_data, 
            files=files
        )

        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Updated Title"
        assert data["content"] == "Updated Content"
        assert len(data["image_url"]) == 1
        assert data["image_url"][0] == "http://new.com/img.jpg"
        
        res_tags = [t["word"] for t in data["hashtag"]]
        assert "new_tag" in res_tags
        assert "python" in res_tags

        mock_delete.assert_called_once_with("http://old.com/img.jpg")

def test_edit_post_endpoint_forbidden(client: TestClient, db_session: Session, setup_data_for_edit):
    post = setup_data_for_edit["post"]
    other_user = setup_data_for_edit["other_user"]

    update_data = {
        "post_id": post.post_id,
        "title": "Hacked",
        "content": "Hacked",
        "current_user_id": other_user.user_id,
        "hashtag": []
    }
    files = [("images", ("test.jpg", b"data", "image/jpeg"))]

    response = client.put(
        "/post",
        data=update_data,
        files=files
    )

    assert response.status_code == 403
    assert response.json()["detail"] == "수정 권한이 없습니다."

def test_delete_post_endpoint_success(client: TestClient, db_session: Session, setup_data_for_edit):
    post = setup_data_for_edit["post"]
    user = setup_data_for_edit["user"]

    payload = {
        "post_id": post.post_id,
        "current_user_id": user.user_id
    }

    with patch("app.api.services.post.delete_img_from_cloudinary") as mock_delete:
        response = client.request("DELETE", "/post", json=payload)

        assert response.status_code == 204
        
        mock_delete.assert_called_once_with("http://old.com/img.jpg")

    deleted_post = db_session.query(Post).filter(Post.post_id == post.post_id).first()
    assert deleted_post is None

def test_delete_post_endpoint_not_found(client: TestClient, db_session: Session):
    payload = {
        "post_id": "nonexistent_id",
        "current_user_id": "user"
    }

    response = client.request("DELETE", "/post", json=payload)

    assert response.status_code == 404
    assert response.json()["detail"] == "조건에 해당하는 게시물을 찾지 못했습니다."

def test_delete_post_endpoint_forbidden(client: TestClient, db_session: Session, setup_data_for_edit):
    post = setup_data_for_edit["post"]
    other_user = setup_data_for_edit["other_user"]

    payload = {
        "post_id": post.post_id,
        "current_user_id": other_user.user_id
    }

    response = client.request("DELETE", "/post", json=payload)

    assert response.status_code == 403
    assert response.json()["detail"] == "해당 유저는 권한이 없습니다"