# ETAPA 5.2 - VALIDACIÓN

## Servicio de Evaluación de Alertas del Sistema

### ✅ Estado: COMPLETADO

## Objetivo

Crear un servicio puro de evaluación que analice las métricas de la cola de notificaciones y detecte condiciones de alerta, sin efectos secundarios (sin escribir en BD, sin enviar notificaciones).

## Servicio Implementado

**Archivo:** `backend/app/services/alert_evaluator.py`

**Función:** `evaluate_system_alerts(db: Session) -> List[Dict[str, Any]]`

## Especificaciones Técnicas

### Función Principal

```python
def evaluate_system_alerts(db: Session) -> List[Dict[str, Any]]:
    """Evaluate notification queue and detect alert conditions."""
```

### Parámetros

- **db** (Session): Sesión de SQLAlchemy para consultas de solo lectura

### Retorno

Lista de diccionarios de alerta. Cada alerta contiene:

```python
{
    "alert_type": str,      # FAILED_THRESHOLD | STUCK_QUEUE
    "severity": str,        # "critical"
    "message": str,         # Mensaje legible
    "metrics": Dict,        # Métricas relevantes
    "detected_at": str      # Timestamp ISO 8601
}
```

## Umbrales de Alerta (ETAPA 5.1)

### Constantes Configuradas

```python
FAILED_THRESHOLD = 3              # Notificaciones fallidas
STUCK_THRESHOLD_HOURS = 1         # Horas para considerar "stuck"
SANTIAGO_TZ = pytz.timezone('America/Santiago')
```

## Reglas de Evaluación Implementadas

### ✅ Regla 1: Umbral de Notificaciones Fallidas

**Condición:**
```python
failed_count >= FAILED_THRESHOLD
```

**Query:**
```python
failed_count = db.query(func.count(NotificationQueue.id)).filter(
    NotificationQueue.status == "failed"
).scalar() or 0
```

**Alerta Generada:**
```python
{
    "alert_type": "FAILED_THRESHOLD",
    "severity": "critical",
    "message": "{failed_count} notificaciones fallidas detectadas (umbral: {FAILED_THRESHOLD})",
    "metrics": {
        "failed_count": failed_count,
        "threshold": FAILED_THRESHOLD
    },
    "detected_at": now.isoformat()
}
```

### ✅ Regla 2: Notificaciones Pendientes Atascadas

**Condición:**
```python
stuck_count > 0
```

Donde stuck son notificaciones:
- Con `status == "pending"`
- Con `scheduled_for <= (now - STUCK_THRESHOLD_HOURS)`

**Query:**
```python
stuck_threshold = now - timedelta(hours=STUCK_THRESHOLD_HOURS)

stuck_count = db.query(func.count(NotificationQueue.id)).filter(
    and_(
        NotificationQueue.status == "pending",
        NotificationQueue.scheduled_for <= stuck_threshold
    )
).scalar() or 0
```

**Alerta Generada:**
```python
{
    "alert_type": "STUCK_QUEUE",
    "severity": "critical",
    "message": "{stuck_count} notificaciones pendientes sin procesar por más de {STUCK_THRESHOLD_HOURS} hora(s)",
    "metrics": {
        "stuck_count": stuck_count,
        "threshold_hours": STUCK_THRESHOLD_HOURS,
        "oldest_scheduled": stuck_threshold.isoformat()
    },
    "detected_at": now.isoformat()
}
```

## Características del Servicio

### ✅ Función Pura (Sin Efectos Secundarios)

- **NO** escribe en base de datos
- **NO** envía notificaciones
- **NO** modifica estado del sistema
- **NO** tiene side-effects
- Solo **LEE** y **EVALÚA**

### ✅ Logging Estructurado

```python
logger = logging.getLogger(__name__)
```

**Logs Informativos:**
- Alert detected (con extra data)
- System evaluation completed

**Logs de Error:**
- Error evaluating system alerts (con exc_info)

### ✅ Manejo de Errores Robusto

```python
try:
    # Evaluation logic
except Exception as e:
    logger.error(
        f"Error evaluating system alerts: {str(e)}",
        exc_info=True
    )
    return []  # Empty list on error
```

- Retorna lista vacía `[]` en caso de error
- No propaga excepciones
- Log completo con stack trace

### ✅ Timezone Aware

```python
SANTIAGO_TZ = pytz.timezone('America/Santiago')
now = datetime.now(SANTIAGO_TZ)
```

- Usa timezone de Chile (America/Santiago)
- Timestamps en formato ISO 8601

## Validaciones Implementadas

### ✅ Retorno Vacío Cuando No Hay Alertas

```python
if not alerts:
    logger.debug(
        "System evaluation completed - No alerts detected",
        extra={
            "failed_count": failed_count,
            "stuck_count": stuck_count
        }
    )
```

### ✅ Scalar Safety

```python
.scalar() or 0  # Previene None, retorna 0
```

### ✅ Multiple Alerts Support

Puede retornar múltiples alertas simultáneamente:
- FAILED_THRESHOLD
- STUCK_QUEUE
- Ambas si aplican

