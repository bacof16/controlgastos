"""Pydantic schemas for notification queue"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict
from uuid import UUID


class NotificationQueueBase(BaseModel):
    """Base schema for notification queue"""
    channel: str = Field(..., max_length=50, description="Notification channel (email, telegram)")
    status: str = Field(default="pending", max_length=20, description="Notification status")
    summary_content: Optional[str] = Field(default=None, description="Summary content")


class NotificationQueueCreate(NotificationQueueBase):
    """Schema for creating notification queue entry"""
    company_id: UUID = Field(..., description="Company ID")
    notification_date: datetime = Field(default_factory=datetime.utcnow, description="Notification date")


class NotificationQueueUpdate(BaseModel):
    """Schema for updating notification queue entry"""
    status: Optional[str] = Field(None, max_length=20, description="Notification status")
    summary_content: Optional[str] = Field(None, description="Summary content")
    sent_at: Optional[datetime] = Field(None, description="Time when notification was sent")
    error_message: Optional[str] = Field(None, description="Error message if failed")


class NotificationQueueInDB(NotificationQueueBase):
    """Schema for notification queue in database"""
    id: UUID
    company_id: UUID
    notification_date: datetime
    sent_at: Optional[datetime] = None
    error_message: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class NotificationQueueResponse(NotificationQueueInDB):
    """Schema for notification queue response"""
    pass
