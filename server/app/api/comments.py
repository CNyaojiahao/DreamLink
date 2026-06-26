from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.schemas.comment import CommentItem
from app.services import comment_service
from app.utils.deps import get_current_user

router = APIRouter(tags=["评论"])


class CreateCommentRequest(BaseModel):
    content: str = Field(..., min_length=1, max_length=1000)
    parent_id: int | None = None


@router.get("/api/videos/{video_id}/comments")
def list_comments(
    video_id: int,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=50),
    db: Session = Depends(get_db),
):
    result = comment_service.list_comments(db, video_id, page, page_size)
    return {
        "data": {
            "items": [CommentItem.from_orm_with_replies(c) for c in result["items"]],
            "page": result["page"],
            "page_size": result["page_size"],
            "total": result["total"],
        },
        "message": "ok",
    }


@router.post("/api/videos/{video_id}/comments")
def create_comment(
    video_id: int,
    body: CreateCommentRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    comment = comment_service.create_comment(db, current_user, video_id, body.content, body.parent_id)
    return {"data": CommentItem.model_validate(comment), "message": "ok"}


@router.delete("/api/comments/{comment_id}")
def delete_comment(
    comment_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    from app.models.comment import Comment
    comment = db.query(Comment).filter(Comment.id == comment_id).first()
    if not comment:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail={"code": "COMMENT_NOT_FOUND", "message": "评论不存在"})
    comment_service.delete_comment(db, comment, current_user)
    return {"message": "ok"}
