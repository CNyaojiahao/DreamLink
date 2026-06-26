from datetime import datetime, timezone

from fastapi import HTTPException, status
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from app.models.admin import Admin, AdminRole, Report, AuditLog
from app.models.video import Video, VideoStatus
from app.models.user import User
from app.utils.jwt import create_access_token, decode_token

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def admin_login(db: Session, username: str, password: str) -> dict:
    admin = db.query(Admin).filter(Admin.username == username).first()
    if not admin or not pwd_context.verify(password, admin.password_hash):
        raise HTTPException(status_code=401, detail={"code": "AUTH_INVALID_CREDENTIALS", "message": "用户名或密码错误"})
    if not admin.is_active:
        raise HTTPException(status_code=403, detail={"code": "PERMISSION_DENIED", "message": "账号已停用"})
    # 管理员 token 用 admin: 前缀区分
    token = create_access_token(admin.id)
    return {"access_token": token, "admin": admin}


def get_admin_stats(db: Session) -> dict:
    return {
        "user_count": db.query(User).count(),
        "video_count": db.query(Video).count(),
        "pending_video_count": db.query(Video).filter(Video.status == VideoStatus.pending).count(),
        "pending_report_count": db.query(Report).filter(Report.status == "pending").count(),
    }


def list_admin_users(db: Session, page: int = 1, page_size: int = 20) -> dict:
    query = db.query(User).order_by(User.created_at.desc())
    total = query.count()
    items = query.offset((page - 1) * page_size).limit(page_size).all()
    return {"items": items, "page": page, "page_size": page_size, "total": total}


def ban_user(db: Session, user_id: int, admin: Admin) -> User:
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail={"code": "USER_NOT_FOUND", "message": "用户不存在"})
    user.is_banned = True
    db.add(AuditLog(admin_id=admin.id, target_type="user", target_id=user_id, action="ban"))
    db.commit()
    return user


def unban_user(db: Session, user_id: int, admin: Admin) -> User:
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail={"code": "USER_NOT_FOUND", "message": "用户不存在"})
    user.is_banned = False
    db.add(AuditLog(admin_id=admin.id, target_type="user", target_id=user_id, action="unban"))
    db.commit()
    return user


def list_admin_videos(db: Session, video_status: str | None = None, page: int = 1, page_size: int = 20) -> dict:
    query = db.query(Video)
    if video_status:
        query = query.filter(Video.status == video_status)
    query = query.order_by(Video.created_at.desc())
    total = query.count()
    items = query.offset((page - 1) * page_size).limit(page_size).all()
    return {"items": items, "page": page, "page_size": page_size, "total": total}


def review_video(db: Session, video_id: int, new_status: str, reason: str | None, admin: Admin) -> Video:
    video = db.query(Video).filter(Video.id == video_id).first()
    if not video:
        raise HTTPException(status_code=404, detail={"code": "VIDEO_NOT_FOUND", "message": "视频不存在"})
    video.status = new_status
    video.reject_reason = reason if new_status == "rejected" else None
    db.add(AuditLog(admin_id=admin.id, target_type="video", target_id=video_id, action=f"status:{new_status}", reason=reason))
    db.commit()
    db.refresh(video)
    return video


def list_reports(db: Session, report_status: str | None = None, page: int = 1, page_size: int = 20) -> dict:
    query = db.query(Report)
    if report_status:
        query = query.filter(Report.status == report_status)
    query = query.order_by(Report.created_at.desc())
    total = query.count()
    items = query.offset((page - 1) * page_size).limit(page_size).all()
    return {"items": items, "page": page, "page_size": page_size, "total": total}


def handle_report(db: Session, report_id: int, new_status: str, admin: Admin) -> Report:
    report = db.query(Report).filter(Report.id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail={"code": "REPORT_NOT_FOUND", "message": "举报不存在"})
    report.status = new_status
    report.handled_by = admin.id
    report.handled_at = datetime.now(timezone.utc)
    db.commit()
    return report
