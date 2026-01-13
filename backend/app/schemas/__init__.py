"""Schemas package for controlgastos API"""

from app.schemas.notification_settings import (
    NotificationSettingsBase,
    NotificationSettingsCreate,
    NotificationSettingsUpdate,
    NotificationSettingsInDB,
    NotificationSettingsResponse,
)
from app.schemas.notification_queue import (
    NotificationQueueBase,
    NotificationQueueCreate,
    NotificationQueueUpdate,
    NotificationQueueInDB,
    NotificationQueueResponse,
)

__all__ = [
    # Notification Settings
    "NotificationSettingsBase",
    "NotificationSettingsCreate",
    "NotificationSettingsUpdate",
    "NotificationSettingsInDB",
    "NotificationSettingsResponse",
    # Notification Queue
    "NotificationQueueBase",
    "NotificationQueueCreate",
    "NotificationQueueUpdate",
    "NotificationQueueInDB",
    "NotificationQueueResponse",
]
