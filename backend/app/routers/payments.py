from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID
from datetime import datetime
import traceback

from app.database import get_db
from app.models.payment import Payment as PaymentModel
from app.schemas.payment import Payment, PaymentCreate, PaymentUpdate

router = APIRouter(
    prefix="/payments",
    tags=["payments"],
)

@router.post("/", response_model=Payment)
def create_payment(payment: PaymentCreate, db: Session = Depends(get_db)):
    try:
        print(f"DEBUG: Payload: {payment.model_dump()}")
        db_payment = PaymentModel(**payment.model_dump())
        db.add(db_payment)
        db.commit()
        db.refresh(db_payment)
        return db_payment
    except Exception as e:
        print("ERROR CREATING PAYMENT:")
        traceback.print_exc()
        # If possible rollback, but if commit succeeded, we might be here due to response validation
        # We can't rollback a committed transaction easily without manual cleanup, 
        # but usually 500 here means commit failed OR response failed.
        # If response failed, data is in DB.
        raise HTTPException(status_code=500, detail=f"Server Error: {str(e)}")

@router.get("/", response_model=List[Payment])
def read_payments(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    payments = db.query(PaymentModel).offset(skip).limit(limit).all()
    return payments

@router.get("/company/{company_id}", response_model=List[Payment])
def read_payments_by_company(company_id: UUID, db: Session = Depends(get_db)):
    payments = db.query(PaymentModel).filter(PaymentModel.company_id == company_id).all()
    return payments

@router.put("/{payment_id}", response_model=Payment)
def update_payment(payment_id: UUID, payment: PaymentUpdate, db: Session = Depends(get_db)):
    db_payment = db.query(PaymentModel).filter(PaymentModel.id == payment_id).first()
    if not db_payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    
    payment_data = payment.model_dump(exclude_unset=True)
    for key, value in payment_data.items():
        setattr(db_payment, key, value)
    
    if payment_data.get("status") == "paid" and not db_payment.paid_at:
        db_payment.paid_at = datetime.utcnow()

    db.add(db_payment)
    db.commit()
    db.refresh(db_payment)
    return db_payment

@router.get("/setup/default-company")
def get_default_company(db: Session = Depends(get_db)):
    from app.models.company import Company
    company = db.query(Company).first()
    if not company:
        raise HTTPException(status_code=404, detail="No company found")
    return {"id": str(company.id), "name": company.name}

@router.delete("/{payment_id}")
def delete_payment(payment_id: UUID, db: Session = Depends(get_db)):
    db_payment = db.query(PaymentModel).filter(PaymentModel.id == payment_id).first()
    if not db_payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    
    db.delete(db_payment)
    db.commit()
    return {"ok": True}
