#!/bin/bash

# --- SCRIPT DE CONFIGURATION MINIO POUR MISSION FORMATIONS ---
echo "🚀 Configuration du bucket missionformations..."

# 1. Définition de l'URL de l'API S3
ENDPOINT="http://s3.local.openedx.io"

# 2. Création de l'alias
mc alias set script-minio $ENDPOINT openedx 7ozwtaX9Qt0qEQcgq8IRMS6y --insecure

# 3. Création du bucket
mc mb script-minio/mysite-images --insecure

# 4. Accès public
mc anonymous set download script-minio/mysite-images --insecure

echo "✅ Terminé ! Le bucket est prêt."
