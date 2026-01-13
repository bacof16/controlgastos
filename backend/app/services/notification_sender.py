notification_sender.py  """Sender service for delivering notifications via Telegram and Email."""

import logging
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional
import requests

from app.models.notification_queue import NotificationQueue
from app.models.notification_settings import NotificationSettings
from app.services.notification_builder import format_telegram_message, format_email_html

logger = logging.getLogger(__name__)

# Variables de entorno
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
SMTP_HOST = os.getenv('SMTP_HOST', 'smtp.gmail.com')
SMTP_PORT = int(os.getenv('SMTP_PORT', '587'))
SMTP_USER = os.getenv('SMTP_USER')
SMTP_PASS = os.getenv('SMTP_PASS')
SMTP_FROM = os.getenv('SMTP_FROM', SMTP_USER)


def send_telegram(notification: NotificationQueue, settings: NotificationSettings) -> bool:
    """Envía notificación por Telegram.
    
    Args:
        notification: Registro de NotificationQueue
        settings: Configuración de notificaciones de la empresa
    
    Returns:
        True si se envió exitosamente, False en caso contrario
    """
    if not TELEGRAM_BOT_TOKEN:
        logger.error("TELEGRAM_BOT_TOKEN not configured")
        return False
    
    if not settings.telegram_chat_id:
        logger.error(f"No telegram_chat_id for company {notification.company_id}")
        return False
    
    try:
        # Formatear mensaje
        message = format_telegram_message(notification.payload)
        
        # Endpoint de Telegram Bot API
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        
        # Payload
        data = {
            "chat_id": settings.telegram_chat_id,
            "text": message,
            "parse_mode": "Markdown"
        }
        
        # Enviar request
        response = requests.post(url, json=data, timeout=10)
        response.raise_for_status()
        
        result = response.json()
        
        if result.get('ok'):
            logger.info(f"Telegram sent successfully to {settings.telegram_chat_id}")
            return True
        else:
            logger.error(f"Telegram API error: {result.get('description')}")
            return False
            
    except requests.exceptions.RequestException as e:
        logger.error(f"Error sending Telegram: {e}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error sending Telegram: {e}")
        return False


def send_email(notification: NotificationQueue, settings: NotificationSettings) -> bool:
    """Envía notificación por Email.
    
    Args:
        notification: Registro de NotificationQueue
        settings: Configuración de notificaciones de la empresa
    
    Returns:
        True si se envió exitosamente, False en caso contrario
    """
    if not all([SMTP_HOST, SMTP_USER, SMTP_PASS]):
        logger.error("SMTP settings not fully configured")
        return False
    
    if not settings.email_to:
        logger.error(f"No email_to for company {notification.company_id}")
        return False
    
    try:
        # Formatear contenido HTML
        html_content = format_email_html(notification.payload)
        
        # Crear mensaje
        msg = MIMEMultipart('alternative')
        msg['Subject'] = f"Resumen Diario - {notification.payload['summary_date']}"
        msg['From'] = SMTP_FROM
        msg['To'] = settings.email_to
        
        # Adjuntar HTML
        html_part = MIMEText(html_content, 'html', 'utf-8')
        msg.attach(html_part)
        
        # Conectar y enviar
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASS)
            server.send_message(msg)
        
        logger.info(f"Email sent successfully to {settings.email_to}")
        return True
        
    except smtplib.SMTPException as e:
        logger.error(f"SMTP error sending email: {e}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error sending email: {e}")
        return False


def send_notification(notification: NotificationQueue, settings: NotificationSettings) -> bool:
    """Envía notificación según el canal configurado.
    
    Args:
        notification: Registro de NotificationQueue
        settings: Configuración de notificaciones de la empresa
    
    Returns:
        True si se envió exitosamente, False en caso contrario
    """
    if notification.channel == 'telegram':
        return send_telegram(notification, settings)
    elif notification.channel == 'email':
        return send_email(notification, settings)
    else:
        logger.error(f"Unknown channel: {notification.channel}")
        return False
