from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.admin import Admin
from app.utils.jwt import decode_token

admin_bearer = HTTPBearer()


def get_current_admin(
    credentials: HTTPAuthorizationCredentials = Depends(admin_bearer),
    db: Session = Depends(get_db),
) -> Admin:
    payload = decode_token(credentials.credentials)
    if payload is None or payload.get("type") != "access":
        raise HTTPException(status_code=401, detail={"code": "AUTH_TOKEN_EXPIRED", "message": "Token 无效或已过期"})

    admin = db.query(Admin).filter(Admin.id == int(payload["sub"])).first()
    if not admin or not admin.is_active:
        raise HTTPException(status_code=401, detail={"code": "AUTH_REQUIRED", "message": "管理员不存在或已停用"})
    return admin
