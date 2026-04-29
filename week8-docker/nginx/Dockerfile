# ============================================================================
# Dockerfile — Nginx Reverse Proxy
# Práctica 2 GSX | Semana 8
# Puerto: 8080 (non-privileged, compatible con non-root user)
# ============================================================================

FROM nginx:1.27-alpine AS runtime

LABEL org.opencontainers.image.title="GreenDevCorp Nginx Proxy"
LABEL org.opencontainers.image.description="Reverse proxy — punto de entrada único del sistema"
LABEL org.opencontainers.image.version="1.0.0"

# ── [SEGURIDAD] Non-root user + permisos correctos ───────────────────────
RUN addgroup --system --gid 1001 proxygroup && \
    adduser  --system --uid 1001 --ingroup proxygroup --no-create-home proxyuser && \
    mkdir -p /var/cache/nginx/client_temp \
             /var/cache/nginx/proxy_temp \
             /var/cache/nginx/fastcgi_temp \
             /var/log/nginx \
             /tmp && \
    chown -R proxyuser:proxygroup \
        /var/cache/nginx \
        /var/log/nginx \
        /tmp && \
    chmod -R 755 /var/cache/nginx && \
    # Eliminar conf.d default que escucha en 80 (requiere root)
    rm -f /etc/nginx/conf.d/default.conf

# Copiar configuración personalizada (puerto 8080)
COPY --chown=proxyuser:proxygroup nginx.conf /etc/nginx/nginx.conf

USER proxyuser

# Puerto 8080: no requiere root ni CAP_NET_BIND_SERVICE
EXPOSE 8080

HEALTHCHECK --interval=30s --timeout=5s --start-period=15s --retries=3 \
    CMD wget --no-verbose --tries=1 --spider http://localhost:8080/health || exit 1

CMD ["nginx", "-g", "daemon off;"]
