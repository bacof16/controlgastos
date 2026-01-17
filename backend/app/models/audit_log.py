import uuid
from datetime import datetime
from sqlalchemy import JSON, Column, String, DateTime, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID
from .base import Base


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False)
    entity_type = Column(String, nullable=False)
    entity_id = Column(UUID(as_uuid=True), nullable=False)
    action = Column(String, nullable=False)  # create, update, delete, autopay
    changed_by = Column(UUID(as_uuid=True), nullable=True)
    before_data = Column(nullable=True)
    after_data = Column(nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)

    __table_args__ = (
        Index("idx_audit_logs_company_id", "company_id"),
        Index("idx_audit_logs_entity_type", "entity_type"),
        Index("idx_audit_logs_entity_id", "entity_id"),
        Index("idx_audit_logs_created_at", "created_at"),
    )
