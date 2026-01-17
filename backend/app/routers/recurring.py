from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from app.database import get_db
from app.models.recurring_template import RecurringTemplate as RecModel
from app.schemas.recurring import RecurringTemplate, RecurringTemplateCreate, RecurringTemplateUpdate

router = APIRouter(
    prefix="/recurring",
    tags=["recurring"],
)

@router.post("/", response_model=RecurringTemplate)
def create_template(template: RecurringTemplateCreate, db: Session = Depends(get_db)):
    db_obj = RecModel(**template.model_dump())
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj

@router.get("/company/{company_id}", response_model=List[RecurringTemplate])
def read_templates(company_id: UUID, db: Session = Depends(get_db)):
    return db.query(RecModel).filter(RecModel.company_id == company_id).all()
