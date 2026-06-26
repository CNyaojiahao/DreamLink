from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.category import Category

router = APIRouter(prefix="/api/categories", tags=["分区"])


@router.get("")
def list_categories(db: Session = Depends(get_db)):
    categories = db.query(Category).filter(Category.is_active.is_(True)).order_by(Category.order).all()
    return {
        "data": [{"id": c.id, "name": c.name, "description": c.description} for c in categories],
        "message": "ok",
    }
