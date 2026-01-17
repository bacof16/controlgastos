from pydantic import BaseModel, ConfigDict
from datetime import date, datetime
from typing import Optional
from uuid import UUID
from decimal import Decimal

class RecurringTemplateBase(BaseModel):
    title: str
    total_installments: int
    installment_amount: Decimal
    start_control_date: date
    autopay_enabled: bool = False
    autopay_day: Optional[int] = None

class RecurringTemplateCreate(RecurringTemplateBase):
    company_id: UUID

class RecurringTemplateUpdate(RecurringTemplateBase):
    pass

class RecurringTemplate(RecurringTemplateBase):
    id: UUID
    company_id: UUID
    installments_paid_before: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
