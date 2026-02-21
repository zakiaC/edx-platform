#!/bin/bash
SCRIPT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
PROJECT_ROOT=$(cd "$SCRIPT_DIR/.." && pwd)
SOURCE_DIR="$PROJECT_ROOT/assets"
TARGET="script-minio/mysite-images"

if [ ! -d "$SOURCE_DIR" ]; then
    mkdir -p "$SOURCE_DIR"
    echo "📁 Dossier assets créé automatiquement."
fi

mc mirror --overwrite "$SOURCE_DIR/" "$TARGET/" --insecure
echo "✅ Synchronisation terminée avec succès."
