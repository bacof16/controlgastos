"""Pydantic schemas for notification settings"""
from datetime import time
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict
from uuid import UUID


class NotificationSettingsBase(BaseModel):
    """Base schema for notification settings"""
    telegram_enabled: bool = Field(default=False, description="Enable Telegram notifications")
    telegram_chat_id: Optional[str] = Field(default=None, max_length=255, description="Telegram chat ID")
    email_enabled: bool = Field(default=False, description="Enable email notifications")
    email_to: Optional[str] = Field(default=None, max_length=255, description="Email recipient")
    daily_summary_time: Optional[time] = Field(default=None, description="Time for daily summary")


class NotificationSettingsCreate(NotificationSettingsBase):
    """Schema for creating notification settings"""
    company_id: UUID = Field(..., description="Company ID")


class NotificationSettingsUpdate(NotificationSettingsBase):
    """Schema for updating notification settings"""
    telegram_enabled: Optional[bool] = None
    email_enabled: Optional[bool] = None


class NotificationSettingsInDB(NotificationSettingsBase):
    """Schema for notification settings in database"""
    id: UUID
    company_id: UUID
    
    model_config = ConfigDict(from_attributes=True)


class NotificationSettingsResponse(NotificationSettingsInDB):
    """Schema for notification settings response"""
    pass
