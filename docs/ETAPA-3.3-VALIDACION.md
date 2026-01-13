# ETAPA 3.3 - VALIDACIÓN

## Endpoint de Reintento de Notificaciones Fallidas

### ✅ Estado: COMPLETADO

---

## Objetivo

Implementar un endpoint REST que permita reenviar manualmente una notificación fallida mediante el reseteo de su estado a "pending" para que sea procesada posteriormente por el worker automático.

---

## Endpoint Implementado

### POST `/api/notifications/queue/{queue_id}/retry`

**Archivo:** `backend/app/routers/notifications.py`

**Líneas:** 235-286

---

## Especificaciones Técnicas

### Decorador
```python
@router.post(
    "/queue/{queue_id}/retry",
    status_code=status.HTTP_200_OK,
    summary="Retry failed notification",
)
```

### Parámetros
- **queue_id** (UUID): ID de la notificación a reintentar - Path parameter
- **db** (Session): Sesión de base de datos - Dependency injection

### Función
```python
def retry_failed_notification(
    queue_id: UUID,
    db: Session = Depends(get_db),
):
```

---

## Lógica Implementada

### 1. ✅ Búsqueda de Notificación
```python
db_queue = db.query(NotificationQueue).filter(
    NotificationQueue.id == queue_id
).first()
```

### 2. ✅ Validación de Existencia
```python
if not db_queue:
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Notification not found",
    )
```
**Respuesta:** HTTP 404 si no existe la notificación

### 3. ✅ Validación de Estado
```python
if db_queue.status != "failed":
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail=f"Cannot retry notification with status '{db_queue.status}'. Only 'failed' notifications can be retried.",
    )
```
**Respuesta:** HTTP 400 si el estado no es "failed"

### 4. ✅ Reseteo a Pending
```python
# Reset to pending for retry
db_queue.status = "pending"
db_queue.sent_at = None
# Keep payload intact - do not modify

db.commit()
db.refresh(db_queue)
```

**Acciones:**
- Cambia `status` de "failed" a "pending"
- Limpia `sent_at` (set a `None`)
- **NO modifica** el campo `payload`
- **NO modifica** `error_message` (mantiene historial)

### 5. ✅ Respuesta Exitosa
```python
return {
    "status": "ok",
    "message": "Notification queued for retry"
}
```
**Respuesta:** HTTP 200 con mensaje de confirmación

---

## Validaciones Implementadas

### ✅ HTTP 404 - Not Found
- **Condición:** Notificación con `queue_id` no existe
- **Mensaje:** "Notification not found"

### ✅ HTTP 400 - Bad Request
- **Condición:** Status != "failed"
- **Mensaje:** "Cannot retry notification with status '{status}'. Only 'failed' notifications can be retried."

### ✅ HTTP 200 - OK
- **Condición:** Reintento exitoso
- **Respuesta:**
  ```json
  {
    "status": "ok",
    "message": "Notification queued for retry"
  }
  ```

---

## Comportamiento y Reglas

### ✅ NO Ejecuta Procesamiento Inmediato
- **NO** llama a `process_notification_queue()`
- **NO** envía la notificación directamente
- Solo resetea el estado a "pending"

### ✅ Worker Procesará Posteriormente
- El scheduler automático (09:00 AM diario) procesará la notificación
- Puede procesarse manualmente via POST `/api/notifications/process`

### ✅ Payload Intacto
- **NO** modifica el campo `payload`
- Mantiene exactamente los mismos datos de envío

### ✅ Sin Cambios en Base de Datos
- **NO** se agregaron columnas nuevas
- **NO** se crearon migraciones
- Usa la estructura existente de `notification_queue`

### ✅ Error Message Preservado
- **NO** limpia `error_message`
- Mantiene el registro del error anterior para auditoría

---
## Ejemplos de Uso

### Ejemplo 1: Reintento Exitoso
```bash
curl -X POST http://localhost:8000/api/notifications/queue/123e4567-e89b-12d3-a456-426614174000/retry
```

**Respuesta (200 OK):**
```json
{
  "status": "ok",
  "message": "Notification queued for retry"
}
```

### Ejemplo 2: Notificación No Encontrada
```bash
curl -X POST http://localhost:8000/api/notifications/queue/00000000-0000-0000-0000-000000000000/retry
```

**Respuesta (404 Not Found):**
```json
{
  "detail": "Notification not found"
}
```

