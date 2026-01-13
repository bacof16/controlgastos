"""Company model for multi-tenant support."""

import uuid
from datetime import datetime
from sqlalchemy import Column, String, Text, Boolean, DateTime
from sqlalchemy.dialects.postgresql import UUID
from .base import Base


class Company(Base):
    """Modelo de Empresa/Compañía.
    
    Arquitectura:
    - Un solo identificador: id (UUID, primary key)
    - NO usa BaseModel
    - Timestamps tz-aware manuales
    - Todas las FK en otros modelos apuntan a companies.id
    """
    
    __tablename__ = "companies"
    
    # Identificador único UUID (primary key)
    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        comment="Identificador único UUID de la empresa"
    )
    
    # Información básica
    name = Column(
        String(255),
        nullable=False,
        comment="Nombre de la empresa"
    )
    
    tax_id = Column(
        String(50),
        unique=True,
        nullable=True,
        index=True,
        comment="RUT o identificador tributario"
    )
    
    description = Column(
        Text,
        nullable=True,
        comment="Descripción de la empresa"
    )
    
    # Estado
    is_active = Column(
        Boolean,
        default=True,
        nullable=False,
        comment="Empresa activa o desactivada"
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
        """Representación del modelo."""
        return f"<Company(id={self.id}, name={self.name}, tax_id={self.tax_id})>"
