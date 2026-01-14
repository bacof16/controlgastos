"""APScheduler configuration for daily notification jobs."""

import logging
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
import pytz
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models.notification_settings import NotificationSettings
from app.models.notification_queue import NotificationQueue
from app.services.notification_builder import build_daily_summary
from app.services.alert_scheduler import run_alert_checks

logger = logging.getLogger(__name__)

# Timezone para Chile
SANTIAGO_TZ = pytz.timezone('America/Santiago')

# Scheduler global
scheduler = BackgroundScheduler(timezone=SANTIAGO_TZ)


def schedule_daily_summary_job(company_id: str, time_str: str):
    """Agrega un job diario para una empresa específica.
    
    Args:
        company_id: UUID de la empresa
        time_str: Hora en formato HH:MM (ej: '08:00')
    """
    hour, minute = map(int, time_str.split(':'))
    
    job_id = f"daily_summary_{company_id}"
    
    # Remover job existente si existe
    if scheduler.get_job(job_id):
        scheduler.remove_job(job_id)
    
    # Crear trigger cron para la hora específica
    trigger = CronTrigger(
        hour=hour,
        minute=minute,
        timezone=SANTIAGO_TZ
    )
    
    scheduler.add_job(
        func=generate_and_queue_summary,
        trigger=trigger,
        id=job_id,
        args=[company_id],
        replace_existing=True,
        name=f"Daily summary for company {company_id}"
    )
    
    logger.info(f"Scheduled daily summary job for company {company_id} at {time_str}")


def generate_and_queue_summary(company_id: str):
    """Genera y encola el resumen diario.
    
    Args:
        company_id: UUID de la empresa
    """
    db: Session = SessionLocal()
    
    try:
        # Obtener configuración de notificaciones
        settings = db.query(NotificationSettings).filter(
            NotificationSettings.company_id == company_id
        ).first()
        
        if not settings:
            logger.warning(f"No notification settings found for company {company_id}")
            return
        
        # Generar resumen
        today = datetime.now(SANTIAGO_TZ).date()
        summary_payload = build_daily_summary(db, company_id, today)
        
        if not summary_payload:
            logger.info(f"No data to notify for company {company_id} on {today}")
            return
        
        # Calcular hora de envío (usar la hora configurada de hoy)
        scheduled_time = datetime.combine(
            today,
            settings.daily_summary_time
        )
        scheduled_time = SANTIAGO_TZ.localize(scheduled_time)
        
        # Encolar para Telegram si está habilitado
        if settings.telegram_enabled and settings.telegram_chat_id:
            _queue_notification(
                db, 
                company_id, 
                'telegram', 
                summary_payload,
                scheduled_time
            )
        
        # Encolar para Email si está habilitado
        if settings.email_enabled and settings.email_to:
            _queue_notification(
                db, 
                company_id, 
                'email', 
                summary_payload,
                scheduled_time
            )
        
        db.commit()
        logger.info(f"Queued notifications for company {company_id}")
        
    except Exception as e:
        logger.error(f"Error generating summary for company {company_id}: {e}")
        db.rollback()
    finally:
        db.close()


def _queue_notification(db: Session, company_id: str, channel: str, payload: dict, scheduled_time: datetime):
    """Crea entrada en notification_queue evitando duplicados.
    
    Args:
        db: Sesión de base de datos
        company_id: UUID de la empresa
        channel: Canal (telegram/email)
        payload: Contenido del mensaje
        scheduled_time: Hora programada de envío
    """
    # Verificar si ya existe notificación para hoy
    existing = db.query(NotificationQueue).filter(
        NotificationQueue.company_id == company_id,
        NotificationQueue.channel == channel,
        NotificationQueue.scheduled_for == scheduled_time,
        NotificationQueue.status.in_(['pending', 'sent'])
    ).first()
    
    if existing:
        logger.info(f"Notification already queued for {company_id} on {channel}")
        return
    
    # Crear nueva notificación
    notification = NotificationQueue(
        company_id=company_id,
        channel=channel,
        payload=payload,
        scheduled_for=scheduled_time,
        status='pending'
    )
    
    db.add(notification)
    logger.info(f"Queued {channel} notification for company {company_id}")


def load_all_company_schedules():
    """Carga todos los schedules de empresas desde la BD."""
    db: Session = SessionLocal()
    
    try:
        settings_list = db.query(NotificationSettings).all()
        
        for settings in settings_list:
            if settings.telegram_enabled or settings.email_enabled:
                time_str = settings.daily_summary_time.strftime('%H:%M')
                schedule_daily_summary_job(
                    str(settings.company_id),
                    time_str
                )
        
        logger.info(f"Loaded {len(settings_list)} company schedules")
        
    except Exception as e:
        logger.error(f"Error loading company schedules: {e}")
    finally:
        db.close()


def start_scheduler():
    """Inicia el scheduler y carga los jobs."""
    if not scheduler.running:
        scheduler.start()
        logger.info("APScheduler started")
        
        # Cargar schedules de empresas
        load_all_company_schedules()

    # Registrar job de monitoreo de alertas cada 10 minutos
    scheduler.add_job(
                func=run_alert_checks,
                trigger='interval',
                minutes=10,
                id='alert_monitoring',
                replace_existing=True,
                name='System alerts monitoring'
            )
    logger.info("Alert monitoring job registered (every 10 minutes)")


def shutdown_scheduler():
    """Detiene el scheduler."""
    if scheduler.running:
        scheduler.shutdown()
        logger.info("APScheduler shut down")
