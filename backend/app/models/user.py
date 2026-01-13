"""User model for authentication and user management."""

import uuid
from datetime import datetime
from sqlalchemy import Column, String, Boolean, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from .base import Base


class User(Base):
    """Modelo de Usuario para autenticación y gestión de usuarios."""
    
    __tablename__ = "users"
    
    # Identificador UUID
    id = Column(
        UUID(as_uuid=True),
        default=uuid.uuid4,
        primary_key=True,     
        index=True,
        comment="Identificador único UUID del usuario"
    )
    
    # Información básica
    email = Column(
        String(255),
        unique=True,
        nullable=False,
        index=True,
        comment="Email del usuario (usado para login)"
    )
    
    full_name = Column(
        String(255),
        nullable=False,
        comment="Nombre completo del usuario"
    )
    
    # Autenticación (campos preparados para futuro)
    password_hash = Column(
        String(255),
        nullable=True,
        comment="Hash de contraseña (implementación futura)"
    )
    
    # Estado del usuario
    is_active = Column(
        Boolean,
        default=True,
        nullable=False,
        comment="Usuario activo o desactivado"
    )
    
    is_superuser = Column(
        Boolean,
        default=False,
        nullable=False,
        comment="Usuario administrador del sistema"
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
    
    # Relaciones
    # company_users = relationship("CompanyUser", back_populates="user")
    # audit_logs = relationship("AuditLog", back_populates="user")
    
    def __repr__(self):
        """Representación del usuario."""
        return f"<User(id={self.id}, email={self.email}, full_name={self.full_name})>"
    
    def to_dict(self):
        """Convierte el modelo a diccionario (sin contraseña)."""
        data = super().to_dict()
        # Excluir campo sensible
        data.pop('password_hash', None)
        return data
