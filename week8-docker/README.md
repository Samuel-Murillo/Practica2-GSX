# Semana 8 — Containerización con Docker

## Objetivo

Empaquetar los servicios de **GreenDevCorp** en imágenes Docker reproducibles, optimizadas y seguras, siguiendo buenas prácticas de producción.

## Arquitectura

```
                    ┌─────────────────────────────────┐
                    │     GreenDevCorp - Semana 8      │
                    │                                  │
  build/test ──────►│  [Backend]  python:3.12-slim     │
                    │  FastAPI · Puerto 8000            │
                    │                                  │
  build/test ──────►│  [Frontend] node:20-alpine       │
                    │  → nginx:1.27-alpine · Puerto 3000│
                    │                                  │
  build/test ──────►│  [Proxy]    nginx:1.27-alpine    │
                    │  Reverse Proxy · Puerto 80        │
                    └─────────────────────────────────┘
```

## Estructura de archivos

```
week8-docker/
├── backend/
│   ├── app/
│   │   ├── main.py          # FastAPI con /health, /api/v1/*, /metrics
│   │   └── requirements.txt # Dependencias fijadas (pinned versions)
│   ├── Dockerfile           # Multi-stage, non-root (uid 1001), healthcheck
│   └── .dockerignore
├── frontend/
│   ├── src/
│   │   └── index.html       # Dashboard GreenDevCorp (HTML/CSS/JS)
│   ├── nginx.conf           # Config segura (server_tokens off, CSP, rate limit)
│   ├── Dockerfile           # Multi-stage (Node → Nginx Alpine), non-root
│   └── .dockerignore
└── nginx/
    ├── nginx.conf           # Reverse proxy con upstreams y rate limiting
    └── Dockerfile           # Nginx Alpine, non-root
```

## Comandos de build y prueba

### Construir imágenes

```bash
# Backend
docker build -t greendavcorp-backend:1.0.0 ./week8-docker/backend/

# Frontend
docker build -t greendavcorp-frontend:1.0.0 ./week8-docker/frontend/

# Nginx Proxy
docker build -t greendavcorp-proxy:1.0.0 ./week8-docker/nginx/
```

### Verificar imágenes construidas

```bash
docker images | grep greendavcorp
```

### Probar backend en local

```bash
docker run --rm -d \
  --name backend-test \
  -p 8000:8000 \
  -e APP_ENV=development \
  greendavcorp-backend:1.0.0

# Verificar health
curl http://localhost:8000/health

# Ver logs
docker logs backend-test

# Parar
docker stop backend-test
```

### Escaneo de seguridad con Trivy (nivel intermedio/avanzado)

```bash
# Instalar Trivy: https://trivy.dev/latest/getting-started/installation/
trivy image greendavcorp-backend:1.0.0
trivy image greendavcorp-frontend:1.0.0
```

## Decisiones de diseño y seguridad

| Práctica | Motivo |
|---|---|
| **Multi-stage build** | La imagen final no contiene compiladores ni herramientas de build — reduce superficie de ataque y tamaño |
| **Non-root user (uid 1001)** | Principio de mínimo privilegio — si el proceso es comprometido, el atacante no tiene acceso root al host |
| **`python:3.12-slim`** | Versión activa con parches de seguridad. `slim` elimina herramientas innecesarias vs imagen completa |
| **`nginx:1.27-alpine`** | Alpine Linux — imagen mínima (~5MB base), actualizaciones de seguridad frecuentes |
| **Versiones fijadas en requirements.txt** | Reproducibilidad y control de supply chain (evitar dependencias comprometidas) |
| **`server_tokens off`** | No revelar versión de Nginx a posibles atacantes |
| **Cabeceras HTTP de seguridad** | OWASP Secure Headers Project — protección XSS, clickjacking, MIME sniffing |
| **HEALTHCHECK en Dockerfile** | Docker puede detectar y reiniciar contenedores degradados automáticamente |
| **`.dockerignore`** | Evita copiar `.env`, venvs, Git history al contexto de build |

## Publicación en Docker Hub (nivel intermedio)

```bash
# Login
docker login

# Tag con tu username de Docker Hub
docker tag greendavcorp-backend:1.0.0 TU_USUARIO/greendavcorp-backend:1.0.0
docker tag greendavcorp-backend:1.0.0 TU_USUARIO/greendavcorp-backend:latest

# Push
docker push TU_USUARIO/greendavcorp-backend:1.0.0
docker push TU_USUARIO/greendavcorp-backend:latest
```
