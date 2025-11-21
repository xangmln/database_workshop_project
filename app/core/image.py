import os
from dotenv import load_dotenv
import cloudinary
import cloudinary.uploader

from fastapi import UploadFile, HTTPException
load_dotenv()

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
    try:
        response = cloudinary.uploader.upload(
            file.file,
            folder="database_workshop"
        )
        return response["secure_url"]
    except Exception as e:
        print(f"Cloudinary upload error: {e}")
        raise HTTPException(status_code=500, detail="Image upload failed")