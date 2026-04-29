# ============================================================================
# Dockerfile — GreenDevCorp Backend
# Práctica 2 GSX | Semana 8: Containerización
#
# Estrategia: Multi-stage build
#   Stage 1 (builder): Instala dependencias Python en un entorno aislado
#   Stage 2 (runtime): Copia SÓLO lo necesario — imagen final mínima y segura
#
# Seguridad implementada:
#   [1] Base image slim (no full) — reduce superficie de ataque
#   [2] Non-root user — principio de mínimo privilegio
#   [3] Sin secrets en el Dockerfile — todo vía variables de entorno
#   [4] HEALTHCHECK nativo de Docker
#   [5] No se instalan herramientas de build en la imagen final
# ============================================================================

# ─────────────────────────────────────────────────────────────────────────────
# STAGE 1: Builder — instalación de dependencias
# ─────────────────────────────────────────────────────────────────────────────
FROM python:3.12-slim AS builder

# Directorio de trabajo del builder
WORKDIR /build

# Copiar SÓLO requirements primero → Docker puede cachear esta capa
# Si requirements.txt no cambia, esta capa no se reconstruye (optimización)
COPY app/requirements.txt .

# Instalar dependencias en un directorio local (no en system site-packages)
# --no-cache-dir: no guardar cache de pip → imagen más pequeña
# --prefix: instala en /install para copiarlo fácilmente al stage final
RUN pip install --no-cache-dir --upgrade pip==24.1.2 && \
    pip install --no-cache-dir --prefix=/install -r requirements.txt


# ─────────────────────────────────────────────────────────────────────────────
# STAGE 2: Runtime — imagen final de producción
# ─────────────────────────────────────────────────────────────────────────────
FROM python:3.12-slim AS runtime

# Metadatos OCI estándar (buena práctica de documentación)
LABEL org.opencontainers.image.title="GreenDevCorp Backend"
LABEL org.opencontainers.image.description="FastAPI backend para GreenDevCorp"
LABEL org.opencontainers.image.version="1.0.0"
LABEL org.opencontainers.image.source="https://github.com/samuel-murillo/Practica2-GSX"

# ── Variables de entorno del runtime ──────────────────────────────────────
# PYTHONDONTWRITEBYTECODE: No genera ficheros .pyc → imagen más limpia
# PYTHONUNBUFFERED: Output de Python sin buffer → logs en tiempo real
# PYTHONPATH: Python busca módulos en /install/lib/...
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/install/lib/python3.12/site-packages \
    APP_ENV=production \
    APP_VERSION=1.0.0

# ── [SEGURIDAD] Crear usuario non-root ────────────────────────────────────
# Un proceso root en el contenedor = riesgo de escalada de privilegios
# Si el atacante sale del contenedor, es root en el host
RUN groupadd --system --gid 1001 appgroup && \
    useradd --system --uid 1001 --gid appgroup --no-create-home appuser

# Directorio de trabajo para la aplicación
WORKDIR /app

# Copiar dependencias instaladas desde el builder (sin pip, sin compiladores)
COPY --from=builder /install /install

# Copiar código fuente de la aplicación
COPY --chown=appuser:appgroup app/ .

# ── [SEGURIDAD] Cambiar al usuario non-root ANTES de exponer puertos ──────
USER appuser

# Puerto que expone la aplicación (documentación, no abre el puerto)
EXPOSE 8000

# ── Health check nativo de Docker ─────────────────────────────────────────
# Docker usa esto para reportar si el contenedor está "healthy" o "unhealthy"
# --interval: Comprueba cada 30s
# --timeout: Falla si no responde en 10s
# --start-period: Da 40s de gracia al arrancar (tiempo de inicialización)
# --retries: 3 fallos consecutivos → "unhealthy"
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" || exit 1

# ── Comando de arranque ───────────────────────────────────────────────────
# uvicorn: servidor ASGI de producción
# --host 0.0.0.0: escucha en todas las interfaces (necesario en contenedor)
# --workers 1: en producción real usar 2*CPU+1, aquí 1 para simplicidad
# --no-access-log: los logs de acceso los gestiona Nginx upstream
CMD ["python", "-m", "uvicorn", "main:app", \
     "--host", "0.0.0.0", \
     "--port", "8000", \
     "--workers", "1"]
