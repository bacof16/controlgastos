# Reglas de Estabilidad

## Principios Fundamentales

controlgastos se rige por estas reglas estrictas para garantizar estabilidad, mantenibilidad y bajo consumo de recursos.

## 1. Simplicidad sobre Complejidad

- Usar soluciones probadas y establecidas
- Evitar dependencias innecesarias
- Preferir código claro sobre código "inteligente"

## 2. Base de Datos

- Una sola base de datos PostgreSQL
- Sin bases de datos adicionales (Redis, MongoDB, etc.)
- Migraciones controladas con Alembic
- Backup automático configurado

## 3. APIs y Servicios

- Un solo backend en FastAPI
- RESTful API claramente definida
- Versionado de API desde el inicio
- Sin microservicios innecesarios

## 4. Frontend

- Next.js con renderizado server-side
- Sin frameworks experimentales
- CSS modular y mantenible
- Progressive enhancement

## 5. Docker y Contenedores

- Imágenes base oficiales y estables
- Multi-stage builds para optimización
- Health checks configurados
- Logs centralizados

## 6. Documentación

- Código autodocumentado
- README actualizado
- Decisiones arquitectónicas registradas
- Comentarios solo cuando sean necesarios

## 7. Testing

- Tests unitarios para lógica crítica
- Tests de integración para APIs
- Coverage mínimo del 70%

## 8. Performance

- Queries optimizadas (sin N+1)
- Paginación obligatoria en listados
- Caching estratégico
- Monitoreo de recursos

## 9. Seguridad

- Variables de entorno para secretos
- Validación de inputs
- Rate limiting
- HTTPS obligatorio en producción

## 10. Mantenimiento

- Actualizaciones de seguridad prioritarias
- Dependencias mínimas y revisadas
- Compatibilidad hacia atrás cuando sea posible

---

*Estas reglas son obligatorias y no negociables - ETAPA 0*
