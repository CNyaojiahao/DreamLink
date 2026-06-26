from datetime import datetime

from pydantic import BaseModel

from app.schemas.user import UserProfile


class VideoPartItem(BaseModel):
    id: int
    title: str
    file_path: str
    duration: int
    file_size: int
    order: int

    model_config = {"from_attributes": True}


class VideoListItem(BaseModel):
    id: int
    title: str
    cover: str
    duration: int
    view_count: int
    like_count: int
    author: UserProfile | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


class VideoDetail(BaseModel):
    id: int
    title: str
    description: str | None = None
    cover: str
    duration: int
    view_count: int
    like_count: int
    favorite_count: int
    coin_count: int
    status: str
    author: UserProfile | None = None
    parts: list[VideoPartItem] = []
    created_at: datetime

    model_config = {"from_attributes": True}
