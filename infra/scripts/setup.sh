#!/usr/bin/env bash
set -euo pipefail

# Initial project setup: install dependencies, copy env files, start services
echo "==> AQ Project Setup"

# Copy environment files if they don't exist
if [ ! -f .env ]; then
  cp .env.example .env
  echo "    Created .env from .env.example"
fi

if [ ! -f backend/.env ]; then
  cp backend/.env.example backend/.env
  echo "    Created backend/.env"
fi

if [ ! -f frontend/.env.local ]; then
  cp frontend/.env.example frontend/.env.local
  echo "    Created frontend/.env.local"
fi

echo "==> Setup complete. Run 'make up' to start services."
