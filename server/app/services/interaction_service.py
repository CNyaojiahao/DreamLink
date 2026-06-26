from fastapi import HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func as sa_func

from app.models.interaction import Like, Favorite, FavoriteFolder, Coin
from app.models.video import Video, VideoStatus
from app.models.user import User


def _get_published_video(db: Session, video_id: int) -> Video:
    video = db.query(Video).filter(Video.id == video_id, Video.status == VideoStatus.published).first()
    if not video:
        raise HTTPException(status_code=404, detail={"code": "VIDEO_NOT_FOUND", "message": "视频不存在"})
    return video


# ---- 点赞 ----

def toggle_like(db: Session, user: User, video_id: int) -> bool:
    _get_published_video(db, video_id)
    existing = db.query(Like).filter(Like.user_id == user.id, Like.video_id == video_id).first()
    if existing:
        db.delete(existing)
        db.query(Video).filter(Video.id == video_id).update({Video.like_count: Video.like_count - 1})
        db.commit()
        return False
    else:
        db.add(Like(user_id=user.id, video_id=video_id))
        db.query(Video).filter(Video.id == video_id).update({Video.like_count: Video.like_count + 1})
        db.commit()
        return True


def is_liked(db: Session, user_id: int, video_id: int) -> bool:
    return db.query(Like).filter(Like.user_id == user_id, Like.video_id == video_id).first() is not None


# ---- 收藏 ----

def _get_or_create_default_folder(db: Session, user_id: int) -> FavoriteFolder:
    folder = db.query(FavoriteFolder).filter(FavoriteFolder.user_id == user_id, FavoriteFolder.is_default.is_(True)).first()
    if not folder:
        folder = FavoriteFolder(user_id=user_id, name="默认收藏夹", is_default=True)
        db.add(folder)
        db.flush()
    return folder


def toggle_favorite(db: Session, user: User, video_id: int) -> bool:
    _get_published_video(db, video_id)
    folder = _get_or_create_default_folder(db, user.id)
    existing = db.query(Favorite).filter(Favorite.user_id == user.id, Favorite.video_id == video_id).first()
    if existing:
        db.delete(existing)
        db.query(Video).filter(Video.id == video_id).update({Video.favorite_count: Video.favorite_count - 1})
        db.commit()
        return False
    else:
        db.add(Favorite(user_id=user.id, video_id=video_id, folder_id=folder.id))
        db.query(Video).filter(Video.id == video_id).update({Video.favorite_count: Video.favorite_count + 1})
        db.commit()
        return True


def is_favorited(db: Session, user_id: int, video_id: int) -> bool:
    return db.query(Favorite).filter(Favorite.user_id == user_id, Favorite.video_id == video_id).first() is not None


# ---- 投币 ----

def add_coin(db: Session, user: User, video_id: int, amount: int) -> int:
    if amount not in (1, 2):
        raise HTTPException(status_code=422, detail={"code": "VALIDATION_ERROR", "message": "投币数量只能是 1 或 2"})

    _get_published_video(db, video_id)
    existing = db.query(Coin).filter(Coin.user_id == user.id, Coin.video_id == video_id).first()
    already = existing.amount if existing else 0
    if already >= 2:
        raise HTTPException(status_code=422, detail={"code": "VALIDATION_ERROR", "message": "已投满 2 个币"})

    add_amount = min(amount, 2 - already)
    if existing:
        existing.amount += add_amount
    else:
        db.add(Coin(user_id=user.id, video_id=video_id, amount=add_amount))

    db.query(Video).filter(Video.id == video_id).update({Video.coin_count: Video.coin_count + add_amount})
    db.commit()
    return already + add_amount
