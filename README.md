# DB Workshop Program API

FastAPI 기반으로 구현한 소셜 피드용 백엔드입니다. 사용자 인증, 게시글/댓글/좋아요/태그 관리와 이미지 업로드(Cloudinary)를 제공하며 Render로 배포했습니다.

## 주요 기능
- 회원가입/로그인 및 비밀번호, 이메일, 이름, 바이오 수정
- 게시글 생성·수정·삭제(이미지 1~3장 업로드, 태그 연결)
- 댓글 작성/조회, 좋아요 토글 및 좋아요한 게시글 목록 조회
- 태그별 게시글 검색, 사용자 프로필 조회(작성 글 + 좋아요 수, 내가 좋아요 눌렀는지 여부 포함)
- Cloudinary 업로드: jpg/jpeg/png/gif/webp, 10MB 이하

## 기능 상세
- 인증/계정: 이메일 중복을 막고 비밀번호를 해시 저장. 로그인·비밀번호 변경 시 올바른 비밀번호를 검사합니다.
- 게시글/이미지: 최소 1장, 최대 3장의 이미지를 Cloudinary에 업로드하고 URL을 저장합니다. 수정 시 기존 이미지를 Cloudinary에서 삭제 후 재업로드하며, 태그도 새로 교체합니다. 삭제 시 게시글과 연동된 이미지/태그를 함께 정리합니다.
- 태그: 게시글 등록·수정 시 전달된 태그 단어가 없으면 자동 생성합니다. 태그 검색 결과에는 작성자, 이미지, 태그 목록, 좋아요 수, 내 좋아요 여부가 포함됩니다.
- 좋아요: 동일 게시글·사용자 조합으로 두 번 이상 등록되지 않으며, 삭제 시 조합을 기준으로 제거합니다. 내가 좋아요한 게시글 목록을 최신순으로 제공합니다.
- 댓글: 작성·조회 시 작성자의 이름을 함께 반환합니다.
- 사용자 프로필: 특정 사용자의 게시글 목록을 최신순으로 반환하며, 각 게시글에 총 좋아요 수와 현재 사용자의 좋아요 여부를 포함합니다.

## 기술 스택
- FastAPI, Pydantic, SQLAlchemy
- MySQL (SQLAlchemy `DATABASE_URL`, `mysqlclient`)
- Cloudinary (이미지 저장)
- Render (배포), Uvicorn (ASGI 서버)

## 디렉터리 개요
- `app/main.py`: FastAPI 앱 생성, 라우터 등록, CORS 설정
- `app/api/routes/*`: 엔드포인트 정의 (auth, post, comment, like, tag, user)
- `app/api/services/*`: 비즈니스 로직
- `app/api/models/*`: SQLAlchemy 모델
- `app/api/schemas/*`: Pydantic 스키마
- `app/core/db.py`: DB 세션/엔진 설정 (`DATABASE_URL` 사용)
- `app/core/image.py`: Cloudinary 업로드/삭제 헬퍼

## 환경 변수(.env 예시)
```
DATABASE_URL=mysql://<USER>:<PASSWORD>@<HOST>:<PORT>/<DB_NAME>
CLOUDINARY_CLOUD_NAME=<cloud-name>
CLOUDINARY_API_KEY=<api-key>
CLOUDINARY_API_SECRET=<api-secret>
```

## 로컬 실행 방법
1) Python 3.11+ 가상환경 생성 및 활성화
```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
```
2) 의존성 설치
```bash
pip install -r requirements.txt
```
3) `.env` 파일을 위 예시대로 준비 (DB/Cloudinary 정보 필요)
4) 개발 서버 실행
```bash
uvicorn app.main:app --reload
```
5) 문서 확인: http://localhost:8000/docs

## 주요 API 요약
- `POST /auth/signup` 회원가입 (body: email, password, name)
- `POST /auth/login` 로그인 (body: email, password)
- `PATCH /auth/{user_id}/password` 비밀번호 변경 (body: old_password, new_password)
- `GET /post/{current_user_id}` 전체 피드 조회 (like 여부/개수 포함)
- `POST /post/create` 게시글 생성 (multipart: title, content, user_id, tags[], images[1..3])
- `PUT /post` 게시글 수정 (multipart: post_id, title, content, current_user_id, hashtag[], images[1..3])
- `DELETE /post` 게시글 삭제 (body: post_id, current_user_id)
- `POST /comment` 댓글 생성 (body: user_id, post_id, content)
- `GET /comment/post/{post_id}` 댓글 목록
- `POST /like` 좋아요 추가 (body: user_id, post_id)
- `DELETE /like` 좋아요 취소 (body: user_id, post_id)
- `GET /like/{user_id}` 내가 좋아요한 게시글
- `GET /tag/{tag_word}/{current_user_id}` 특정 태그 게시글
- `GET /user/{user_id}/profile` 사용자 프로필 조회
- `PATCH /user/{user_id}/bio|email|name` 사용자 정보 변경

## Render 배포 메모
- Start Command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- Render Dashboard에 위 환경 변수를 그대로 등록
- DB는 Render 외부 MySQL 호스트 또는 Render 내부 MySQL(Private Service) 주소를 `DATABASE_URL`에 입력
- 배포 URL 예시: `https://<your-service>.onrender.com` (실제 주소로 교체)

## 테스트
- pytest 기반 스위트가 `test/`에 포함되어 있습니다. 필요 시 `pip install pytest` 후 실행하세요.
```bash
pytest
```
