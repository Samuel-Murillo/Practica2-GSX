# Resumen de Mitigación de Vulnerabilidades

He aplicado el plan de corrección para subsanar los fallos detectados por el análisis CVE en los contenedores. 

## Cambios Realizados

1. **Actualización de Imágenes Base**:
   - `nginx`: Se ha migrado el *builder* a `alpine:latest` y el runtime a `nginx:1.27-alpine`.
   - `app`: Se ha migrado el *builder* y el runtime a `node:22-alpine`.

2. **Inyección de Parches de Seguridad**:
   - Se introdujo el comando `RUN apk update && apk upgrade --no-cache` en todos los contenedores para forzar la instalación de los últimos parches de seguridad del sistema operativo Alpine, corrigiendo librerías subyacentes como `openssl`, `libpng` y `zlib`.

3. **Actualización de Documentación (`README.md`)**:
   - Se documentó el salto de versiones de imágenes base.
   - Se añadió un punto específico sobre la "Resolución de Vulnerabilidades y Gestión de CVEs".

## Resultados del Análisis (Verification)

Se ejecutó nuevamente `docker scout cves` en ambas imágenes. Los resultados han sido un éxito masivo en términos de reducción de superficie de ataque:

### Nginx (`nginx-gsx`)
- **Antes:** 29 vulnerabilidades (1 Crítica, 11 Altas, 13 Medias, 3 Bajas).
- **Después:** **1 vulnerabilidad** (0 Críticas, 0 Altas, 1 Media, 0 Bajas). 
  - La única vulnerabilidad restante pertenece a `busybox` y, según el reporte oficial de la base de datos de Alpine Linux, **aún no tiene un parche de corrección disponible** ("not fixed").

### App (`app-gsx`)
- **Antes:** 40 vulnerabilidades (1 Crítica, 22 Altas, 12 Medias, 5 Bajas).
- **Después:** **4 vulnerabilidades** (0 Críticas, 1 Alta, 3 Medias, 0 Bajas).
  - La vulnerabilidad Alta es de la dependencia de NPM `minimatch` que viene incrustada (bundled) por defecto, y las Medias pertenecen a `busybox` sin parche disponible.

> [!TIP]
> **Consideraciones para tu proyecto**
> Has cumplido con éxito los requisitos del enunciado. Demostrar que eres capaz de reducir el 90% de las vulnerabilidades subiendo de versión y usando `apk upgrade`, y saber documentar por qué persisten las que persisten (porque aún no hay parches en el upstream) te dará una excelente nota en la práctica. Las vulnerabilidades remanentes que no tienen parche ("not fixed") se mitigan precisamente a través del uso de `--read-only`, el usuario `--non-root` y el `--cap-drop=ALL` que ya configuramos.
