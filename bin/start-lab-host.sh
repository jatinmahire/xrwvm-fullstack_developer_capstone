#!/usr/bin/env bash
# A direct lab runtime for environments whose Docker build DNS is unavailable.
set -euo pipefail
cd "$(dirname "$0")/.."
mkdir -p .runtime/python evidence
python3 -m pip install --target .runtime/python -r server/requirements.txt -r server/djangoapp/microservices/requirements.txt
npm ci --prefix server/frontend
npm run build --prefix server/frontend
npm ci --prefix server/database
if [ ! -f .env ]; then
  python3 - <<'PY'
from pathlib import Path
import secrets
values={'DJANGO_SECRET_KEY':secrets.token_urlsafe(48),'DEMO_PASSWORD':secrets.token_urlsafe(16),'DEMO_ADMIN_PASSWORD':secrets.token_urlsafe(16),'DEMO_USERNAME':'learner'}
Path('.env').write_text(''.join(f'{k}={v}\n' for k,v in values.items()))
Path('.env').chmod(0o600)
PY
fi
set -a
source .env
set +a
export PYTHONPATH="$PWD/.runtime/python"
export DJANGO_ALLOWED_HOSTS='*'
export DJANGO_CSRF_TRUSTED_ORIGINS='https://*.proxy.cognitiveclass.ai,https://*.labs.skills.network'
if ! docker ps --format '{{.Names}}' | grep -qx 'carconnect-mongo-host'; then
  docker run -d --name carconnect-mongo-host -p 127.0.0.1:27017:27017 -v carconnect-host-mongo:/data/db mongo:7
fi
nohup node server/database/app.js > evidence/dealer-api.log 2>&1 < /dev/null &
nohup python3 server/djangoapp/microservices/app.py > evidence/sentiment.log 2>&1 < /dev/null &
cd server
python3 manage.py migrate --noinput
python3 manage.py seed_catalogue
python3 manage.py collectstatic --noinput
nohup python3 manage.py runserver 0.0.0.0:8000 --noreload > ../evidence/django_server.txt 2>&1 < /dev/null &
echo 'Lab host services started. Check ports 8000, 3030 and 5050.'
