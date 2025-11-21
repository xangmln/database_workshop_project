import logging
import os
from dotenv import load_dotenv
import cloudinary
import cloudinary.uploader

from fastapi import UploadFile, HTTPException
load_dotenv()

logger = logging.getLogger(__name__)

ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png", "gif", 'webp'}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key=os.getenv("CLOUDINARY_API_KEY"),
    api_secret=os.getenv("CLOUDINARY_API_SECRET"),
    secure=True
)

def upload_img_to_cloudinary(file: UploadFile) -> str:
    """
    이미지를 Cloudinary에 업로드하고 URL을 반환합니다.
    """
    if file.filename:
        ext = file.filename.rsplit('.', 1)[-1].lower()
        if ext not in ALLOWED_EXTENSIONS:
            raise HTTPException(status_code=400, detail=f"허용되지 않는 파일 형식입니다. 허용 형식: {', '.join(ALLOWED_EXTENSIONS)}")
    file.file.seek(0,2)
    file_size = file.file.tell()
    file.file.seek(0)
    if file_size > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="파일 크기가 10MB를 초과할 수 없습니다.")
    try:
        response = cloudinary.uploader.upload(
            file.file,
            folder="database_workshop"
        )
        return response["secure_url"]
    except Exception as e:
        logger.error(f"Cloudinary 업로드 실패: {e}")
        raise HTTPException(status_code=500, detail="이미지 업로드에 실패했습니다.") from e