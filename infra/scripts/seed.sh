#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
BACKEND_ENV_FILE="${ROOT_DIR}/backend/.env"
SEED_SQL_FILE="${ROOT_DIR}/infra/seeds/reference_data.sql"

if ! command -v psql >/dev/null 2>&1; then
  echo "psql is required to run seeds."
  exit 1
fi

if [[ ! -f "${BACKEND_ENV_FILE}" ]]; then
  echo "Missing ${BACKEND_ENV_FILE}. Create it first."
  exit 1
fi

set -a
. "${BACKEND_ENV_FILE}"
set +a

if [[ -z "${DATABASE_URL:-}" ]]; then
  echo "DATABASE_URL is not set in ${BACKEND_ENV_FILE}."
  exit 1
fi

SYNC_DATABASE_URL="${DATABASE_URL/+asyncpg/}"
SYNC_DATABASE_URL="${SYNC_DATABASE_URL/+psycopg/}"

if [[ ! -f "${SEED_SQL_FILE}" ]]; then
  echo "Missing seed file: ${SEED_SQL_FILE}"
  exit 1
fi

echo "==> Seeding reference data into ${SYNC_DATABASE_URL}"
psql "${SYNC_DATABASE_URL}" -v ON_ERROR_STOP=1 -f "${SEED_SQL_FILE}"
echo "==> Seed complete."
