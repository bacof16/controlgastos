"""Notification settings model for managing daily notification preferences."""

import uuid
from datetime import datetime
from sqlalchemy import Column, Boolean, String, Time, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from .base import Base


class NotificationSettings(Base):
    """Configuración de notificaciones por empresa.
    
    Arquitectura:
    - Un registro por company_id (relación 1:1)
    - Controla telegram y email
    - Hora de envío diario configurable
    """
    
    __tablename__ = "notification_settings"
    
    # Identificador único UUID (primary key)
    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        comment="Identificador único de configuración"
    )
    
    # Relación con empresa
    company_id = Column(
        UUID(as_uuid=True),
        ForeignKey("companies.id"),
        nullable=False,
        unique=True,
        comment="Empresa asociada (1:1)"
    )
    
    # Configuración Telegram
    telegram_enabled = Column(
        Boolean,
        default=False,
        nullable=False,
        comment="Notificaciones vía Telegram habilitadas"
    )
    
    telegram_chat_id = Column(
        String,
        nullable=True,
        comment="Chat ID de Telegram para envío"
    )
    
    # Configuración Email
    email_enabled = Column(
        Boolean,
        default=False,
        nullable=False,
        comment="Notificaciones vía email habilitadas"
    )
    
    email_to = Column(
        String,
        nullable=True,
        comment="Email destinatario"
    )
    
    # Configuración temporal
    daily_summary_time = Column(
        Time,
        nullable=False,
        default="08:00",
        comment="Hora diaria para envío de resumen (HH:MM)"
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
        """Representación de la configuración."""
        return f"<NotificationSettings(id={self.id}, company_id={self.company_id}, time={self.daily_summary_time})>"
