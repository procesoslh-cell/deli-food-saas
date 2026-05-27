from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from src.db.session import get_db
from src.models.models import Category

router = APIRouter(prefix='/categories', tags=['categories'])
class CategoryIn(BaseModel):
    name: str
    description: str = ''

@router.get('')
def list_categories(db: Session = Depends(get_db)):
    return db.query(Category).filter(Category.active == True).order_by(Category.name).all()

@router.post('')
def create_category(payload: CategoryIn, db: Session = Depends(get_db)):
    category = Category(**payload.model_dump())
    db.add(category); db.commit(); db.refresh(category)
    return category
