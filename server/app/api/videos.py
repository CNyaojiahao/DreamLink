from fastapi import APIRouter, Depends, UploadFile, File, Form, Request
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.models.video import VideoStatus
from app.schemas.video import VideoDetail, VideoListItem, VideoPartItem
from app.services import video_service, storage_service
from app.utils.deps import get_current_user

router = APIRouter(prefix="/api/videos", tags=["视频"])


@router.get("")
def list_videos(
    page: int = 1,
    page_size: int = 20,
    category_id: int | None = None,
    sort: str = "latest",
    keyword: str | None = None,
    db: Session = Depends(get_db),
):
    result = video_service.list_videos(db, page, page_size, category_id, sort, keyword)
    return {
        "data": {
            "items": [VideoListItem.model_validate(v) for v in result["items"]],
            "page": result["page"],
            "page_size": result["page_size"],
            "total": result["total"],
        },
        "message": "ok",
    }


@router.post("")
async def create_video(
    title: str = Form(...),
    description: str | None = Form(None),
    category_id: int | None = Form(None),
    cover: UploadFile = File(...),
    parts: list[UploadFile] = File(...),
    part_titles: str = Form(""),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    cover_path = await storage_service.save_cover(cover)

    titles = [t.strip() for t in part_titles.split(",") if t.strip()] if part_titles else []
    part_data = []
    for i, part_file in enumerate(parts):
        file_path = await storage_service.save_video(part_file)
        part_data.append({
            "title": titles[i] if i < len(titles) else f"P{i + 1}",
            "file_path": file_path,
            "file_size": part_file.size or 0,
        })

    video = video_service.create_video(db, current_user, title, description, category_id, cover_path, part_data)
    return {"data": VideoDetail.model_validate(video), "message": "ok"}


@router.get("/{video_id}")
def get_video(video_id: int, db: Session = Depends(get_db)):
    video = video_service.get_published_video(db, video_id)
    return {"data": VideoDetail.model_validate(video), "message": "ok"}


@router.put("/{video_id}")
def update_video(
    video_id: int,
    title: str | None = None,
    description: str | None = None,
    category_id: int | None = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    video = video_service.get_video_or_404(db, video_id)
    video = video_service.update_video(db, video, current_user, title, description, category_id)
    return {"data": VideoDetail.model_validate(video), "message": "ok"}


@router.delete("/{video_id}")
def delete_video(
    video_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    video = video_service.get_video_or_404(db, video_id)
    video_service.delete_video(db, video, current_user)
    return {"message": "ok"}


@router.get("/{video_id}/parts")
def get_parts(video_id: int, db: Session = Depends(get_db)):
    video_service.get_video_or_404(db, video_id)
    from app.models.video import VideoPart
    parts = db.query(VideoPart).filter(VideoPart.video_id == video_id).order_by(VideoPart.order).all()
    return {"data": [VideoPartItem.model_validate(p) for p in parts], "message": "ok"}


@router.post("/{video_id}/view")
def record_view(video_id: int, db: Session = Depends(get_db)):
    video = video_service.get_published_video(db, video_id)
    video_service.record_view(db, video)
    return {"message": "ok"}