### Ejemplo 3: Estado Inválido
```bash
# Intentar reintentar una notificación con status="pending"
curl -X POST http://localhost:8000/api/notifications/queue/123e4567-e89b-12d3-a456-426614174001/retry
```

**Respuesta (400 Bad Request):**
```json
{
  "detail": "Cannot retry notification with status 'pending'. Only 'failed' notifications can be retried."
}
```

---

## Integración con Sistema Existente

### ✅ Router Registrado
- Endpoint ya incluido en `/api/notifications` prefix
- No requiere cambios en `main.py`

### ✅ Compatible con Worker
- El worker `process_notification_queue()` ya existe
- Procesará automáticamente las notificaciones con status="pending"

### ✅ Compatible con Scheduler
- El scheduler diario ejecutará el worker
- Las notificaciones reintenntadas serán procesadas en el próximo ciclo

---

## Tests de Validación

### Test 1: Verificar Endpoint Existe
```bash
curl -X OPTIONS http://localhost:8000/api/notifications/queue/123e4567-e89b-12d3-a456-426614174000/retry
```
**Esperado:** Endpoint disponible

### Test 2: Simular Notificación Fallida
```python
# Crear notificación de prueba con status="failed"
POST /api/notifications/queue
{
  "company_id": "uuid-test",
  "notification_type": "test",
  "channel": "email",
  "status": "failed",
  "scheduled_for": "2026-01-13T10:00:00Z",
  "payload": {"to": "test@example.com"}
}
```

### Test 3: Ejecutar Retry
```bash
POST /api/notifications/queue/{id_obtenido}/retry
```
**Esperado:** Status cambia a "pending", sent_at se limpia

### Test 4: Verificar en Base de Datos
```sql
SELECT id, status, sent_at, error_message, payload 
FROM notification_queue 
WHERE id = 'uuid-test';
```
**Esperado:**
- `status` = "pending"
- `sent_at` = NULL
- `payload` sin cambios
- `error_message` preservado

---

## Cumplimiento de Requisitos

### ✅ Funcionales
- [x] Endpoint POST `/queue/{queue_id}/retry` creado
- [x] Parámetro `queue_id` como UUID en path
- [x] Busca notificación por ID
- [x] HTTP 404 si no existe
- [x] HTTP 400 si status != "failed"
- [x] Resetea status a "pending"
- [x] Limpia `sent_at` (None)
- [x] Mantiene `payload` intacto
- [x] Retorna mensaje de confirmación

### ✅ Restricciones
- [x] NO ejecuta `process_notification_queue()`
- [x] NO envía notificaciones directamente
- [x] NO modifica payload
- [x] NO agrega reintentos automáticos
- [x] NO agrega columnas nuevas
- [x] NO crea migraciones

### ✅ Validaciones
- [x] HTTP 200 en caso correcto
- [x] No falla si cola está vacía
- [x] Worker procesará luego el reenvío

---

## Documentación del Endpoint

La documentación automática estará disponible en:
- **Swagger UI:** `http://localhost:8000/docs`
- **ReDoc:** `http://localhost:8000/redoc`

### Información Visible:
- Summary: "Retry failed notification"
- Method: POST
- Path: `/api/notifications/queue/{queue_id}/retry`
- Responses: 200, 400, 404

---

## Conclusión

### ✅ ETAPA 3.3 COMPLETADA AL 100%

El endpoint de reintento de notificaciones fallidas ha sido implementado exitosamente cumpliendo todos los requisitos:

1. ✅ **Funcionalidad Core:** Resetea notificaciones fallidas a pending
2. ✅ **Validaciones:** HTTP 404 y 400 implementadas correctamente
3. ✅ **Integridad de Datos:** Payload se mantiene intacto
4. ✅ **Sin Efectos Secundarios:** No ejecuta procesamiento inmediato
5. ✅ **Sin Cambios Estructurales:** No requiere migraciones
6. ✅ **Integración:** Compatible con sistema existente

**Sistema listo para uso en producción** con capacidad de:
- Reintentar manualmente notificaciones fallidas
- Mantener auditoría de errores previos
- Delegar procesamiento al worker existente
- Validar estados correctamente
- Manejar errores de forma robusta

---

**Fecha de Implementación:** 2026-01-13
**Commit:** 00fc863d0a4af34fefcc57e2e7783972bbe7f59d
**Archivo Modificado:** `backend/app/routers/notifications.py`
**Líneas Agregadas:** 52 (235-286)
**Tamaño Total Archivo:** 286 líneas (236 loc) · 7.62 KB
