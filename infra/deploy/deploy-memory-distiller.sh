#!/usr/bin/env bash
set -euo pipefail

APP_DIR="/opt/memory-distiller"
BRANCH="main"
LOCK_FILE="/tmp/memory-distiller-deploy.lock"

exec 9>"$LOCK_FILE"
flock -n 9 || {
  echo "Another deployment is already running."
  exit 1
}

echo "Starting Memory Distiller deployment..."
cd "$APP_DIR"

echo "Fetching latest code..."
git fetch origin "$BRANCH"
git checkout "$BRANCH"
git reset --hard "origin/$BRANCH"

echo "Building Docker image..."
docker compose build

echo "Starting updated container..."
docker compose up -d

echo "Container status:"
docker compose ps

echo "Waiting for health check..."
for i in {1..30}; do
  if curl -fsS http://127.0.0.1:8501/_stcore/health >/dev/null; then
    echo "Health check passed."
    echo "Deployment completed successfully."
    exit 0
  fi
  echo "Health check attempt $i failed; retrying..."
  sleep 2
done

echo "Health check failed."
docker compose logs --tail=100 memory-distiller || true
exit 1
