#!/bin/sh
set -e

MINIO_ALIAS="${MINIO_ALIAS:-local}"
MINIO_ENDPOINT="${MINIO_ENDPOINT:-http://minio:9000}"
MINIO_ACCESS_KEY="${MINIO_ACCESS_KEY:-minioadmin}"
MINIO_SECRET_KEY="${MINIO_SECRET_KEY:-minioadmin123}"
MINIO_BUCKET="${MINIO_BUCKET:-products}"

until mc alias set "$MINIO_ALIAS" "$MINIO_ENDPOINT" "$MINIO_ACCESS_KEY" "$MINIO_SECRET_KEY" 2>/dev/null; do
  echo "Waiting for MinIO..."
  sleep 2
done

mc mb --ignore-existing "$MINIO_ALIAS/$MINIO_BUCKET"
mc anonymous set download "$MINIO_ALIAS/$MINIO_BUCKET"
echo "Bucket $MINIO_BUCKET is ready (public read)."
