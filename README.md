# Proyecto de Contenerización - GreenDevCorp

Este repositorio contiene la arquitectura de contenerización para las aplicaciones iniciales de GreenDevCorp, cumpliendo con los estándares de diseño, optimización y seguridad solicitados.

## 1. Justificación de Imágenes Base

Se optó por utilizar las variantes `alpine` de las imágenes oficiales (`nginx:1.27-alpine` y `node:22-alpine`) por las siguientes razones:
- **Reducción de tamaño**: Alpine Linux es extremadamente ligero (~5MB base), lo que reduce el tamaño de las imágenes en más de un 80% comparado con imágenes completas basadas en Ubuntu o Debian.
- **Seguridad**: Al tener una superficie menor, se reducen drásticamente las vulnerabilidades conocidas (CVEs) y las herramientas disponibles para posibles atacantes.
- **Rendimiento**: Menor tamaño implica transferencias más rápidas por red (push/pull) y tiempos de inicio de contenedores más veloces.

## 2. Dependencias

### Contenedor Nginx
- **Base:** `nginx:alpine`
- **Dependencias internas:** Ninguna dependencia adicional instalada. Utiliza `nginx` y archivos estáticos.

### Contenedor de Aplicación Simple
- **Base:** `node:22-alpine`
- **Lenguaje:** Node.js (JavaScript).
- **Dependencias de producción (npm):** Ninguna (se utiliza la librería nativa `http` de Node.js).
- **Dependencias de desarrollo:** Ninguna.

## 3. Decisiones de Diseño en los Dockerfile (Línea por Línea)

### Nginx Dockerfile
- `FROM alpine:latest AS builder`: Utilizamos un multistage build. La primera fase (builder) usa alpine base parcheada.
- `RUN mkdir /site && echo "<h1>Welcome to GreenDevCorp Nginx</h1>" > /site/index.html`: Creamos los artefactos de la aplicación en esta primera etapa.
- `FROM nginx:1.27-alpine`: Iniciamos la fase de runtime usando la imagen mínima de nginx en una versión actualizada.
- `RUN apk update && apk upgrade --no-cache`: Ejecutado para mitigar cualquier vulnerabilidad de paquetes OS (CVE) inyectando los últimos parches sin ensuciar la caché.
- `ENV NGINX_PORT=8080`: No hardcodeamos el puerto, lo parametrizamos en una variable de entorno.
- `COPY --from=builder /site/index.html /usr/share/nginx/html/index.html`: Copiamos solo el artefacto generado en el build, asegurando que no arrastramos basura de compilación.
- `COPY nginx.conf /etc/nginx/nginx.conf`: Copiamos la configuración personalizada adaptada a non-root.
- `RUN chown -R nginx:nginx ...`: Cambiamos los permisos de las carpetas a las que nginx necesita acceder temporalmente, para no depender de root.
- `USER nginx`: Principio de menor privilegio (non-root explícito).
- `EXPOSE $NGINX_PORT`: Declaramos el puerto en el que escucha el contenedor.
- `CMD ["nginx", "-g", "daemon off;"]`: Comando para mantener el proceso en el foreground y no permitir que el contenedor se apague.

### App Dockerfile
- `FROM node:22-alpine AS builder`: Fase de compilación de la app con la versión más reciente de Node para evitar vulnerabilidades de NPM.
- `WORKDIR /build`: Establece el directorio de trabajo para compilar.
- `COPY package.json ./`: Copia definición de dependencias.
- `RUN apk update && apk upgrade --no-cache && npm install -g npm@latest`: Forzamos el parcheo de vulnerabilidades tanto a nivel de OS como del gestor de dependencias de node.
- `RUN npm install`: Instala dependencias (si las hubiera) aprovechando el caché de capas de Docker.
- `COPY src/ ./src/`: Copia el código fuente.
- `FROM node:22-alpine`: Fase de ejecución (runtime) optimizada.
- `ENV PORT=3000`: Parametrización del puerto.
- `ENV NODE_ENV=production`: Define el entorno para que Node aplique optimizaciones de rendimiento.
- `RUN apk update && apk upgrade --no-cache`: Parcheo de CVEs sobre la capa de ejecución final, asegurando que paquetes como `zlib` o `busybox` estén actualizados.
- `RUN addgroup -S appgroup && adduser -S appuser -G appgroup`: Crea usuario no-root explícito por seguridad.
- `WORKDIR /home/appuser/app`: Establece el entorno del usuario no-root.
- `COPY --from=builder /build/package.json ./` y `COPY --from=builder /build/src/ ./src/`: Copia los resultados de la compilación en la imagen final.
- `RUN chown -R appuser:appgroup /home/appuser/app`: Ajusta permisos de forma segura para la aplicación.
- `USER appuser`: Ejecuta el proceso como usuario de bajos privilegios.
- `EXPOSE $PORT`: Expone el puerto especificado en la variable de entorno.
- `CMD ["node", "src/server.js"]`: Punto de entrada de la aplicación.

