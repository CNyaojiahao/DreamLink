from datetime import datetime

from pydantic import BaseModel, Field


class UserProfile(BaseModel):
    id: int
    username: str
    avatar: str | None = None
    bio: str | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


class UserDetail(BaseModel):
    id: int
    username: str
    email: str
    avatar: str | None = None
    bio: str | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


class UpdateUserRequest(BaseModel):
    avatar: str | None = Field(None, max_length=500)
    bio: str | None = Field(None, max_length=300)
