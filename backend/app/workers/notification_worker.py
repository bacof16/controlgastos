"""Worker for processing notification queue and sending notifications."""

import logging
from datetime import datetime
import pytz
from sqlalchemy.orm import Session
from sqlalchemy import and_

from app.models.database import SessionLocal
from app.models.notification_queue import NotificationQueue
from app.models.notification_settings import NotificationSettings
from app.services.notification_builder import format_telegram_message, format_email_html
from app.services.notification_sender import send_telegram, send_email

logger = logging.getLogger(__name__)

# Timezone para Chile
SANTIAGO_TZ = pytz.timezone('America/Santiago')


def process_notification_queue():
    """Procesa la cola de notificaciones pendientes.
    
    Lee notification_queue donde:
    - status = 'pending'
    - scheduled_for <= now()
    
    Para cada notificación:
    - Envía según el canal (telegram/email)
    - Actualiza status a 'sent' o 'failed'
    - Registra sent_at en caso de éxito
    """
    db: Session = SessionLocal()
    
    try:
        now = datetime.now(SANTIAGO_TZ)
        
        # Obtener notificaciones pendientes
        pending_notifications = db.query(NotificationQueue).filter(
            and_(
                NotificationQueue.status == 'pending',
                NotificationQueue.scheduled_for <= now
            )
        ).all()
        
        if not pending_notifications:
            logger.debug("No pending notifications to process")
            return
        
        logger.info(f"Processing {len(pending_notifications)} pending notifications")
        
        for notification in pending_notifications:
            try:
                # Obtener configuración de la empresa
                settings = db.query(NotificationSettings).filter(
                    NotificationSettings.company_id == notification.company_id
                ).first()
                
                if not settings:
                    logger.error(f"No settings found for company {notification.company_id}")
                    notification.status = 'failed'
                    notification.error_message = "No notification settings found"
                    db.commit()
                    continue
                
                # Validar que hay payload
                if not notification.payload:
                    logger.error(f"Notification {notification.id} has no payload")
                    notification.status = 'failed'
                    notification.error_message = "No payload"
                    db.commit()
                    continue
                
                # Procesar según canal
                success = False
                
                if notification.channel == 'telegram':
                    if not settings.telegram_enabled:
                        logger.warning(f"Telegram disabled for company {notification.company_id}")
                        notification.status = 'failed'
                        notification.error_message = "Telegram disabled"
                        db.commit()
                        continue
                    
                    # Formatear mensaje
                    message_text = format_telegram_message(notification.payload)
                    
                    # Enviar
                    success = send_telegram(notification, settings)
                    
                elif notification.channel == 'email':
                    if not settings.email_enabled:
                        logger.warning(f"Email disabled for company {notification.company_id}")
                        notification.status = 'failed'
                        notification.error_message = "Email disabled"
                        db.commit()
                        continue
                    
                    # Formatear HTML
                    html_content = format_email_html(notification.payload)
                    
                    # Enviar
                    success = send_email(notification, settings)
                    
                else:
                    logger.error(f"Unknown channel: {notification.channel}")
                    notification.status = 'failed'
                    notification.error_message = f"Unknown channel: {notification.channel}"
                    db.commit()
                    continue
                
                # Actualizar status
                if success:
                    notification.status = 'sent'
                    notification.sent_at = datetime.now(SANTIAGO_TZ)
                    notification.error_message = None
                    logger.info(
                        f"Sent {notification.channel} notification "
                        f"for company {notification.company_id}"
                    )
                else:
                    notification.status = 'failed'
                    notification.error_message = "Send failed"
                    logger.error(
                        f"Failed to send {notification.channel} notification "
                        f"for company {notification.company_id}"
                    )
                
                db.commit()
                
            except Exception as e:
                logger.error(
                    f"Error processing notification {notification.id}: {e}",
                    exc_info=True
                )
                notification.status = 'failed'
                notification.error_message = str(e)[:500]  # Limitar longitud
                db.commit()
        
        logger.info(f"Finished processing {len(pending_notifications)} notifications")
        
    except Exception as e:
        logger.error(f"Error in process_notification_queue: {e}", exc_info=True)
    finally:
        db.close()


def process_failed_notifications(max_retries: int = 3):
    """Reintenta enviar notificaciones fallidas.
    
    Args:
        max_retries: Número máximo de reintentos
    """
    db: Session = SessionLocal()
    
    try:
        # Obtener notificaciones fallidas con reintentos pendientes
        failed_notifications = db.query(NotificationQueue).filter(
            and_(
                NotificationQueue.status == 'failed',
                NotificationQueue.retry_count < max_retries
            )
        ).all()
        
        if not failed_notifications:
            return
        
        logger.info(f"Retrying {len(failed_notifications)} failed notifications")
        
        for notification in failed_notifications:
            try:
                # Incrementar contador de reintentos
                notification.retry_count = (notification.retry_count or 0) + 1
                
                # Cambiar status a pending para que se procese
                notification.status = 'pending'
                notification.error_message = None
                
                db.commit()
                
                logger.info(
                    f"Retrying notification {notification.id} "
                    f"(attempt {notification.retry_count}/{max_retries})"
                )
                
            except Exception as e:
                logger.error(f"Error retrying notification {notification.id}: {e}")
                db.rollback()
        
    except Exception as e:
        logger.error(f"Error in process_failed_notifications: {e}", exc_info=True)
    finally:
        db.close()
