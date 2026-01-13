import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, Boolean, Date, DateTime, Numeric, ForeignKey, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID
from .base import Base


class RecurringTemplate(Base):
    __tablename__ = "recurring_templates"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False)
    title = Column(String, nullable=False)
    total_installments = Column(Integer, nullable=False)
    installments_paid_before = Column(Integer, nullable=False, default=0)
    installment_amount = Column(Numeric(12, 2), nullable=False)
    start_control_date = Column(Date, nullable=False)
    autopay_enabled = Column(Boolean, nullable=False, default=False)
    autopay_day = Column(Integer, nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    __table_args__ = (
        CheckConstraint(
            "installments_paid_before <= total_installments",
            name="check_installments_paid_before_lte_total"
        ),
        CheckConstraint(
            "autopay_day IS NULL OR (autopay_day >= 1 AND autopay_day <= 28)",
            name="check_autopay_day_range"
        ),
    )
