"""
GreenDevCorp Backend API
Práctica 2 - GSX | Semana 8: Containerización

Arquitectura: FastAPI + Uvicorn
Seguridad: Non-root container, no hardcoded secrets, env-based config
"""
import os
import time
import platform
from datetime import datetime, timezone

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, Response
import uvicorn

# ---------------------------------------------------------------------------
# Configuración — Siempre desde variables de entorno, NUNCA hardcoded
# ---------------------------------------------------------------------------

APP_VERSION = os.getenv("APP_VERSION", "1.0.0")
APP_ENV     = os.getenv("APP_ENV", "production")
DB_HOST     = os.getenv("DB_HOST", "postgres")   # Resuelto vía DNS interno Docker/K8s
DB_PORT     = int(os.getenv("DB_PORT", "5432"))
DB_NAME     = os.getenv("DB_NAME", "greendavcorp")
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000").split(",")

# ---------------------------------------------------------------------------
# App setup
# ---------------------------------------------------------------------------

app = FastAPI(
    title="GreenDevCorp API",
    description="Backend API para la infraestructura de GreenDevCorp",
    version=APP_VERSION,
    # En producción desactivamos la documentación pública
    docs_url="/api/docs" if APP_ENV != "production" else None,
    redoc_url=None,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type", "Authorization"],
)

# Timestamp de arranque para calcular uptime
START_TIME = time.time()


# ---------------------------------------------------------------------------
# Middleware — Cabeceras de seguridad HTTP en todas las respuestas
# ---------------------------------------------------------------------------

@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    """
    Añade cabeceras de seguridad estándar (OWASP Secure Headers Project).
    Elimina la cabecera 'Server' para no revelar versión del software.
    """
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"]        = "DENY"
    response.headers["X-XSS-Protection"]       = "1; mode=block"
    response.headers["Referrer-Policy"]        = "strict-origin-when-cross-origin"
    response.headers["Cache-Control"]          = "no-store"
    response.headers.pop("Server", None)
    return response


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@app.get("/health", tags=["System"])
async def health_check():
    """
    Liveness/readiness probe para Docker HEALTHCHECK y Kubernetes probes.
    HTTP 200 = servicio operativo.
    """
    return {
        "status": "healthy",
        "uptime_seconds": int(time.time() - START_TIME),
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@app.get("/api/v1/status", tags=["API"])
async def get_status():
    """Estado del servicio. Nunca expone credenciales."""
    return {
        "service": "greendavcorp-backend",
        "version": APP_VERSION,
        "environment": APP_ENV,
        "uptime_seconds": int(time.time() - START_TIME),
        "python_version": platform.python_version(),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "database": {
            "host": DB_HOST,
            "port": DB_PORT,
            "name": DB_NAME,
            # NOTA: user/password NUNCA se exponen en endpoints
        },
    }


@app.get("/api/v1/info", tags=["API"])
async def get_info():
    """Información pública sobre GreenDevCorp."""
    return {
        "company": "GreenDevCorp",
        "description": "Empresa de desarrollo sostenible en crecimiento",
        "team_size": 20,
        "founded": 2020,
        "services": [
            {"name": "Desarrollo Web",        "status": "active"},
            {"name": "Cloud Infrastructure",  "status": "active"},
            {"name": "DevOps Consulting",      "status": "active"},
        ],
    }


@app.get("/metrics", tags=["System"])
async def metrics_endpoint():
    """
    Métricas en formato Prometheus text exposition format (RFC).
    Consumido por Prometheus scraper en Semana 13.
    """
    uptime = int(time.time() - START_TIME)
    metrics_text = (
        "# HELP greendavcorp_uptime_seconds Uptime del servicio backend\n"
        "# TYPE greendavcorp_uptime_seconds gauge\n"
        f"greendavcorp_uptime_seconds {uptime}\n"
        "# HELP greendavcorp_up Estado del servicio (1=operativo, 0=caído)\n"
        "# TYPE greendavcorp_up gauge\n"
        "greendavcorp_up 1\n"
    )
    return Response(content=metrics_text, media_type="text/plain; version=0.0.4")


# ---------------------------------------------------------------------------
# Entry point (para desarrollo local sin Docker)
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=False, log_level="info")
