#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
npm run build --prefix server/frontend
set -a
source .env
set +a
export PYTHONPATH="$PWD/.runtime/python"
export PYTHONUNBUFFERED=1
export DJANGO_ALLOWED_HOSTS='*'
export DJANGO_CSRF_TRUSTED_ORIGINS='https://*.proxy.cognitiveclass.ai,https://*.labs.skills.network'
python3 server/manage.py collectstatic --noinput
python3 bin/restart-owned-devserver.py
