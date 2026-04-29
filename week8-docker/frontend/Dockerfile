# ============================================================================
# Dockerfile — GreenDevCorp Frontend
# Práctica 2 GSX | Semana 8: Containerización
#
# Estrategia: Multi-stage build
#   Stage 1 (builder): Node.js — prepara assets estáticos
#   Stage 2 (runtime): Nginx Alpine — sirve los ficheros
#
# Seguridad:
#   [1] Nginx Alpine — imagen mínima (~25MB)
#   [2] Non-root user — Nginx escucha en 8080 (non-privileged)
#   [3] nginx.conf personalizado (server_tokens off, CSP, security headers)
#   [4] Eliminamos conf.d/default.conf para evitar conflictos con entrypoint
#   [5] HEALTHCHECK nativo
# ============================================================================

# ─────────────────────────────────────────────────────────────────────────────
# STAGE 1: Builder — preparación de assets estáticos
# ─────────────────────────────────────────────────────────────────────────────
FROM node:20-alpine AS builder

LABEL stage="builder"
WORKDIR /build

# En proyecto real con React/Vue aquí iría:
#   COPY package*.json .
#   RUN npm ci --omit=dev
#   COPY . .
#   RUN npm run build
# Para esta práctica, copiamos estáticos directamente
COPY src/ ./dist/


# ─────────────────────────────────────────────────────────────────────────────
# STAGE 2: Runtime — servidor Nginx minimal
# ─────────────────────────────────────────────────────────────────────────────
FROM nginx:1.27-alpine AS runtime

LABEL org.opencontainers.image.title="GreenDevCorp Frontend"
LABEL org.opencontainers.image.description="Dashboard web de GreenDevCorp servido con Nginx"
LABEL org.opencontainers.image.version="1.0.0"

# ── [SEGURIDAD] Preparar entorno para non-root ────────────────────────────
# 1. Crear usuario/grupo non-root
# 2. Dar permisos sobre los directorios que nginx necesita en runtime
# 3. Eliminar conf.d/default.conf — evita conflictos con el docker-entrypoint
#    que intenta escuchar en 80 (root-only) y choca con nuestro non-root user
RUN addgroup --system --gid 1001 nginxgroup && \
    adduser  --system --uid 1001 --ingroup nginxgroup --no-create-home nginxuser && \
    mkdir -p /var/cache/nginx/client_temp \
             /var/cache/nginx/proxy_temp \
             /var/cache/nginx/fastcgi_temp \
             /var/cache/nginx/uwsgi_temp \
             /var/cache/nginx/scgi_temp \
             /var/log/nginx \
             /tmp && \
    chown -R nginxuser:nginxgroup \
        /var/cache/nginx \
        /var/log/nginx \
        /tmp && \
    chmod -R 755 /var/cache/nginx && \
    # Eliminar configuración default para evitar conflicto port 80 vs 8080
    rm -f /etc/nginx/conf.d/default.conf

# Copiar configuración Nginx segura (puerto 8080, no requiere root)
COPY --chown=nginxuser:nginxgroup nginx.conf /etc/nginx/nginx.conf

# Copiar assets estáticos desde el builder
COPY --from=builder --chown=nginxuser:nginxgroup /build/dist/ /usr/share/nginx/html/

# Cambiar al usuario non-root ANTES del EXPOSE
USER nginxuser

# Puerto 8080: non-privileged (no requiere CAP_NET_BIND_SERVICE ni root)
EXPOSE 8080

# Health check — verifica que Nginx está sirviendo en el puerto correcto
HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
    CMD wget --no-verbose --tries=1 --spider http://localhost:8080/health || exit 1

# Nginx en foreground mode (obligatorio en contenedores)
CMD ["nginx", "-g", "daemon off;"]
