from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.schemas.user import UserDetail, UpdateUserRequest
from app.utils.deps import get_current_user

router = APIRouter(prefix="/api/users", tags=["用户"])


@router.get("/me")
def get_me(current_user: User = Depends(get_current_user)):
    return {"data": UserDetail.model_validate(current_user), "message": "ok"}


@router.put("/me")
def update_me(
    body: UpdateUserRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if body.avatar is not None:
        current_user.avatar = body.avatar
    if body.bio is not None:
        current_user.bio = body.bio
    db.commit()
    db.refresh(current_user)
    return {"data": UserDetail.model_validate(current_user), "message": "ok"}


@router.get("/{user_id}")
def get_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail={"code": "USER_NOT_FOUND", "message": "用户不存在"})
    from app.schemas.user import UserProfile
    return {"data": UserProfile.model_validate(user), "message": "ok"}
