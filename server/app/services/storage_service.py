import os
import uuid
from datetime import datetime
from pathlib import Path

from fastapi import UploadFile, HTTPException

from app.config import settings

ALLOWED_VIDEO_TYPES = {"video/mp4", "video/webm"}
ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/webp"}

VIDEO_MAX_SIZE = 500 * 1024 * 1024  # 500MB
COVER_MAX_SIZE = 5 * 1024 * 1024    # 5MB
AVATAR_MAX_SIZE = 2 * 1024 * 1024   # 2MB


def _generate_path(category: str, ext: str) -> tuple[str, str]:
    """生成存储路径，返回 (相对路径, 绝对路径)"""
    today = datetime.now().strftime("%Y/%m/%d")
    filename = f"{uuid.uuid4().hex}{ext}"
    rel_path = f"/media/{category}/{today}/{filename}"
    abs_path = os.path.join(settings.media_root, category, today, filename)
    os.makedirs(os.path.dirname(abs_path), exist_ok=True)
    return rel_path, abs_path


def _get_ext(filename: str) -> str:
    _, ext = os.path.splitext(filename)
    return ext.lower()


async def save_upload_file(
    file: UploadFile,
    category: str,
    allowed_types: set[str],
    max_size: int,
) -> str:
    """保存上传文件，返回相对路径"""
    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=415,
            detail={"code": "UNSUPPORTED_MEDIA_TYPE", "message": f"不支持的文件类型: {file.content_type}"},
        )

    content = await file.read()
    if len(content) > max_size:
        raise HTTPException(
            status_code=413,
            detail={"code": "FILE_TOO_LARGE", "message": "文件过大"},
        )

    ext = _get_ext(file.filename or "file")
    rel_path, abs_path = _generate_path(category, ext)

    with open(abs_path, "wb") as f:
        f.write(content)

    return rel_path


async def save_video(file: UploadFile) -> str:
    return await save_upload_file(file, "videos", ALLOWED_VIDEO_TYPES, VIDEO_MAX_SIZE)


async def save_cover(file: UploadFile) -> str:
    return await save_upload_file(file, "covers", ALLOWED_IMAGE_TYPES, COVER_MAX_SIZE)


async def save_avatar(file: UploadFile) -> str:
    return await save_upload_file(file, "avatars", ALLOWED_IMAGE_TYPES, AVATAR_MAX_SIZE)
