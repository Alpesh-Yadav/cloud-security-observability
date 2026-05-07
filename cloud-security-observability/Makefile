.PHONY: cluster-up localstack-up deploy port-forward full-setup status terraform-apply destroy

cluster-up:
kind delete cluster --name security-observability || true
kind create cluster --name security-observability
kubectl create namespace monitoring || true
kubectl create namespace security || true
kubectl create namespace logging || true

localstack-up:
docker rm -f localstack || true
docker run -d --name localstack -p 4566:4566 -e SERVICES=s3,iam,cloudwatch,cloudtrail,sns,sqs localstack/localstack
bash -lc 'sleep 15 && /home/codespace/.python/current/bin/awslocal s3 mb s3://security-logs-bucket'
bash -lc '/home/codespace/.python/current/bin/awslocal iam create-role --role-name security-exporter-role --assume-role-policy-document "{"Version":"2012-10-17","Statement":[{"Effect":"Allow","Principal":{"Service":"ec2.amazonaws.com"},"Action":"sts:AssumeRole"}]}"'
bash -lc '/home/codespace/.python/current/bin/awslocal logs create-log-group --log-group-name /security/events || true'
bash -lc '/home/codespace/.python/current/bin/awslocal sns create-topic --name security-alerts'
bash -lc '/home/codespace/.python/current/bin/awslocal sqs create-queue --queue-name alert-queue'

deploy:
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts || true
helm repo add grafana https://grafana.github.io/helm-charts || true
helm repo update
helm install monitoring prometheus-community/kube-prometheus-stack --namespace monitoring --create-namespace --set grafana.adminPassword=admin123 --set prometheus.prometheusSpec.scrapeInterval=15s --set alertmanager.enabled=true --wait --timeout 5m || true
helm install loki grafana/loki-stack --namespace logging --create-namespace --set grafana.enabled=false --wait --timeout 3m || true
helm install security-exporter ./helm/security-exporter --namespace security --create-namespace --wait --timeout 3m || true

port-forward:
bash scripts/port-forward.sh

full-setup: cluster-up localstack-up deploy port-forward

status:
kubectl get all --all-namespaces

terraform-apply:
cd terraform && terraform apply -auto-approve

destroy:
helm uninstall security-exporter --namespace security || true
helm uninstall loki --namespace logging || true
helm uninstall monitoring --namespace monitoring || true
kind delete cluster --name security-observability || true
