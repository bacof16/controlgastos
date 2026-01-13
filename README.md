# controlgastos

## Descripción

**controlgastos** es un sistema de gestión y control de gastos personales y empresariales diseñado para ser:

- **Estable**: Construido sobre tecnologías probadas y confiables
- **Eficiente**: Bajo consumo de recursos, optimizado para Ubuntu + Docker
- **Mantenible**: Código limpio, documentado y fácil de entender
- **Profesional**: Estructura clara para equipos técnicos y no técnicos

## Tecnologías

- **Backend**: FastAPI (Python 3.12)
- **Frontend**: Next.js (por implementar)
- **Base de Datos**: PostgreSQL
- **Infraestructura**: Docker Compose
- **Sistema Operativo**: Ubuntu Linux

## Requisitos

- Docker 24.0+
- Docker Compose 2.20+
- Ubuntu 22.04 LTS o superior

## Inicio Rápido

```bash
# Clonar el repositorio
git clone https://github.com/bacof16/controlgastos.git
cd controlgastos

# Copiar variables de entorno
cp .env.example .env
# Editar .env con tus valores reales

# Levantar servicios
cd infra
docker compose up -d
```

## Estructura del Proyecto

```
controlgastos/
├── backend/          # API FastAPI
├── frontend/         # Aplicación Next.js
├── infra/            # Configuración Docker
├── docs/             # Documentación técnica
├── .env.example      # Variables de entorno de ejemplo
├── .gitignore        # Archivos ignorados por git
└── README.md         # Este archivo
```

## Documentación

- [Arquitectura del Sistema](docs/arquitectura.md)
- [Reglas de Estabilidad](docs/reglas-estabilidad.md)
- [Decisiones Técnicas](docs/decisiones-tecnicas.md)

## Estado del Proyecto

**ETAPA 0 - Estructura Inicial** ✅

- [x] Configuración de repositorio
- [x] Estructura de carpetas
- [x] Documentación base
- [ ] Implementación de lógica de negocio

## Licencia

Propietario - Uso privado

## Contacto

Proyecto desarrollado para uso empresarial interno.
