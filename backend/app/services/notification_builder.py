services/notification_builder.py  """Builder service for creating notification payloads."""

import logging
from datetime import date, datetime
from typing import Optional, Dict, List
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from app.models.payment import Payment

logger = logging.getLogger(__name__)


def build_daily_summary(db: Session, company_id: str, target_date: date) -> Optional[Dict]:
    """Construye el payload del resumen diario de pagos.
    
    Args:
        db: Sesión de base de datos
        company_id: UUID de la empresa
        target_date: Fecha del resumen
    
    Returns:
        Dict con el payload o None si no hay datos
    """
    try:
        # Obtener pagos pendientes con vencimiento hoy
        pending_payments = db.query(Payment).filter(
            and_(
                Payment.company_id == company_id,
                Payment.status == 'pending',
                Payment.due_date == target_date
            )
        ).all()
        
        # Obtener pagos realizados hoy con autopago
        paid_today = db.query(Payment).filter(
            and_(
                Payment.company_id == company_id,
                Payment.status == 'paid',
                Payment.autopay == True,
                Payment.paid_at >= datetime.combine(target_date, datetime.min.time()),
                Payment.paid_at < datetime.combine(target_date, datetime.max.time())
            )
        ).all()
        
        # Si no hay datos, retornar None
        if not pending_payments and not paid_today:
            logger.info(f"No data for summary on {target_date} for company {company_id}")
            return None
        
        # Construir listas de pagos
        pending_list = [
            {
                "id": str(payment.id),
                "description": payment.description or "Sin descripción",
                "amount": float(payment.amount),
                "due_date": payment.due_date.isoformat(),
                "payment_method": payment.payment_method or "No especificado"
            }
            for payment in pending_payments
        ]
        
        paid_list = [
            {
                "id": str(payment.id),
                "description": payment.description or "Sin descripción",
                "amount": float(payment.amount),
                "paid_at": payment.paid_at.isoformat() if payment.paid_at else None,
                "payment_method": payment.payment_method or "No especificado"
            }
            for payment in paid_today
        ]
        
        # Calcular totales
        total_pending = sum(p.amount for p in pending_payments)
        total_paid = sum(p.amount for p in paid_today)
        
        # Construir payload
        payload = {
            "summary_date": target_date.isoformat(),
            "company_id": str(company_id),
            "pending_payments": {
                "count": len(pending_list),
                "total_amount": float(total_pending),
                "items": pending_list
            },
            "paid_today": {
                "count": len(paid_list),
                "total_amount": float(total_paid),
                "items": paid_list
            },
            "generated_at": datetime.utcnow().isoformat()
        }
        
        logger.info(
            f"Built summary for {company_id}: "
            f"{len(pending_list)} pending, {len(paid_list)} paid"
        )
        
        return payload
        
    except Exception as e:
        logger.error(f"Error building summary for company {company_id}: {e}")
        return None


def format_telegram_message(payload: Dict) -> str:
    """Formatea el payload para Telegram.
    
    Args:
        payload: Payload del resumen
    
    Returns:
        Mensaje formateado para Telegram
    """
    date_str = payload['summary_date']
    pending = payload['pending_payments']
    paid = payload['paid_today']
    
    message = f"📅 *Resumen Diario - {date_str}*\n\n"
    
    # Pagos pendientes
    if pending['count'] > 0:
        message += f"⌛ *Pendientes Hoy ({pending['count']})*\n"
        message += f"Total: ${pending['total_amount']:,.0f}\n\n"
        
        for item in pending['items'][:5]:  # Máximo 5
            message += f"  • {item['description']}\n"
            message += f"    ${item['amount']:,.0f} - {item['payment_method']}\n"
        
        if pending['count'] > 5:
            message += f"  ... y {pending['count'] - 5} más\n"
        
        message += "\n"
    
    # Pagos realizados
    if paid['count'] > 0:
        message += f"✅ *Pagados Hoy ({paid['count']})*\n"
        message += f"Total: ${paid['total_amount']:,.0f}\n\n"
        
        for item in paid['items'][:5]:  # Máximo 5
            message += f"  • {item['description']}\n"
            message += f"    ${item['amount']:,.0f}\n"
        
        if paid['count'] > 5:
            message += f"  ... y {paid['count'] - 5} más\n"
    
    if pending['count'] == 0 and paid['count'] == 0:
        message += "🎉 No hay actividad para hoy"
    
    return message


def format_email_html(payload: Dict) -> str:
    """Formatea el payload para Email HTML.
    
    Args:
        payload: Payload del resumen
    
    Returns:
        HTML formateado para email
    """
    date_str = payload['summary_date']
    pending = payload['pending_payments']
    paid = payload['paid_today']
    
    html = f"""
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; }}
            .header {{ background-color: #4CAF50; color: white; padding: 20px; }}
            .section {{ margin: 20px 0; }}
            .pending {{ background-color: #fff3cd; padding: 15px; border-radius: 5px; }}
            .paid {{ background-color: #d4edda; padding: 15px; border-radius: 5px; }}
            .item {{ margin: 10px 0; padding: 10px; background-color: white; border-radius: 3px; }}
            .amount {{ font-weight: bold; }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>📅 Resumen Diario - {date_str}</h1>
        </div>
    """
    
    # Pagos pendientes
    if pending['count'] > 0:
        html += f"""
        <div class="section pending">
            <h2>⌛ Pendientes Hoy ({pending['count']})</h2>
            <p class="amount">Total: ${pending['total_amount']:,.0f}</p>
        """
        
        for item in pending['items']:
            html += f"""
            <div class="item">
                <strong>{item['description']}</strong><br>
                Monto: ${item['amount']:,.0f}<br>
                Método: {item['payment_method']}
            </div>
            """
        
        html += "</div>"
    
    # Pagos realizados
    if paid['count'] > 0:
        html += f"""
        <div class="section paid">
            <h2>✅ Pagados Hoy ({paid['count']})</h2>
            <p class="amount">Total: ${paid['total_amount']:,.0f}</p>
        """
        
        for item in paid['items']:
            html += f"""
            <div class="item">
                <strong>{item['description']}</strong><br>
                Monto: ${item['amount']:,.0f}
            </div>
            """
        
        html += "</div>"
    
    if pending['count'] == 0 and paid['count'] == 0:
        html += "<p>🎉 No hay actividad para hoy</p>"
    
    html += """
    </body>
    </html>
    """
    
    return html
