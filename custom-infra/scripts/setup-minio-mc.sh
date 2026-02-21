#!/bin/bash

set -e

echo "🔍 Détection de l'IP du container MinIO..."

MINIO_IP=$(docker inspect tutor_local-minio-1 --format='{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}')

if [ -z "$MINIO_IP" ]; then
  echo "❌ Impossible de trouver l'IP du container MinIO"
  exit 1
fi

echo "✅ IP MinIO trouvée: $MINIO_IP"
echo ""

echo "📡 Configuration de l'alias mc..."
mc alias set minio-local \
  http://$\{MINIO_IP\}:9000 \
  openedx \
  7ozwtaX9Qt0qEQcgq8IRMS6y \
  --api S3v4

echo ""
echo "🧪 Test de connexion..."
if mc ls minio-local > /dev/null 2>&1; then
  echo "✅ Connexion réussie !"
else
  echo "❌ Connexion échouée"
  exit 1
fi

echo ""
echo "📦 Création du bucket mysite-images..."
mc mb minio-local/mysite-images --ignore-existing

echo ""
echo "🔓 Configuration des permissions publiques..."
mc anonymous set download minio-local/mysite-images

echo ""
echo "✅ Configuration terminée !"
