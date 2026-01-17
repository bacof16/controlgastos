from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from app.database import get_db
from app.models.company import Company as CompanyModel
from app.schemas.company import Company, CompanyCreate

router = APIRouter(
    prefix="/companies",
    tags=["companies"],
)

@router.get("/", response_model=List[Company])
def read_companies(db: Session = Depends(get_db)):
    return db.query(CompanyModel).filter(CompanyModel.is_active == True).all()

@router.post("/", response_model=Company)
def create_company(company: CompanyCreate, db: Session = Depends(get_db)):
    db_obj = CompanyModel(**company.model_dump())
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj
