from pydantic import BaseModel, ConfigDict
from datetime import date, datetime
from typing import Optional
from uuid import UUID
from decimal import Decimal

# Shared properties
class PaymentBase(BaseModel):
    installment_number: Optional[int] = None
    installment_total: Optional[int] = None
    due_date: date
    amount: Decimal
    status: str = "pending"
    autopay: bool = False
    payment_method: Optional[str] = None
    payment_reference: Optional[str] = None

# Properties to receive on item creation
class PaymentCreate(PaymentBase):
    company_id: UUID

# Properties to receive on item update
class PaymentUpdate(PaymentBase):
    pass

# Properties shared by models stored in DB
class PaymentInDBBase(PaymentBase):
    id: UUID
    company_id: UUID
    created_at: datetime
    updated_at: datetime
    paid_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

# Properties to return to client
class Payment(PaymentInDBBase):
    pass
