# GreenDevCorp Infrastructure — Práctica 2 GSX

[![CI](https://github.com/Samuel-Murillo/Practica2-GSX/actions/workflows/ci.yml/badge.svg)](https://github.com/Samuel-Murillo/Practica2-GSX/actions)

## 📋 Descripción

Infraestructura IT completa para **GreenDevCorp**, una empresa de desarrollo sostenible en crecimiento. Implementada siguiendo estándares de producción real: contenedores seguros, orquestación escalable, automatización declarativa, redes segmentadas y observabilidad completa.

**Asignatura:** Gestión de Sistemas y Redes (GSX) — Práctica 2  
**Período:** Semanas 8–13 | **Entrega:** 15 de mayo de 2026

---

## 🏗️ Arquitectura

```
Internet
   │
   ▼
[Nginx Proxy :80]  ← único punto de entrada
   │
   ├──► [Frontend :3000]   (Dashboard web)
   │
   └──► [Backend API :8000] (FastAPI REST)
              │
              ▼
        [PostgreSQL :5432]  (aislado, sin acceso externo)
              │
        [Prometheus + Grafana]  (observabilidad, Semana 13)
```

**Segmentación de red (Docker Compose / Kubernetes):**
- `dmz_net` — Proxy expuesto al exterior
- `internal_net` — Frontend ↔ Backend
- `db_net` — Backend ↔ PostgreSQL (aislada)

---

## 📦 Estructura del repositorio

```
Practica2-GSX/
├── .github/workflows/     # CI/CD — GitHub Actions (Semana 11)
├── week8-docker/          # Semana 8: Containerización
│   ├── backend/           # FastAPI + Dockerfile multi-stage
│   ├── frontend/          # Dashboard HTML/CSS/JS + Nginx
│   └── nginx/             # Reverse Proxy
├── week9-compose/         # Semana 9: Docker Compose
│   ├── docker-compose.yml # Stack completo (4 servicios, 3 redes)
│   └── .env.example       # Template de variables de entorno
├── week10-kubernetes/     # Semana 10: Kubernetes (Minikube)
├── week11-iac/            # Semana 11: Terraform + GitHub Actions
├── week12-network/        # Semana 12: Network Design + NetworkPolicies
├── week13-observability/  # Semana 13: Prometheus + Grafana
└── docs/                  # Arquitectura, Runbook, Troubleshooting
```

---

## 🚀 Inicio rápido

### Pre-requisitos

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) ≥ 26.x
- [Docker Compose](https://docs.docker.com/compose/) (incluido en Docker Desktop)
- [Minikube](https://minikube.sigs.k8s.io/) (para Semana 10)
- [kubectl](https://kubernetes.io/docs/tasks/tools/) (para Semana 10)

### Levantar el stack completo (Semana 9)

```bash
# 1. Crear fichero de entorno con credenciales
cp week9-compose/.env.example week9-compose/.env
# Editar .env y cambiar DB_USER y DB_PASSWORD

# 2. Construir imágenes localmente
docker build -t greendavcorp-backend:1.0.0  ./week8-docker/backend/
docker build -t greendavcorp-frontend:1.0.0 ./week8-docker/frontend/
docker build -t greendavcorp-proxy:1.0.0    ./week8-docker/nginx/

# 3. Levantar todos los servicios
docker compose -f week9-compose/docker-compose.yml --env-file week9-compose/.env up -d

# 4. Verificar que todos están healthy
docker compose -f week9-compose/docker-compose.yml ps

# 5. Acceder al dashboard
# Abrir http://localhost en el navegador
```

### Verificar servicios individualmente

```bash
# Health del backend
curl http://localhost/health

# Status de la API
curl http://localhost/api/v1/status

# Métricas (formato Prometheus)
curl http://localhost/metrics
```

---

## 🔒 Seguridad implementada

| Área | Medida | Impacto |
|---|---|---|
| **Contenedores** | Non-root user (uid 1001) en todos | Mínimo privilegio |
| **Imágenes** | Multi-stage build, alpine/slim | Superficie de ataque reducida |
| **Secretos** | Variables de entorno, nunca hardcoded | Evita exposición de credenciales |
| **Red** | 3 redes aisladas (DMZ/Internal/DB) | Segmentación de tráfico |
| **HTTP** | Cabeceras OWASP (X-Frame, CSP, etc.) | Protección cliente |
| **Nginx** | `server_tokens off`, rate limiting | Oscurecer versión, proteger DDoS |
| **Git** | `.gitignore` completo + `.env.example` | No filtrar secretos |
| **PostgreSQL** | Sin puerto expuesto al host | Acceso solo desde backend |

---

## 📅 Progreso semanal

| Semana | Contenido | Estado |
|---|---|---|
| **8** | Docker — Containerización | ✅ Completo |
| **9** | Docker Compose — Orquestación | ✅ Completo |
| **10** | Kubernetes (Minikube) | 🔄 Pendiente |
| **11** | IaC (Terraform) + CI/CD (GitHub Actions) | 🔄 Pendiente |
| **12** | Network Design + Identity | 🔄 Pendiente |
| **13** | Observabilidad + Documentación final | 🔄 Pendiente |

---

## 👥 Equipo

Samuel Murillo — Práctica 2 GSX
