from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.services import interaction_service
from app.utils.deps import get_current_user

router = APIRouter(tags=["互动"])


class CoinRequest(BaseModel):
    amount: int


@router.post("/api/videos/{video_id}/like")
def like_video(
    video_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    liked = interaction_service.toggle_like(db, current_user, video_id)
    return {"data": {"liked": liked}, "message": "ok"}


@router.delete("/api/videos/{video_id}/like")
def unlike_video(
    video_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    interaction_service.toggle_like(db, current_user, video_id)
    return {"data": {"liked": False}, "message": "ok"}


@router.post("/api/videos/{video_id}/favorite")
def favorite_video(
    video_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    favorited = interaction_service.toggle_favorite(db, current_user, video_id)
    return {"data": {"favorited": favorited}, "message": "ok"}


@router.delete("/api/videos/{video_id}/favorite")
def unfavorite_video(
    video_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    interaction_service.toggle_favorite(db, current_user, video_id)
    return {"data": {"favorited": False}, "message": "ok"}


@router.post("/api/videos/{video_id}/coin")
def coin_video(
    video_id: int,
    body: CoinRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    total = interaction_service.add_coin(db, current_user, video_id, body.amount)
    return {"data": {"total": total}, "message": "ok"}


@router.get("/api/videos/{video_id}/interaction")
def get_interaction_status(
    video_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return {
        "data": {
            "liked": interaction_service.is_liked(db, current_user.id, video_id),
            "favorited": interaction_service.is_favorited(db, current_user.id, video_id),
        },
        "message": "ok",
    }
