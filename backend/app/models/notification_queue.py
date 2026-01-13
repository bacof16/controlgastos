"""Notification queue model for daily notification tracking."""

import uuid
from datetime import datetime, date
from sqlalchemy import Column, String, Date, Boolean, Text, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from .base import Base


class NotificationQueue(Base):
    """Cola de notificaciones diarias agrupadas.
    
    Arquitectura:
    - Un registro por (company_id, notification_date, channel)
    - Agrupa múltiples eventos del día
    - Estado de envío (pending/sent/failed)
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
    
    # Información de la notificación
    notification_date = Column(
        Date,
        nullable=False,
        index=True,
        default=date.today,
        comment="Fecha del resumen diario"
    )
    
    channel = Column(
        String(50),
        nullable=False,
        comment="Canal de envío (telegram/email)"
    )
    
    status = Column(
        String(20),
        nullable=False,
        default="pending",
        comment="Estado (pending/sent/failed)"
    )
    
    summary_content = Column(
        Text,
        nullable=True,
        comment="Contenido del resumen agrupado (JSON o texto)"
    )
    
    sent_at = Column(
        DateTime(timezone=True),
        nullable=True,
        comment="Fecha y hora de envío efectivo"
    )
    
    error_message = Column(
        Text,
        nullable=True,
        comment="Mensaje de error si falla el envío"
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
        return f"<NotificationQueue(id={self.id}, company_id={self.company_id}, date={self.notification_date}, channel={self.channel}, status={self.status})>"
