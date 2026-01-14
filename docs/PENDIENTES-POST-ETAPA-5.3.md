# TAREAS PENDIENTES POST-ETAPA 5.3

## Estado General

**Fecha:** 2026-01-13  
**Contexto:** ETAPA 5.3 implementada y corregida (scheduler startup hooks)  
**Próximos pasos:** Completar incidencias pendientes para deployment en producción

---

## ⏸️ INCIDENCIA 2 - Ejecutar Migración Alembic

### Estado: PENDIENTE

### Objetivo
Ejecutar la migración `003_create_alert_state_table.py` para crear la tabla `alert_state` en la base de datos de producción.

### Archivo de Migración
- **Ubicación:** `backend/alembic/versions/003_create_alert_state_table.py`
- **Creado:** 2026-01-13
- **Propósito:** Crear tabla para anti-spam persistente de alertas

### Pasos para Ejecutar

#### Opción 1: Desde contenedor Docker (Producción)

```bash
# 1. Acceder al contenedor del backend
docker exec -it controlgastos-api bash

# 2. Ejecutar migración
alembic upgrade head

# 3. Verificar que la migración se aplicó
alembic current

# Salida esperada:
# INFO  [alembic.runtime.migration] Context impl PostgreSQLImpl.
# INFO  [alembic.runtime.migration] Will assume transactional DDL.
# INFO  [alembic.runtime.migration] Running upgrade 002 -> 003, create alert_state table
```

#### Opción 2: Desde entorno local

```bash
# 1. Navegar a carpeta backend
cd backend

# 2. Activar entorno virtual (si aplica)
source venv/bin/activate

# 3. Ejecutar migración
alembic upgrade head
```

### Validación Post-Migración

```sql
-- Conectar a PostgreSQL y verificar tabla
\dt alert_state

-- Verificar estructura
\d alert_state

-- Salida esperada:
Table "public.alert_state"
Column            | Type                     | Nullable | Default
------------------+--------------------------+----------+---------
id                | uuid                     | not null | gen_random_uuid()
alert_type        | character varying(100)   | not null |
is_active         | boolean                  | not null | false
last_triggered_at | timestamp with time zone |
last_resolved_at  | timestamp with time zone |
created_at        | timestamp with time zone | not null | CURRENT_TIMESTAMP
updated_at        | timestamp with time zone | not null | CURRENT_TIMESTAMP
```

### Criterios de Aceptación

- [x] Migración 003 existe en `alembic/versions/`
- [ ] Migración ejecutada en base de datos
- [ ] Tabla `alert_state` creada correctamente
- [ ] Constraint UNIQUE en `alert_type` aplicado
- [ ] Índices creados
- [ ] Sin errores en logs

---

## ⏸️ INCIDENCIA 3 - Validar company_id=None en Workers

### Estado: PENDIENTE

### Objetivo
Validar que el sistema maneja correctamente notificaciones de alertas del sistema (company_id=None) sin causar errores en los workers.

### Contexto
Las alertas del sistema (DISK_USAGE, MEMORY_USAGE, etc.) tienen `company_id=None` porque son alertas globales, no asociadas a una empresa específica.

### Archivos a Revisar

#### 1. `backend/app/workers/notification_worker.py`

**Líneas críticas:** ~30-80

**Verificar:**
- ✅ Manejo de `company_id=None` en función `process_notification_queue()`
- ✅ Validación de `queue.company_id` antes de queries
- ✅ Logging apropiado para alertas del sistema

**Código a validar:**
```python
# ¿El worker maneja company_id=None?
if queue.company_id:
    company = db.query(Company).filter(Company.id == queue.company_id).first()
    # Procesar con contexto de empresa
else:
    # Procesar como alerta del sistema
    # NO intentar buscar empresa
```

#### 2. `backend/app/services/notification_sender.py`

**Verificar:**
- ✅ Funciones `send_telegram()` y `send_email()` no requieren company_id
- ✅ Payload contiene toda la información necesaria
- ✅ Sin errores si company_id es None

### Tests Funcionales a Ejecutar

#### Test 1: Crear alerta del sistema manualmente

```python
# Crear notificación de prueba con company_id=None
from app.models.notification_queue import NotificationQueue
from app.database import get_db
import uuid

db = next(get_db())

test_notification = NotificationQueue(
    id=uuid.uuid4(),
    company_id=None,  # ← Alerta del sistema
    notification_type="system_alert",
    channel="telegram",
    status="pending",
    payload={
        "type": "SYSTEM_ALERT",
        "alert_type": "DISK_USAGE",
        "message": "Test: Disk usage at 85%"
    }
)

db.add(test_notification)
db.commit()

print(f"Notification created: {test_notification.id}")
```

#### Test 2: Procesar la notificación manualmente

```bash
# Ejecutar worker manualmente
curl -X POST http://localhost:8000/api/notifications/process

# Verificar logs
docker logs controlgastos-api | grep "Processing notification"

# Verificar que el status cambió a 'sent' o 'failed'
```

#### Test 3: Esperar ejecución automática del scheduler

