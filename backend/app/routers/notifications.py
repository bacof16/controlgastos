"""API router for notification endpoints"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from app.models.database import get_db
from app.models.notification_settings import NotificationSettings
from app.models.notification_queue import NotificationQueue
from app.schemas.notification_settings import (
    NotificationSettingsCreate,
    NotificationSettingsUpdate,
    NotificationSettingsResponse,
)
from app.schemas.notification_queue import (
    NotificationQueueCreate,
    NotificationQueueUpdate,
    NotificationQueueResponse,
)

router = APIRouter(
    prefix="/notifications",
    tags=["notifications"],
)


# Notification Settings Endpoints

@router.post(
    "/settings",
    response_model=NotificationSettingsResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create notification settings",
)
def create_notification_settings(
    settings: NotificationSettingsCreate,
    db: Session = Depends(get_db),
):
    """Create new notification settings for a company."""
    db_settings = NotificationSettings(**settings.model_dump())
    db.add(db_settings)
    db.commit()
    db.refresh(db_settings)
    return db_settings


@router.get(
    "/settings/company/{company_id}",
    response_model=NotificationSettingsResponse,
    summary="Get notification settings by company",
)
def get_notification_settings_by_company(
    company_id: UUID,
    db: Session = Depends(get_db),
):
    """Get notification settings for a specific company."""
    settings = db.query(NotificationSettings).filter(
        NotificationSettings.company_id == company_id
    ).first()
    
    if not settings:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification settings not found for this company",
        )
    
    return settings


@router.patch(
    "/settings/{settings_id}",
    response_model=NotificationSettingsResponse,
    summary="Update notification settings",
)
def update_notification_settings(
    settings_id: UUID,
    settings_update: NotificationSettingsUpdate,
    db: Session = Depends(get_db),
):
    """Update notification settings."""
    db_settings = db.query(NotificationSettings).filter(
        NotificationSettings.id == settings_id
    ).first()
    
    if not db_settings:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification settings not found",
        )
    
    # Update only provided fields
    update_data = settings_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_settings, field, value)
    
    db.commit()
    db.refresh(db_settings)
    return db_settings


# Notification Queue Endpoints

@router.post(
    "/queue",
    response_model=NotificationQueueResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create notification queue entry",
)
def create_notification_queue(
    queue: NotificationQueueCreate,
    db: Session = Depends(get_db),
):
    """Create a new notification queue entry."""
    db_queue = NotificationQueue(**queue.model_dump())
    db.add(db_queue)
    db.commit()
    db.refresh(db_queue)
    return db_queue


@router.get(
    "/queue/company/{company_id}",
    response_model=List[NotificationQueueResponse],
    summary="Get notification queue by company",
)
def get_notification_queue_by_company(
    company_id: UUID,
    db: Session = Depends(get_db),
):
    """Get all notification queue entries for a company."""
    queue_entries = db.query(NotificationQueue).filter(
        NotificationQueue.company_id == company_id
    ).all()
    
    return queue_entries


@router.patch(
    "/queue/{queue_id}",
    response_model=NotificationQueueResponse,
    summary="Update notification queue entry",
)
def update_notification_queue(
    queue_id: UUID,
    queue_update: NotificationQueueUpdate,
    db: Session = Depends(get_db),
):
    """Update a notification queue entry."""
    db_queue = db.query(NotificationQueue).filter(
        NotificationQueue.id == queue_id
    ).first()
    
    if not db_queue:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification queue entry not found",
        )
    
    # Update only provided fields
    update_data = queue_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_queue, field, value)
    
    db.commit()
    db.refresh(db_queue)
    return db_queue


# Worker Endpoint

@router.post(
    "/process",
    status_code=status.HTTP_200_OK,
    summary="Process notification queue",
)
def process_notifications():
    """Manually trigger processing of notification queue."""
    from app.workers.notification_worker import process_notification_queue
    
    process_notification_queue()
    
    return {
        "status": "ok",
        "message": "Notification queue processed"
    }


# List Queue Endpoint

@router.get(
    "/queue",
    response_model=List[NotificationQueueResponse],
    summary="List notification queue with filters",
)
def list_notification_queue(
    company_id: UUID = None,
    status: str = None,
    limit: int = 50,
    offset: int = 0,
    db: Session = Depends(get_db),
):
    """List notification queue entries with optional filters.
    
    Args:
        company_id: Filter by company UUID (optional)
        status: Filter by status: pending, sent, or failed (optional)
        limit: Maximum number of results (default 50, max 100)
        offset: Offset for pagination (default 0)
    
    Returns:
        List of notification queue entries ordered by scheduled_for DESC
    """
    # Enforce max limit
    if limit > 100:
        limit = 100
    
    # Build query
    query = db.query(NotificationQueue)
    
    # Apply filters if provided
    if company_id:
        query = query.filter(NotificationQueue.company_id == company_id)
    
    if status:
        query = query.filter(NotificationQueue.status == status)
    
    # Order by scheduled_for descending
    query = query.order_by(NotificationQueue.scheduled_for.desc())
    
    # Apply pagination
    queue_entries = query.offset(offset).limit(limit).all()
    
    return queue_entries

# Retry Failed Notification Endpoint
@router.post(
    "/queue/{queue_id}/retry",
    status_code=status.HTTP_200_OK,
    summary="Retry failed notification",
)
def retry_failed_notification(
    queue_id: UUID,
    db: Session = Depends(get_db),
):
    """Retry a failed notification by resetting it to pending status.
    
    Args:
        queue_id: UUID of the notification to retry
    
    Returns:
        Success message confirming the notification was queued for retry
    
    Raises:
        HTTPException 404: If notification not found
        HTTPException 400: If notification status is not 'failed'
    """
    # Find the notification
    db_queue = db.query(NotificationQueue).filter(
        NotificationQueue.id == queue_id
    ).first()
    
    if not db_queue:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found",
        )
    
    # Check if status is failed
    if db_queue.status != "failed":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot retry notification with status '{db_queue.status}'. Only 'failed' notifications can be retried.",
        )
    
    # Reset to pending for retry
    db_queue.status = "pending"
    db_queue.sent_at = None
    # Keep payload intact - do not modify
    
    db.commit()
    db.refresh(db_queue)
    
    return {
        "status": "ok",
        "message": "Notification queued for retry"
    }