## Ejemplos de Uso

### Ejemplo 1: Sistema Saludable

**Estado:**
- 0 notificaciones fallidas
- 0 notificaciones atascadas

**Resultado:**
```python
alerts = evaluate_system_alerts(db)
# alerts = []
```

### Ejemplo 2: Umbral de Fallidas Excedido

**Estado:**
- 5 notificaciones con status="failed"
- 0 notificaciones atascadas

**Resultado:**
```python
alerts = evaluate_system_alerts(db)
# alerts = [
#     {
#         "alert_type": "FAILED_THRESHOLD",
#         "severity": "critical",
#         "message": "5 notificaciones fallidas detectadas (umbral: 3)",
#         "metrics": {"failed_count": 5, "threshold": 3},
#         "detected_at": "2026-01-13T22:00:00-03:00"
#     }
# ]
```

### Ejemplo 3: Notificaciones Atascadas

**Estado:**
- 2 notificaciones con status="pending"
- scheduled_for hace 2 horas

**Resultado:**
```python
alerts = evaluate_system_alerts(db)
# alerts = [
#     {
#         "alert_type": "STUCK_QUEUE",
#         "severity": "critical",
#         "message": "2 notificaciones pendientes sin procesar por más de 1 hora(s)",
#         "metrics": {
#             "stuck_count": 2,
#             "threshold_hours": 1,
#             "oldest_scheduled": "2026-01-13T21:00:00-03:00"
#         },
#         "detected_at": "2026-01-13T22:00:00-03:00"
#     }
# ]
```

### Ejemplo 4: Múltiples Alertas Simultáneas

**Estado:**
- 4 notificaciones fallidas
- 3 notificaciones atascadas

**Resultado:**
```python
alerts = evaluate_system_alerts(db)
# alerts = [
#     {"alert_type": "FAILED_THRESHOLD", ...},
#     {"alert_type": "STUCK_QUEUE", ...}
# ]
```

## Cumplimiento de Requisitos

### ✅ Funcionales

- [x] Función `evaluate_system_alerts(db)` creada
- [x] Parámetro `db: Session` para consultas
- [x] Retorna `List[Dict[str, Any]]`
- [x] Detecta umbral de fallidas (>= 3)
- [x] Detecta notificaciones atascadas (> 1 hora)
- [x] Retorna lista vacía si no hay alertas
- [x] Estructura de alerta con todos los campos
- [x] Timestamps en formato ISO 8601
- [x] Timezone de Chile (America/Santiago)

### ✅ Restricciones (Función Pura)

- [x] NO escribe en base de datos
- [x] NO envía notificaciones
- [x] NO modifica estado
- [x] Solo consultas SELECT
- [x] Sin efectos secundarios

### ✅ Calidad de Código

- [x] Docstring completo con ejemplos
- [x] Type hints en función
- [x] Logging estructurado
- [x] Manejo de errores robusto
- [x] Retorna [] en caso de error
- [x] Constantes configurables
- [x] Código limpio y legible

### ✅ Testing y Validación

- [x] Función importable desde `app.services.alert_evaluator`
- [x] Query de fallidas funcional
- [x] Query de atascadas funcional
- [x] Lógica de umbrales correcta
- [x] Formato de alerta correcto

## Integración con Sistema Existente

### ✅ Imports Requeridos

```python
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
import pytz
from app.models.notification_queue import NotificationQueue
```

### ✅ Sin Dependencias Adicionales

- Usa librerías ya instaladas
- No requiere nuevos paquetes
- Compatible con estructura existente

### ✅ Preparado para Integración Futura

Este servicio será utilizado por:
- Worker de monitoreo (ETAPA 5.3)
- Endpoint de salud (ETAPA 5.4)
- Sistema de alertas automático

## Documentación del Código

### Docstring Completo

```python
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
```

## Conclusión

### ✅ ETAPA 5.2 COMPLETADA AL 100%

El servicio de evaluación de alertas ha sido implementado exitosamente cumpliendo todos los requisitos:

1. ✅ **Función Pura:** Sin efectos secundarios, solo lectura y evaluación
2. ✅ **Reglas de Alerta:** Implementadas ambas reglas (fallidas y atascadas)
3. ✅ **Umbrales Configurables:** Constantes fáciles de ajustar
4. ✅ **Logging Estructurado:** Información clara para debugging
5. ✅ **Manejo de Errores:** Robusto y no propaga excepciones
6. ✅ **Timezone Aware:** Uso correcto de timezone de Chile
7. ✅ **Type Hints:** Código bien tipado y documentado
8. ✅ **Sin Dependencias Nuevas:** Compatible con entorno actual

**Sistema listo** para ser integrado en el worker de monitoreo (ETAPA 5.3) y endpoint de salud (ETAPA 5.4).

**Fecha de Implementación:** 2026-01-13  
**Commit:** 310a77e  
**Archivo Creado:** `backend/app/services/alert_evaluator.py`  
**Líneas:** 129 (111 loc) · 4.33 KB
