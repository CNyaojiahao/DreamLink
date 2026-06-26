from fastapi import FastAPI, Query, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.api.auth import router as auth_router
from app.api.users import router as users_router
from app.api.videos import router as videos_router
from app.api.comments import router as comments_router
from app.api.interactions import router as interactions_router
from app.api.categories import router as categories_router
from app.api.admin import router as admin_router
from app.models.video import Video, VideoStatus
from app.schemas.video import VideoListItem

app = FastAPI(title="DreamLink API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(users_router)
app.include_router(videos_router)
app.include_router(comments_router)
app.include_router(interactions_router)
app.include_router(categories_router)
app.include_router(admin_router)


@app.get("/api/health")
def health_check():
    return {"status": "ok"}


@app.get("/api/feed")
def feed(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=50),
    db: Session = Depends(get_db),
):
    """首页推荐：按综合分数排序"""
    query = db.query(Video).filter(Video.status == VideoStatus.published)
    # 综合分数 = 播放 + 点赞*5 + 收藏*8 + 投币*10
    score = Video.view_count + Video.like_count * 5 + Video.favorite_count * 8 + Video.coin_count * 10
    query = query.order_by(score.desc(), Video.created_at.desc())
    total = query.count()
    items = query.offset((page - 1) * page_size).limit(page_size).all()
    return {
        "data": {
            "items": [VideoListItem.model_validate(v) for v in items],
            "page": page,
            "page_size": page_size,
            "total": total,
        },
        "message": "ok",
    }


@app.get("/api/search")
def search(
    q: str = Query(..., min_length=1),
    category_id: int | None = None,
    sort: str = Query("relevance"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=50),
    db: Session = Depends(get_db),
):
    """搜索视频：标题 ILIKE"""
    query = db.query(Video).filter(
        Video.status == VideoStatus.published,
        Video.title.ilike(f"%{q}%"),
    )
    if category_id:
        query = query.filter(Video.category_id == category_id)
    if sort == "latest":
        query = query.order_by(Video.created_at.desc())
    elif sort == "views":
        query = query.order_by(Video.view_count.desc())
    else:
        query = query.order_by(Video.created_at.desc())

    total = query.count()
    items = query.offset((page - 1) * page_size).limit(page_size).all()
    return {
        "data": {
            "items": [VideoListItem.model_validate(v) for v in items],
            "page": page,
            "page_size": page_size,
            "total": total,
        },
        "message": "ok",
    }


@app.get("/api/ranking")
def ranking(
    period: str = Query("all"),  # daily / weekly / all
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=50),
    db: Session = Depends(get_db),
):
    """排行榜"""
    from datetime import datetime, timedelta, timezone
    query = db.query(Video).filter(Video.status == VideoStatus.published)

    now = datetime.now(timezone.utc)
    if period == "daily":
        query = query.filter(Video.created_at >= now - timedelta(days=1))
    elif period == "weekly":
        query = query.filter(Video.created_at >= now - timedelta(days=7))

    score = Video.view_count + Video.like_count * 5 + Video.favorite_count * 8 + Video.coin_count * 10
    query = query.order_by(score.desc())
    total = query.count()
    items = query.offset((page - 1) * page_size).limit(page_size).all()
    return {
        "data": {
            "items": [VideoListItem.model_validate(v) for v in items],
            "page": page,
            "page_size": page_size,
            "total": total,
        },
        "message": "ok",
    }


@app.post("/api/reports")
def create_report(
    target_id: int = Query(...),
    target_type: str = Query(...),
    reason: str = Query(...),
    db: Session = Depends(get_db),
):
    """举报内容（简化版，不需要登录）"""
    from app.models.admin import Report
    report = Report(target_id=target_id, target_type=target_type, reason=reason, reporter_id=0)
    db.add(report)
    db.commit()
    return {"message": "ok"}
