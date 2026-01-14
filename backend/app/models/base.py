"""Base model configuration for all models."""

from datetime import datetime
from sqlalchemy import Column, Integer, DateTime
from app.database import Base
# Base declarativa para todos los modelo

class TimestampMixin:
    """Mixin para agregar timestamps automáticos a los modelos."""
    
    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
        comment="Fecha de creación del registro"
    )
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
        comment="Fecha de última actualización"
    )


class BaseModel(Base, TimestampMixin):
    """Modelo base abstracto con ID y timestamps."""
    
    __abstract__ = True
    
    id = Column(
        Integer,
        primary_key=True,
        autoincrement=True,
        comment="Identificador único"
    )
    
    def to_dict(self):
        """Convierte el modelo a diccionario."""
        return {
            column.name: getattr(self, column.name)
            for column in self.__table__.columns
        }
    
    def __repr__(self):
        """Representación del modelo."""
        return f"<{self.__class__.__name__}(id={self.id})>"
