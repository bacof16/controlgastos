"""AlertState model for tracking system alert states."""
from sqlalchemy import Column, String, Boolean, DateTime, Index
from sqlalchemy.sql import func
from app.models.base import BaseModel


class AlertState(BaseModel):
    """Model to track alert states for anti-spam persistence.
    
    This model ensures that:
    - Each alert_type has at most ONE record (UNIQUE constraint)
    - Active alerts are not re-sent (anti-spam)
    - Resolved alerts can be reactivated when they reappear
    - Full audit trail with timestamps
    
    Attributes:
        alert_type (str): Unique identifier for the alert type
                         (e.g., 'FAILED_THRESHOLD', 'STUCK_QUEUE')
        is_active (bool): True if alert is currently active
        last_triggered_at (datetime): When the alert was last detected
        last_resolved_at (datetime): When the alert was last resolved
    """
    
    __tablename__ = "alert_state"
    
    # Alert type identifier - MUST be unique
    alert_type = Column(
        String(50),
        unique=True,
        nullable=False,
        index=True,  # Indexed for fast lookups
        comment="Unique alert type identifier (e.g., FAILED_THRESHOLD)"
    )
    
    # Current state of the alert
    is_active = Column(
        Boolean,
        default=False,
        nullable=False,
        comment="True if alert is currently active, False if resolved"
    )
    
    # Timestamp when alert was last triggered/detected
    last_triggered_at = Column(
        DateTime(timezone=True),
        nullable=True,
        comment="Timestamp when alert was last detected"
    )
    
    # Timestamp when alert was last resolved
    last_resolved_at = Column(
        DateTime(timezone=True),
        nullable=True,
        comment="Timestamp when alert was last resolved"
    )
    
    # Add index for quick lookups by alert_type
    __table_args__ = (
        Index('idx_alert_state_alert_type', 'alert_type', unique=True),
        {'comment': 'Stores alert states for anti-spam and reactivation logic'}
    )
    
    def __repr__(self):
        return (
            f"<AlertState("
            f"id={self.id}, "
            f"alert_type='{self.alert_type}', "
            f"is_active={self.is_active}, "
            f"last_triggered_at={self.last_triggered_at}"
            f")>"
        )
    
    def activate(self):
        """Mark alert as active and update triggered timestamp."""
        self.is_active = True
        self.last_triggered_at = func.now()
    
    def resolve(self):
        """Mark alert as resolved and update resolved timestamp."""
        self.is_active = False
        self.last_resolved_at = func.now()
