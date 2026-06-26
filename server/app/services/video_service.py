from fastapi import HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.models.video import Video, VideoPart, VideoStatus
from app.models.user import User
from app.services import storage_service


def get_video_or_404(db: Session, video_id: int) -> Video:
    video = db.query(Video).filter(Video.id == video_id).first()
    if not video:
        raise HTTPException(
            status_code=404,
            detail={"code": "VIDEO_NOT_FOUND", "message": "视频不存在"},
        )
    return video


def create_video(
    db: Session,
    user: User,
    title: str,
    description: str | None,
    category_id: int | None,
    cover_path: str,
    parts: list[dict],
) -> Video:
    video = Video(
        title=title,
        description=description,
        cover=cover_path,
        author_id=user.id,
        category_id=category_id,
        status=VideoStatus.pending,
    )
    db.add(video)
    db.flush()

    for i, part in enumerate(parts, 1):
        vp = VideoPart(
            video_id=video.id,
            title=part["title"],
            file_path=part["file_path"],
            file_size=part["file_size"],
            order=i,
        )
        db.add(vp)

    db.commit()
    db.refresh(video)
    return video


def get_published_video(db: Session, video_id: int) -> Video:
    video = get_video_or_404(db, video_id)
    if video.status != VideoStatus.published:
        raise HTTPException(
            status_code=404,
            detail={"code": "VIDEO_NOT_FOUND", "message": "视频不存在"},
        )
    return video


def list_videos(
    db: Session,
    page: int = 1,
    page_size: int = 20,
    category_id: int | None = None,
    sort: str = "latest",
    keyword: str | None = None,
    author_id: int | None = None,
    status: VideoStatus | None = VideoStatus.published,
) -> dict:
    query = db.query(Video)
    if status:
        query = query.filter(Video.status == status)
    if category_id:
        query = query.filter(Video.category_id == category_id)
    if author_id:
        query = query.filter(Video.author_id == author_id)
    if keyword:
        query = query.filter(Video.title.ilike(f"%{keyword}%"))

    if sort == "popular":
        query = query.order_by(Video.view_count.desc())
    elif sort == "most_liked":
        query = query.order_by(Video.like_count.desc())
    else:
        query = query.order_by(Video.created_at.desc())

    total = query.count()
    items = query.offset((page - 1) * page_size).limit(page_size).all()

    return {
        "items": items,
        "page": page,
        "page_size": page_size,
        "total": total,
    }


def record_view(db: Session, video: Video) -> None:
    video.view_count += 1
    db.commit()


def update_video(
    db: Session,
    video: Video,
    user: User,
    title: str | None = None,
    description: str | None = None,
    category_id: int | None = None,
) -> Video:
    if video.author_id != user.id:
        raise HTTPException(status_code=403, detail={"code": "PERMISSION_DENIED", "message": "无权操作"})
    if title is not None:
        video.title = title
    if description is not None:
        video.description = description
    if category_id is not None:
        video.category_id = category_id
    db.commit()
    db.refresh(video)
    return video


def delete_video(db: Session, video: Video, user: User) -> None:
    if video.author_id != user.id:
        raise HTTPException(status_code=403, detail={"code": "PERMISSION_DENIED", "message": "无权操作"})
    db.delete(video)
    db.commit()
