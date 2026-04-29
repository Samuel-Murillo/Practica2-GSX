# ============================================================================
# Dockerfile — Nginx Reverse Proxy
# Práctica 2 GSX | Semana 8
# ============================================================================

FROM nginx:1.27-alpine AS runtime

LABEL org.opencontainers.image.title="GreenDevCorp Nginx Proxy"
LABEL org.opencontainers.image.description="Reverse proxy — punto de entrada único del sistema"
LABEL org.opencontainers.image.version="1.0.0"

# ── [SEGURIDAD] Non-root user ─────────────────────────────────────────────
# Nginx necesita puerto 80 que normalmente requiere root.
# Solución: En Docker Compose le asignamos cap_drop + cap_add NET_BIND_SERVICE,
#           o bien usamos un puerto >1024. Aquí mantenemos 80 porque el
#           proxy está detrás de Docker port mapping (no directamente expuesto).
RUN addgroup --system --gid 1001 proxygroup && \
    adduser  --system --uid 1001 --ingroup proxygroup --no-create-home proxyuser && \
    mkdir -p /var/cache/nginx /var/log/nginx /tmp && \
    chown -R proxyuser:proxygroup \
        /var/cache/nginx \
        /var/log/nginx \
        /etc/nginx \
        /tmp

# Copiar configuración personalizada
COPY --chown=proxyuser:proxygroup nginx.conf /etc/nginx/nginx.conf

USER proxyuser

EXPOSE 80

HEALTHCHECK --interval=30s --timeout=5s --start-period=15s --retries=3 \
    CMD wget --no-verbose --tries=1 --spider http://localhost:80/health || exit 1

CMD ["nginx", "-g", "daemon off;"]
