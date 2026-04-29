# ============================================================================
# Dockerfile — GreenDevCorp Frontend
# Práctica 2 GSX | Semana 8: Containerización
#
# Estrategia: Multi-stage build
#   Stage 1 (builder): Node.js — copia los fuentes estáticos
#   Stage 2 (runtime): Nginx Alpine — sirve los ficheros estáticos
#
# Nota: En esta práctica el frontend es HTML/CSS/JS puro (sin framework),
#       por lo que el stage de Node es trivial. En un proyecto real con
#       React/Vue, aquí se ejecutaría el build (npm run build).
#       Lo mantenemos multi-stage para consistencia y demostración del patrón.
#
# Seguridad:
#   [1] Nginx Alpine — imagen mínima (~25MB)
#   [2] Non-root user — Nginx escucha en puerto >1024 (3000)
#   [3] nginx.conf personalizado con cabeceras de seguridad
#   [4] HEALTHCHECK nativo
# ============================================================================

# ─────────────────────────────────────────────────────────────────────────────
# STAGE 1: Builder — preparación de assets estáticos
# ─────────────────────────────────────────────────────────────────────────────
FROM node:20-alpine AS builder

LABEL stage="builder"

WORKDIR /build

# En un proyecto con dependencias npm se haría:
#   COPY package*.json .
#   RUN npm ci --omit=dev
#   COPY . .
#   RUN npm run build

# Para esta práctica, copiamos los archivos estáticos directamente
COPY src/ ./dist/


# ─────────────────────────────────────────────────────────────────────────────
# STAGE 2: Runtime — servidor Nginx minimal
# ─────────────────────────────────────────────────────────────────────────────
FROM nginx:1.27-alpine AS runtime

LABEL org.opencontainers.image.title="GreenDevCorp Frontend"
LABEL org.opencontainers.image.description="Dashboard web de GreenDevCorp servido con Nginx"
LABEL org.opencontainers.image.version="1.0.0"

# ── [SEGURIDAD] Crear usuario non-root para Nginx ─────────────────────────
# Por defecto Nginx corre como root — esto es un riesgo de seguridad.
# Nginx puede escuchar en puertos >1024 sin privilegios de root.
# Puerto elegido: 3000 (no requiere root, al contrario que 80)

RUN addgroup --system --gid 1001 nginxgroup && \
    adduser  --system --uid 1001 --ingroup nginxgroup --no-create-home nginxuser && \
    # Crear directorios necesarios y dar permisos al usuario non-root
    mkdir -p /var/cache/nginx /var/log/nginx /tmp && \
    chown -R nginxuser:nginxgroup \
        /var/cache/nginx \
        /var/log/nginx \
        /etc/nginx \
        /tmp \
        /usr/share/nginx/html

# Copiar configuración Nginx personalizada (segura)
COPY --chown=nginxuser:nginxgroup nginx.conf /etc/nginx/nginx.conf

# Copiar archivos estáticos compilados desde el builder
COPY --from=builder --chown=nginxuser:nginxgroup /build/dist/ /usr/share/nginx/html/

# Cambiar al usuario non-root
USER nginxuser

# Nginx escucha en 3000 (non-privileged port, no requiere root)
EXPOSE 3000

# Health check — verifica que Nginx está sirviendo correctamente
HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
    CMD wget --no-verbose --tries=1 --spider http://localhost:3000/health || exit 1

# Nginx foreground mode (necesario en contenedores — no daemonize)
CMD ["nginx", "-g", "daemon off;"]
