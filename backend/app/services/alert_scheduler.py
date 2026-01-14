"""Alert scheduler service with anti-spam persistence for ETAPA 5.3."""
import logging
from datetime import datetime
from typing import List, Dict, Any
import pytz
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from sqlalchemy.sql import func

from app.database import SessionLocal
from app.models.alert_state import AlertState
from app.models.notification_queue import NotificationQueue
from app.services.alert_evaluator import evaluate_system_alerts

# Logger configuration
logger = logging.getLogger(__name__)

# Timezone for Chile
SANTIAGO_TZ = pytz.timezone('America/Santiago')


def run_alert_checks() -> None:
    """Main function to run alert checks with anti-spam logic.
    
    This function is called by APScheduler every 10 minutes and:
    1. Evaluates system alerts using evaluate_system_alerts()
    2. Checks alert_state to prevent spam
    3. Enqueues new alerts in notification_queue
    4. Updates alert states in database
    5. Detects resolved alerts
    
    Anti-spam rules:
    - CASE A (First time): Create alert_state, enqueue notification
    - CASE B (Active alert): Skip (no spam)
    - CASE C (Resolved): Mark as inactive
    - CASE D (Reappeared): Reactivate and enqueue
    """
    db = SessionLocal()
    try:
        logger.info("Starting alert check cycle")
        now = datetime.now(SANTIAGO_TZ)
        
        # Step 1: Evaluate system alerts using ETAPA 5.2 service
        detected_alerts = evaluate_system_alerts(db)
        
        logger.info(
            f"Evaluation completed - {len(detected_alerts)} alert(s) detected",
            extra={"alert_count": len(detected_alerts)}
        )
        
        if not detected_alerts:
            logger.debug("No alerts detected, checking for resolved alerts")
            # Check if any previously active alerts have been resolved
            _mark_resolved_alerts(db, now)
            return
        
        # Step 2: Process each detected alert with anti-spam logic
        for alert in detected_alerts:
            _process_alert(db, alert, now)
        
        # Step 3: Mark alerts that are no longer detected as resolved
        detected_types = {alert["alert_type"] for alert in detected_alerts}
        _mark_resolved_alerts(db, now, exclude_types=detected_types)
        
        db.commit()
        logger.info("Alert check cycle completed successfully")
        
    except Exception as e:
        db.rollback()
        logger.error(
            f"Error in alert check cycle: {str(e)}",
            exc_info=True
        )
    finally:
        db.close()


def _process_alert(db: Session, alert: Dict[str, Any], now: datetime) -> None:
    """Process a single alert with anti-spam logic.
    
    Args:
        db: Database session
        alert: Alert dictionary from evaluate_system_alerts()
        now: Current timestamp
    """
    alert_type = alert["alert_type"]
    
    try:
        # Try to get existing alert state
        alert_state = db.query(AlertState).filter(
            AlertState.alert_type == alert_type
        ).with_for_update().first()
        
        if not alert_state:
            # CASE A: First time - Create new alert state
            logger.info(
                f"First detection of alert: {alert_type}",
                extra={"alert_type": alert_type}
            )
            _create_new_alert(db, alert, now)
            
        elif not alert_state.is_active:
            # CASE D: Reappeared - Reactivate and enqueue
            logger.warning(
                f"Alert reappeared: {alert_type}",
                extra={
                    "alert_type": alert_type,
                    "last_resolved_at": alert_state.last_resolved_at.isoformat() if alert_state.last_resolved_at else None
                }
            )
            _reactivate_alert(db, alert_state, alert, now)
            
        else:
            # CASE B: Active alert - Skip (anti-spam)
            logger.debug(
                f"Alert still active, skipping: {alert_type}",
                extra={"alert_type": alert_type}
            )
            # Update last_triggered_at to track it's still being detected
            alert_state.last_triggered_at = now
            
    except IntegrityError as e:
        db.rollback()
        logger.error(
            f"Integrity error processing alert {alert_type}: {str(e)}"
        )
    except Exception as e:
        logger.error(
            f"Error processing alert {alert_type}: {str(e)}",
            exc_info=True
        )


def _create_new_alert(
    db: Session,
    alert: Dict[str, Any],
    now: datetime
) -> None:
    """Create new alert state and enqueue notification (CASE A).
    
    Args:
        db: Database session
        alert: Alert dictionary
        now: Current timestamp
    """
    alert_type = alert["alert_type"]
    
    # Create alert state
    alert_state = AlertState(
        alert_type=alert_type,
        is_active=True,
        last_triggered_at=now
    )
    db.add(alert_state)
    
    # Enqueue notification
    _enqueue_alert_notification(db, alert, now)
    
    logger.info(
        f"New alert created and enqueued: {alert_type}",
        extra={
            "alert_type": alert_type,
            "severity": alert.get("severity")
        }
    )


def _reactivate_alert(
    db: Session,
    alert_state: AlertState,
    alert: Dict[str, Any],
    now: datetime
) -> None:
    """Reactivate resolved alert and enqueue notification (CASE D).
    
    Args:
        db: Database session
        alert_state: Existing AlertState record
        alert: Alert dictionary
        now: Current timestamp
    """
    # Update alert state
    alert_state.is_active = True
    alert_state.last_triggered_at = now
    
    # Enqueue notification
    _enqueue_alert_notification(db, alert, now)
    
    logger.warning(
        f"Alert reactivated and enqueued: {alert_state.alert_type}",
        extra={
            "alert_type": alert_state.alert_type,
            "severity": alert.get("severity")
        }
    )


def _mark_resolved_alerts(
    db: Session,
    now: datetime,
    exclude_types: set = None
) -> None:
    """Mark previously active alerts as resolved (CASE C).
    
    Args:
        db: Database session
        now: Current timestamp
        exclude_types: Set of alert_types that are still active (should not be resolved)
    """
    if exclude_types is None:
        exclude_types = set()
    
    # Find all active alerts that are not in the detected list
    query = db.query(AlertState).filter(AlertState.is_active == True)
    
    if exclude_types:
        query = query.filter(~AlertState.alert_type.in_(exclude_types))
    
    resolved_alerts = query.all()
    
    for alert_state in resolved_alerts:
        alert_state.is_active = False
        alert_state.last_resolved_at = now
        
        logger.info(
            f"Alert resolved: {alert_state.alert_type}",
            extra={
                "alert_type": alert_state.alert_type,
                "resolved_at": now.isoformat()
            }
        )


def _enqueue_alert_notification(
    db: Session,
    alert: Dict[str, Any],
    now: datetime
) -> None:
    """Enqueue alert notification in notification_queue.
    
    Args:
        db: Database session
        alert: Alert dictionary from evaluate_system_alerts()
        now: Current timestamp
    """
    # Create payload for notification queue
    payload = {
        "type": "SYSTEM_ALERT",
        "alert_type": alert["alert_type"],
        "severity": alert["severity"],
        "message": alert["message"],
        "metrics": alert.get("metrics", {}),
        "detected_at": alert["detected_at"]
    }
    
    # Create notification queue entry
    notification = NotificationQueue(
        company_id=None,  # System alerts are not company-specific
        notification_type="system_alert",
        channel="telegram",  # Default channel for system alerts
        status="pending",
        scheduled_for=now,
        payload=payload
    )
    
    db.add(notification)
    
    logger.info(
        f"Alert notification enqueued: {alert['alert_type']}",
        extra={
            "alert_type": alert["alert_type"],
            "channel": "telegram",
            "payload": payload
        }
    )
