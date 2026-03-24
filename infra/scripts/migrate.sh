#!/usr/bin/env bash
set -euo pipefail

# Run Alembic database migrations
echo "==> Running database migrations..."
cd backend && alembic upgrade head
echo "==> Migrations complete."
