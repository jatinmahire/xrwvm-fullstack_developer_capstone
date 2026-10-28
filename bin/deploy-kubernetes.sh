#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
TASK_NAMESPACE=$(kubectl config view --minify -o jsonpath='{..namespace}')
if [ -z "$TASK_NAMESPACE" ]; then
  echo 'No learner namespace is configured.' >&2
  exit 1
fi
TASK_REGISTRY=${TASK_REGISTRY:-us.icr.io}
TASK_TAG=${TASK_TAG:-$(git rev-parse --short HEAD)}
TASK_PREFIX="$TASK_REGISTRY/$TASK_NAMESPACE/carconnect"
if [ ! -f .env ]; then
  python3 - <<'PY'
from pathlib import Path
import secrets
values={'DJANGO_SECRET_KEY':secrets.token_urlsafe(48),'DEMO_PASSWORD':secrets.token_urlsafe(16),'DEMO_ADMIN_PASSWORD':secrets.token_urlsafe(16),'DEMO_USERNAME':'learner'}
Path('.env').write_text(''.join(f'{k}={v}\n' for k,v in values.items()))
Path('.env').chmod(0o600)
PY
fi
ibmcloud cr login
docker build -t "$TASK_PREFIX-web:$TASK_TAG" server
docker build -t "$TASK_PREFIX-api:$TASK_TAG" server/database
docker build -t "$TASK_PREFIX-sentiment:$TASK_TAG" server/djangoapp/microservices
for service in web api sentiment; do
  docker push "$TASK_PREFIX-$service:$TASK_TAG"
done
kubectl create secret generic carconnect-settings --from-env-file=.env --dry-run=client -o yaml | kubectl apply -f -
python3 bin/render-kubernetes.py "$TASK_PREFIX" "$TASK_TAG" | kubectl apply -f -
for service in mongo api sentiment web; do
  kubectl rollout status "deployment/carconnect-$service" --timeout=240s
done
kubectl get deployment,service -l app.kubernetes.io/part-of=carconnect
echo 'Use the course lab application preview for port 8000 after starting the port-forward.'
