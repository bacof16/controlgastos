import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, Boolean, Date, DateTime, Numeric, ForeignKey, CheckConstraint, UniqueConstraint, Index
from sqlalchemy.dialects.postgresql import UUID
from .base import Base


class Payment(Base):
    __tablename__ = "payments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False)
    template_id = Column(UUID(as_uuid=True), ForeignKey("recurring_templates.id"), nullable=True)
    installment_number = Column(Integer, nullable=True)
    installment_total = Column(Integer, nullable=True)
    due_date = Column(Date, nullable=False)
    amount = Column(Numeric(12, 2), nullable=False)
    status = Column(String, nullable=False, default="pending")  # pending, scheduled, paid, overdue
    autopay = Column(Boolean, nullable=False, default=False)
    payment_method = Column(String, nullable=True)
    payment_reference = Column(String, nullable=True)
    paid_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    __table_args__ = (
        UniqueConstraint(
            "company_id", "template_id", "installment_number",
            name="unique_company_template_installment"
        ),
        CheckConstraint(
            "installment_number IS NULL OR (installment_number >= 1 AND installment_number <= installment_total)",
            name="check_installment_number_in_range"
        ),
        CheckConstraint(
            "status IN ('pending', 'scheduled', 'paid', 'overdue')",
            name="check_status_valid"
        ),
        Index("idx_payments_company_id", "company_id"),
        Index("idx_payments_due_date", "due_date"),
        Index("idx_payments_status", "status"),
        Index("idx_payments_template_id", "template_id"),
    )
