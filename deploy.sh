#!/bin/bash

# Asegurar que se detiene el script en caso de error
set -e

# Variables
DOCKER_USERNAME="musefa"
NGINX_IMAGE_NAME="nginx-gsx"
APP_IMAGE_NAME="app-gsx"
VERSION="v1"

echo "=== Iniciando automatización de despliegue para GreenDevCorp ==="

echo "1. Autenticación en Docker Hub..."
docker login

echo "2. Construyendo imagen de Nginx..."
cd nginx
docker build -t $NGINX_IMAGE_NAME .
cd ..

echo "3. Construyendo imagen de Aplicación..."
cd app
docker build -t $APP_IMAGE_NAME .
cd ..

echo "4. Etiquetando imágenes..."
docker tag $NGINX_IMAGE_NAME $DOCKER_USERNAME/$NGINX_IMAGE_NAME:$VERSION
docker tag $APP_IMAGE_NAME $DOCKER_USERNAME/$APP_IMAGE_NAME:$VERSION

echo "5. Subiendo imágenes a Docker Hub..."
docker push $DOCKER_USERNAME/$NGINX_IMAGE_NAME:$VERSION
docker push $DOCKER_USERNAME/$APP_IMAGE_NAME:$VERSION

echo "=== Proceso completado exitosamente ==="
