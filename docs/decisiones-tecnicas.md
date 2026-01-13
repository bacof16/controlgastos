# Decisiones Técnicas

## Registro de Decisiones Arquitectónicas (ADR)

Este documento registra las decisiones técnicas importantes tomadas durante el desarrollo de controlgastos.

## ADR-001: FastAPI como Backend Framework

**Fecha**: ETAPA 0  
**Estado**: Aprobado

**Contexto**:  
Necesitamos un framework backend moderno, rápido y fácil de mantener.

**Decisión**:  
Utilizar FastAPI con Python 3.12

**Justificación**:
- Alto rendimiento (comparable a Node.js y Go)
- Documentación automática con OpenAPI
- Tipado estático con Pydantic
- Comunidad activa y estable
- Curva de aprendizaje suave

**Consecuencias**:
- Equipo debe conocer Python
- Excelente para APIs RESTful
- Fácil de testear y mantener

---

## ADR-002: PostgreSQL como Base de Datos

**Fecha**: ETAPA 0  
**Estado**: Aprobado

**Contexto**:  
Necesitamos una base de datos relacional robusta y confiable.

**Decisión**:  
Utilizar PostgreSQL como única base de datos

**Justificación**:
- ACID compliant
- Extensiones potentes (UUID, JSON, etc.)
- Rendimiento probado
- Excelente para datos financieros
- Sin necesidad de bases adicionales

**Consecuencias**:
- Una sola tecnología de almacenamiento
- Fácil de hacer backup
- Menor complejidad operacional

---

## ADR-003: Docker Compose para Orquestación

**Fecha**: ETAPA 0  
**Estado**: Aprobado

**Contexto**:  
Necesitamos una forma simple de desplegar y mantener la aplicación.

**Decisión**:  
Usar Docker Compose en lugar de Kubernetes

**Justificación**:
- Simplicidad sobre complejidad
- Suficiente para escala media
- Fácil de entender para no-programadores
- Bajo overhead de recursos
- Deployment predecible

**Consecuencias**:
- Escalamiento vertical más que horizontal
- Suficiente para equipos pequeños/medianos
- Migración a Kubernetes posible si es necesaria

---

## ADR-004: Next.js para Frontend

**Fecha**: ETAPA 0  
**Estado**: Aprobado

**Contexto**:  
Necesitamos un framework frontend moderno con SSR.

**Decisión**:  
Utilizar Next.js para el frontend

**Justificación**:
- Server-Side Rendering integrado
- Optimización automática de performance
- SEO friendly
- React con mejores prácticas incluidas
- Ecosistema maduro

**Consecuencias**:
- Mejor experiencia de usuario
- Menor carga en cliente
- Requiere Node.js en servidor

---

## ADR-005: Alembic para Migraciones

**Fecha**: ETAPA 0  
**Estado**: Aprobado

**Contexto**:  
Necesitamos gestionar cambios en el esquema de base de datos.

**Decisión**:  
Utilizar Alembic para migraciones de base de datos

**Justificación**:
- Estándar de facto para SQLAlchemy
- Migraciones versionadas y rastreables
- Rollback seguro
- Generación automática de migraciones

**Consecuencias**:
- Control de versiones de esquema
- Deployment más seguro
- Historial de cambios claro

---

*Todas las decisiones técnicas deben documentarse aquí - ETAPA 0*
