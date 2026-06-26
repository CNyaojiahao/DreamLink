from datetime import datetime

from pydantic import BaseModel
from app.schemas.user import UserProfile


class CommentItem(BaseModel):
    id: int
    user: UserProfile | None = None
    content: str
    is_deleted: bool
    parent_id: int | None = None
    created_at: datetime
    replies: list["CommentItem"] = []

    model_config = {"from_attributes": True}

    @classmethod
    def from_orm_with_replies(cls, obj):
        data = cls.model_validate(obj)
        data.replies = [cls.model_validate(r) for r in getattr(obj, "replies_list", [])]
        return data
