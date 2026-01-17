"""Notification queue model for generic notification scheduling."""

import uuid
from datetime import datetime
from sqlalchemy import JSON, Column, String, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from .base import Base


class NotificationQueue(Base):
    """Cola de notificaciones con payload genérico.
    
    Arquitectura:
    - Payload flexible (JSON) para cualquier tipo de notificación
    - Estado de envío (pending/sent/failed)
    - Agendamiento programable (scheduled_for)
    - Sin enviar nada todavía (estructura preparada)
    """
    
    __tablename__ = "notification_queue"
    
    # Identificador único UUID (primary key)
    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        comment="Identificador único de la notificación"
    )
    
    # Relación con empresa
    company_id = Column(
        UUID(as_uuid=True),
        ForeignKey("companies.id"),
        nullable=False,
        index=True,
        comment="Empresa asociada"
    )
    
    # Canal de envío
    channel = Column(
        String(50),
        nullable=False,
        comment="Canal de envío (telegram/email)"
    )
    
    # Payload genérico
    payload = Column(
        JSON,
        nullable=False,
        comment="Contenido de la notificación (formato flexible)"
    )
    
    # Estado
    status = Column(
        String(20),
        nullable=False,
        default="pending",
        index=True,
        comment="Estado (pending/sent/failed)"
    )
    
    # Agendamiento
    scheduled_for = Column(
        DateTime(timezone=True),
        nullable=False,
        index=True,
        comment="Fecha y hora programada para envío"
    )
    
    # Fecha de envío
    sent_at = Column(
        DateTime(timezone=True),
        nullable=True,
        comment="Fecha y hora de envío efectivo"
    )
    
    # Timestamps timezone-aware
    created_at = Column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        nullable=False,
        comment="Fecha de creación del registro"
    )
    
    updated_at = Column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
        comment="Fecha de última actualización"
    )
    
    def __repr__(self):
        """Representación de la notificación."""
        return f"<NotificationQueue(id={self.id}, company_id={self.company_id}, channel={self.channel}, status={self.status}, scheduled_for={self.scheduled_for})>"