```bash
# Scheduler ejecuta cada 10 minutos
# Verificar en logs que la alerta fue procesada
docker logs -f controlgastos-api

# Buscar:
# - "Alert monitoring job executed"
# - "Processing notification [uuid]"
# - "Notification sent successfully" o error
```

### Criterios de Aceptación

- [ ] Worker procesa notificaciones con `company_id=None` sin errores
- [ ] Logs muestran procesamiento correcto
- [ ] No hay intentos de buscar empresa cuando company_id=None
- [ ] Notificación se marca como 'sent' exitosamente
- [ ] No se generan excepciones no manejadas

---

## ⏸️ PRUEBAS FUNCIONALES COMPLETAS

### Estado: PENDIENTE

### Objetivo
Ejecutar suite completa de tests funcionales para validar integración end-to-end del sistema de alertas.

### Tests a Ejecutar

#### 1. Test de Scheduler Startup
```bash
# Reiniciar contenedor y verificar logs
docker restart controlgastos-api
docker logs controlgastos-api | grep -A5 "Application startup"

# ✅ Debe mostrar:
# - "APScheduler started"
# - "Alert monitoring job registered"
```

#### 2. Test de Evaluación de Alertas
```bash
# Forzar evaluación inmediata
curl -X POST http://localhost:8000/api/alerts/evaluate

# Verificar respuesta HTTP 200
# Revisar logs para ver alertas detectadas
```

#### 3. Test de Anti-Spam
```python
# Ejecutar evaluación 2 veces seguidas
import requests

response1 = requests.post("http://localhost:8000/api/alerts/evaluate")
response2 = requests.post("http://localhost:8000/api/alerts/evaluate")

# ✅ Primera ejecución debe encolar notificación
# ✅ Segunda ejecución NO debe encolar (anti-spam)
```

#### 4. Test de Procesamiento de Cola
```bash
# Procesar notificaciones encoladas
curl -X POST http://localhost:8000/api/notifications/process

# Verificar que notificaciones cambian de 'pending' a 'sent'
```

#### 5. Test de Endpoint de Retry
```bash
# Simular notificación fallida y reintentar
NOTIF_ID="<uuid-de-notificacion-fallida>"
curl -X POST http://localhost:8000/api/notifications/queue/${NOTIF_ID}/retry

# ✅ Debe retornar HTTP 200
# ✅ Status debe cambiar de 'failed' a 'pending'
```

### Checklist de Validación

#### Funcionalidad Core
- [ ] Scheduler se inicia automáticamente
- [ ] Job `alert_monitoring` ejecuta cada 10 minutos
- [ ] Evaluación de alertas detecta umbrales correctamente
- [ ] Anti-spam previene notificaciones duplicadas
- [ ] Notificaciones se encolan correctamente
- [ ] Worker procesa cola automáticamente
- [ ] Endpoint de retry funciona correctamente

#### Manejo de Errores
- [ ] Alertas con company_id=None se procesan sin errores
- [ ] Notificaciones fallidas se marcan como 'failed'
- [ ] Error messages se guardan en BD
- [ ] Sistema continúa funcionando tras errores

#### Performance
- [ ] Evaluación de alertas < 5 segundos
- [ ] Procesamiento de cola < 10 segundos
- [ ] Sin memory leaks tras 1 hora de operación
- [ ] Logs no exceden 100MB/día

---

## 📋 RESUMEN EJECUTIVO

### Estado Actual

| Componente | Estado | Comentarios |
|------------|--------|-------------|
| ETAPA 3.3 - Endpoint Retry | ✅ COMPLETADA | 100% funcional |
| ETAPA 5.3 - Scheduler | ✅ COMPLETADA | Startup hooks corregidos |
| Migración 003 | ⏸️ PENDIENTE | Archivo creado, falta ejecutar |
| Validación company_id=None | ⏸️ PENDIENTE | Requiere tests |
| Pruebas funcionales | ⏸️ PENDIENTE | Requiere ejecución completa |

### Tiempo Estimado

- **INCIDENCIA 2 (Migración):** 10 minutos
- **INCIDENCIA 3 (Validación):** 30 minutos
- **Pruebas funcionales:** 1-2 horas

**Total:** ~2-3 horas

### Riesgo

- **Migración:** Bajo (operación estándar)
- **Validación workers:** Medio (puede requerir ajustes)
- **Pruebas:** Bajo (detectar issues antes de producción)

### Recomendación

✅ **Completar las 3 incidencias antes del deployment en producción**

El sistema está técnicamente completo, pero requiere estas validaciones finales para garantizar operación estable 24/7.

---

## 🚀 SIGUIENTE PASO INMEDIATO

**Acción:** Ejecutar migración Alembic (INCIDENCIA 2)

```bash
# Comando a ejecutar:
docker exec -it controlgastos-api alembic upgrade head
```

**Duración estimada:** 5 minutos  
**Prerequisito:** Contenedores levantados con docker-compose  
**Riesgo:** Muy bajo  
**Reversión:** `alembic downgrade -1`
