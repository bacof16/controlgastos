# Arquitectura del Sistema

## Descripción General

controlgastos está diseñado con una arquitectura de microservicios utilizando contenedores Docker para garantizar escalabilidad, mantenibilidad y portabilidad.

## Componentes

### Backend (FastAPI)
- Framework: FastAPI con Python 3.12
- Base de datos: PostgreSQL
- ORM: SQLAlchemy
- Migraciones: Alembic

### Frontend (Next.js)
- Framework: Next.js (por implementar)
- Renderizado: Server-Side Rendering (SSR)

### Base de Datos
- Motor: PostgreSQL
- Gestión: Docker Compose

## Flujo de Datos

1. Usuario interactúa con Frontend
2. Frontend hace peticiones a API Backend
3. Backend procesa lógica de negocio
4. Backend consulta/modifica Base de Datos
5. Backend retorna respuesta al Frontend

## Patrones de Diseño

- Repository Pattern para acceso a datos
- Dependency Injection
- Clean Architecture

## Seguridad

- Autenticación basada en tokens
- Variables de entorno para secretos
- CORS configurado

---

*Documento de referencia técnica - ETAPA 0*