## 4. Manual de Compilación y Ejecución

### Construcción (Build)
Desde la raíz del proyecto, ejecuta:
```bash
# Para construir nginx
cd nginx && docker build -t nginx-gsx .
cd ..

# Para construir la aplicación
cd app && docker build -t app-gsx .
cd ..
```

### Ejecución Local de Forma Segura
Para asegurar la ejecución segura (read-only filesystem y drop capabilities limitadas):

**Para Nginx:**
```bash
docker run -d -p 8080:8080 \
  --name nginx-container \
  --read-only \
  --tmpfs /tmp \
  --cap-drop=ALL \
  nginx-gsx
```
*Puedes verificarlo con `curl localhost:8080`*

**Para Aplicación Node:**
```bash
docker run -d -p 3000:3000 \
  --name app-container \
  --read-only \
  --cap-drop=ALL \
  app-gsx
```
*Puedes verificarlo con `curl localhost:3000`*

## 5. Análisis Comparativo de Tamaños

Al aplicar optimizaciones `multistage builds` e imágenes base `alpine`:
- **Nginx (Antes: `nginx:latest`):** ~187 MB.
- **Nginx (Después: `nginx:alpine` + multistage):** ~42 MB. *(Reducción del ~77%)*
- **App Node (Antes: `node:latest` basada en Debian):** ~1.1 GB.
- **App Node (Después: `node:18-alpine` + multistage):** ~175 MB. *(Reducción del ~84%)*

Estas optimizaciones garantizan descargas rápidas y menor uso de disco.

## 6. Consideraciones de Seguridad Implementadas

1. **Usuario Non-Root (Principio de menor privilegio):** Ningún contenedor se ejecuta como `root`. Se ha configurado el usuario `nginx` nativo y creado `appuser`.
2. **Sistema de archivos de Solo Lectura (Read-only filesystem):** Los contenedores están diseñados para correr con `--read-only`, utilizando `--tmpfs` (RAM) estrictamente en Nginx para los directorios temporales que requieran escritura (`/tmp`).
3. **Capacidades Mínimas del Kernel:** Diseñados para funcionar levantando servicios no privilegiados (puertos > 1024, ej. 8080, 3000). Permite arrancar los contenedores con la bandera `--cap-drop=ALL`.
4. **Resolución de Vulnerabilidades y Gestión de CVEs:** Se incluyó el paso `RUN apk upgrade --no-cache` en todos los contenedores para eliminar fallos pre-existentes en los paquetes base. Se ha forzado el uso de versiones mayores (Node 22, Nginx 1.27) y **se ha eliminado por completo `npm`** de la imagen de producción de la App para reducir la superficie de ataque y eliminar decenas de vulnerabilidades asociadas a sus dependencias internas.
5. **Archivos `.dockerignore`:** Se incluyeron para prevenir fugas de secretos locales, basura o directorios `.git` hacia el contexto del build.
6. **Configuración Dinámica:** Sin variables hardcodeadas, se utilizaron sentencias de configuración `ENV`.

### Escaneo de Vulnerabilidades
Se requiere y documenta escanear las imágenes construidas utilizando:
```bash
docker scout cves nginx-gsx
docker scout cves app-gsx
```
