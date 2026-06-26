from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.comment import Comment
from app.models.video import Video, VideoStatus
from app.models.user import User


def create_comment(db: Session, user: User, video_id: int, content: str, parent_id: int | None = None) -> Comment:
    video = db.query(Video).filter(Video.id == video_id, Video.status == VideoStatus.published).first()
    if not video:
        raise HTTPException(status_code=404, detail={"code": "VIDEO_NOT_FOUND", "message": "视频不存在"})

    if parent_id:
        parent = db.query(Comment).filter(Comment.id == parent_id, Comment.video_id == video_id).first()
        if not parent:
            raise HTTPException(status_code=404, detail={"code": "COMMENT_NOT_FOUND", "message": "父评论不存在"})

    comment = Comment(user_id=user.id, video_id=video_id, parent_id=parent_id, content=content)
    db.add(comment)
    db.commit()
    db.refresh(comment)
    return comment


def list_comments(db: Session, video_id: int, page: int = 1, page_size: int = 20) -> dict:
    query = db.query(Comment).filter(Comment.video_id == video_id, Comment.parent_id.is_(None), Comment.is_deleted.is_(False))
    total = query.count()
    items = query.order_by(Comment.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()

    # 加载回复
    if items:
        parent_ids = [c.id for c in items]
        replies = db.query(Comment).filter(Comment.parent_id.in_(parent_ids), Comment.is_deleted.is_(False)).order_by(Comment.created_at).all()
        reply_map: dict[int, list] = {}
        for r in replies:
            reply_map.setdefault(r.parent_id, []).append(r)
        for c in items:
            c.replies_list = reply_map.get(c.id, [])

    return {"items": items, "page": page, "page_size": page_size, "total": total}


def delete_comment(db: Session, comment: Comment, user: User) -> None:
    if comment.user_id != user.id:
        raise HTTPException(status_code=403, detail={"code": "PERMISSION_DENIED", "message": "无权操作"})
    comment.is_deleted = True
    comment.content = "该评论已删除"
    db.commit()
