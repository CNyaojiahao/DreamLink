from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.auth import (
    RegisterRequest,
    LoginRequest,
    RefreshRequest,
    TokenResponse,
    LoginResponse,
    UserBrief,
)
from app.services import auth_service

router = APIRouter(prefix="/api/auth", tags=["认证"])


@router.post("/register")
def register(body: RegisterRequest, db: Session = Depends(get_db)):
    user = auth_service.register(db, body.username, body.email, body.password)
    return {"data": UserBrief.model_validate(user), "message": "ok"}


@router.post("/login", response_model=None)
def login(body: LoginRequest, db: Session = Depends(get_db)):
    result = auth_service.login(db, body.username, body.password)
    return {
        "data": LoginResponse(
            access_token=result["access_token"],
            refresh_token=result["refresh_token"],
            user=UserBrief.model_validate(result["user"]),
        ),
        "message": "ok",
    }


@router.post("/refresh", response_model=None)
def refresh(body: RefreshRequest, db: Session = Depends(get_db)):
    result = auth_service.refresh(db, body.refresh_token)
    return {
        "data": TokenResponse(**result),
        "message": "ok",
    }
