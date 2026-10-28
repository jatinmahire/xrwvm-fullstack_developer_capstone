#!/usr/bin/env bash
# Deploy the verified CI images when container-build networking is restricted.
set -euo pipefail
cd "$(dirname "$0")/.."
TASK_NAMESPACE=$(kubectl config view --minify -o jsonpath='{..namespace}')
test -n "$TASK_NAMESPACE"
test -f .env
TASK_PREFIX="us.icr.io/$TASK_NAMESPACE/carconnect"
TASK_TAG="ci-99a0aa9"
ibmcloud cr login
for service in web api sentiment; do
  docker tag "carconnect-$service:ci" "$TASK_PREFIX-$service:$TASK_TAG"
  docker push "$TASK_PREFIX-$service:$TASK_TAG"
done
kubectl create secret generic carconnect-settings --from-env-file=.env --dry-run=client -o yaml | kubectl apply -f -
kubectl create secret generic carconnect-registry --type=kubernetes.io/dockerconfigjson --from-file=.dockerconfigjson="$HOME/.docker/config.json" --dry-run=client -o yaml | kubectl apply -f -
TASK_PULL_SECRET=carconnect-registry
if kubectl get secret icr >/dev/null 2>&1; then TASK_PULL_SECRET=icr; fi
python3 bin/render-kubernetes.py "$TASK_PREFIX" "$TASK_TAG" "$TASK_PULL_SECRET" | kubectl apply -f -
for service in mongo api sentiment web; do
  kubectl rollout status "deployment/carconnect-$service" --timeout=240s
done
nohup kubectl port-forward --address=127.0.0.1 service/carconnect-web 8092:8000 > evidence/kubernetes-forward.log 2>&1 < /dev/null &
kubectl get deployment,pods,service -l app.kubernetes.io/part-of=carconnect
echo 'Kubernetes application is available locally at http://127.0.0.1:8092/.'
