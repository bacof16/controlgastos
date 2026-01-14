"""Service for evaluating system alerts based on notification queue metrics."""
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
import pytz

from app.models.notification_queue import NotificationQueue

# Logger configuration
logger = logging.getLogger(__name__)

# Alert thresholds (ETAPA 5.1)
FAILED_THRESHOLD = 3
STUCK_THRESHOLD_HOURS = 1

# Timezone for Chile
SANTIAGO_TZ = pytz.timezone('America/Santiago')


def evaluate_system_alerts(db: Session) -> List[Dict[str, Any]]:
    """Evaluate notification queue and detect alert conditions.
    
    This is a PURE evaluation function:
    - NO side-effects
    - NO database writes
    - NO notifications sent
    - NO state mutation
    
    Args:
        db: SQLAlchemy database session (read-only usage)
    
    Returns:
        List of alert dictionaries, empty if no alerts detected.
        Each alert contains:
        - alert_type: Type identifier (FAILED_THRESHOLD | STUCK_QUEUE)
        - severity: Alert severity level
        - message: Human-readable alert message
        - metrics: Relevant metrics for the alert
        - detected_at: ISO timestamp of detection
    
    Examples:
        >>> alerts = evaluate_system_alerts(db)
        >>> if alerts:
        ...     for alert in alerts:
        ...         print(f"Alert: {alert['message']}")
    """
    alerts = []
    now = datetime.now(SANTIAGO_TZ)
    
    try:
        # Rule 1: Check for failed notifications threshold
        failed_count = db.query(func.count(NotificationQueue.id)).filter(
            NotificationQueue.status == "failed"
        ).scalar() or 0
        
        if failed_count >= FAILED_THRESHOLD:
            alert = {
                "alert_type": "FAILED_THRESHOLD",
                "severity": "critical",
                "message": f"{failed_count} notificaciones fallidas detectadas (umbral: {FAILED_THRESHOLD})",
                "metrics": {
                    "failed_count": failed_count,
                    "threshold": FAILED_THRESHOLD
                },
                "detected_at": now.isoformat()
            }
            alerts.append(alert)
            logger.info(
                f"Alert detected: FAILED_THRESHOLD - {failed_count} failed notifications",
                extra={
                    "alert_type": "FAILED_THRESHOLD",
                    "failed_count": failed_count,
                    "threshold": FAILED_THRESHOLD
                }
            )
        
        # Rule 2: Check for stuck pending notifications
        stuck_threshold = now - timedelta(hours=STUCK_THRESHOLD_HOURS)
        
        stuck_count = db.query(func.count(NotificationQueue.id)).filter(
            and_(
                NotificationQueue.status == "pending",
                NotificationQueue.scheduled_for <= stuck_threshold
            )
        ).scalar() or 0
        
        if stuck_count > 0:
            alert = {
                "alert_type": "STUCK_QUEUE",
                "severity": "critical",
                "message": f"{stuck_count} notificaciones pendientes sin procesar por más de {STUCK_THRESHOLD_HOURS} hora(s)",
                "metrics": {
                    "stuck_count": stuck_count,
                    "threshold_hours": STUCK_THRESHOLD_HOURS,
                    "oldest_scheduled": stuck_threshold.isoformat()
                },
                "detected_at": now.isoformat()
            }
            alerts.append(alert)
            logger.info(
                f"Alert detected: STUCK_QUEUE - {stuck_count} stuck notifications",
                extra={
                    "alert_type": "STUCK_QUEUE",
                    "stuck_count": stuck_count,
                    "threshold_hours": STUCK_THRESHOLD_HOURS
                }
            )
        
        # No alerts detected
        if not alerts:
            logger.debug(
                "System evaluation completed - No alerts detected",
                extra={
                    "failed_count": failed_count,
                    "stuck_count": stuck_count
                }
            )
        
        return alerts
    
    except Exception as e:
        logger.error(
            f"Error evaluating system alerts: {str(e)}",
            exc_info=True
        )
        # Return empty list on error to avoid breaking calling code
        return []
