#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
if [ ! -f .env ]; then
  python3 - <<'PY'
from pathlib import Path
import secrets
values={'DJANGO_SECRET_KEY':secrets.token_urlsafe(48),'DEMO_PASSWORD':secrets.token_urlsafe(16),'DEMO_ADMIN_PASSWORD':secrets.token_urlsafe(16),'DEMO_USERNAME':'learner'}
Path('.env').write_text(''.join(f'{k}={v}\n' for k,v in values.items()))
Path('.env').chmod(0o600)
PY
fi
docker compose up --build -d
docker compose ps
