from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.admin import Admin
from app.schemas.user import UserProfile
from app.schemas.video import VideoDetail
from app.services import admin_service
from app.utils.admin_deps import get_current_admin

router = APIRouter(prefix="/api/admin", tags=["管理端"])


class AdminLoginRequest(BaseModel):
    username: str
    password: str


class ReviewRequest(BaseModel):
    status: str
    reason: str | None = None


class ReportHandleRequest(BaseModel):
    status: str  # processed / dismissed


@router.post("/login")
def admin_login(body: AdminLoginRequest, db: Session = Depends(get_db)):
    result = admin_service.admin_login(db, body.username, body.password)
    return {
        "data": {
            "access_token": result["access_token"],
            "token_type": "bearer",
            "admin": {"id": result["admin"].id, "username": result["admin"].username, "role": result["admin"].role},
        },
        "message": "ok",
    }


@router.get("/stats")
def get_stats(admin: Admin = Depends(get_current_admin), db: Session = Depends(get_db)):
    return {"data": admin_service.get_admin_stats(db), "message": "ok"}


@router.get("/users")
def list_users(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    result = admin_service.list_admin_users(db, page, page_size)
    return {"data": {"items": [UserProfile.model_validate(u) for u in result["items"]], "page": result["page"], "page_size": result["page_size"], "total": result["total"]}, "message": "ok"}


@router.put("/users/{user_id}/ban")
def ban_user(user_id: int, admin: Admin = Depends(get_current_admin), db: Session = Depends(get_db)):
    admin_service.ban_user(db, user_id, admin)
    return {"message": "ok"}


@router.put("/users/{user_id}/unban")
def unban_user(user_id: int, admin: Admin = Depends(get_current_admin), db: Session = Depends(get_db)):
    admin_service.unban_user(db, user_id, admin)
    return {"message": "ok"}


@router.get("/videos")
def list_videos(
    status: str | None = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    result = admin_service.list_admin_videos(db, status, page, page_size)
    return {"data": {"items": [VideoDetail.model_validate(v) for v in result["items"]], "page": result["page"], "page_size": result["page_size"], "total": result["total"]}, "message": "ok"}


@router.put("/videos/{video_id}/status")
def review_video(
    video_id: int,
    body: ReviewRequest,
    admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    video = admin_service.review_video(db, video_id, body.status, body.reason, admin)
    return {"data": VideoDetail.model_validate(video), "message": "ok"}


@router.get("/reports")
def list_reports(
    status: str | None = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    from app.models.admin import Report
    result = admin_service.list_reports(db, status, page, page_size)
    return {"data": {"items": result["items"], "page": result["page"], "page_size": result["page_size"], "total": result["total"]}, "message": "ok"}


@router.put("/reports/{report_id}")
def handle_report(
    report_id: int,
    body: ReportHandleRequest,
    admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    admin_service.handle_report(db, report_id, body.status, admin)
    return {"message": "ok"}
