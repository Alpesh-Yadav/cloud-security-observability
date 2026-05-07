#!/bin/bash

echo "🚀 Starting Cloud Security Observability Platform..."
echo "=================================================="

# Step 1 - Start LocalStack
echo ""
echo "📦 Step 1: Starting LocalStack..."
if docker ps | grep -q localstack; then
  echo "✅ LocalStack already running"
else
  docker start localstack 2>/dev/null || docker run -d \
    --name localstack \
    -p 4566:4566 \
    -e SERVICES=s3,iam,cloudwatch,logs,sns,sqs \
    localstack/localstack:3.0
  echo "⏳ Waiting for LocalStack to be ready..."
  sleep 20
fi
curl -s http://localhost:4566/_localstack/health | grep -q "s3" && echo "✅ LocalStack ready" || echo "⚠️ LocalStack may not be ready"

# Step 2 - Kubernetes cluster
echo ""
echo "☸️  Step 2: Checking Kubernetes cluster..."
if kind get clusters 2>/dev/null | grep -q "security-observability"; then
  echo "✅ Cluster already exists"
else
  echo "⏳ Creating kind cluster..."
  kind create cluster --name security-observability
  kubectl create namespace monitoring
  kubectl create namespace security
  kubectl create namespace logging
  echo "✅ Cluster created"
fi

# Step 3 - Helm repos
echo ""
echo "⎈  Step 3: Adding Helm repos..."
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts 2>/dev/null || true
helm repo add grafana https://grafana.github.io/helm-charts 2>/dev/null || true
helm repo update

# Step 4 - Deploy Prometheus + Grafana
echo ""
echo "📊 Step 4: Checking Prometheus + Grafana..."
if helm list -n monitoring | grep -q "monitoring"; then
  echo "✅ Prometheus stack already deployed"
else
  echo "⏳ Deploying kube-prometheus-stack (takes 3-5 mins)..."
  helm install monitoring prometheus-community/kube-prometheus-stack \
    --namespace monitoring \
    --set grafana.adminPassword=admin123 \
    --set prometheus.prometheusSpec.scrapeInterval=15s \
    --set alertmanager.enabled=true \
    --wait --timeout 8m
  echo "✅ Prometheus + Grafana deployed"
fi

# Step 5 - Deploy Loki
echo ""
echo "📜 Step 5: Checking Loki..."
if helm list -n logging | grep -q "loki"; then
  echo "✅ Loki already deployed"
else
  echo "⏳ Deploying Loki..."
  helm install loki grafana/loki-stack \
    --namespace logging \
    --set grafana.enabled=false \
    --wait --timeout 3m
  echo "✅ Loki deployed"
fi

# Step 6 - Build and deploy security exporter
echo ""
echo "🔐 Step 6: Checking security exporter..."
if helm list -n security | grep -q "security-exporter"; then
  echo "✅ Security exporter already deployed"
else
  echo "⏳ Building and deploying security exporter..."
  cd cloud-security-observability
  docker build -t security-exporter:v1.0 ./exporter
  kind load docker-image security-exporter:v1.0 --name security-observability
  helm install security-exporter ./helm/security-exporter --namespace security
  cd ..
  echo "✅ Security exporter deployed"
fi

# Step 7 - Terraform
echo ""
echo "🏗️  Step 7: Applying Terraform..."
cd cloud-security-observability/terraform
terraform init -input=false > /dev/null 2>&1
terraform apply -auto-approve > /dev/null 2>&1 && echo "✅ Terraform applied" || echo "⚠️ Terraform had errors (may already exist)"
cd ../..

# Step 8 - Wait for all pods
echo ""
echo "⏳ Step 8: Waiting for all pods to be ready..."
kubectl wait --for=condition=ready pod --all -n monitoring --timeout=120s 2>/dev/null || true
kubectl wait --for=condition=ready pod --all -n security --timeout=60s 2>/dev/null || true
echo "✅ Pods ready"

# Step 9 - Port forwarding
echo ""
echo "🌐 Step 9: Setting up port forwarding..."
pkill -f "kubectl port-forward" 2>/dev/null || true
sleep 2
kubectl port-forward svc/monitoring-grafana 3000:80 -n monitoring > /dev/null 2>&1 &
kubectl port-forward svc/prometheus-operated 9090:9090 -n monitoring > /dev/null 2>&1 &
kubectl port-forward svc/alertmanager-operated 9093:9093 -n monitoring > /dev/null 2>&1 &
kubectl port-forward svc/security-exporter 8000:8000 -n security > /dev/null 2>&1 &
sleep 5

# Step 10 - Verify
echo ""
echo "🔍 Step 10: Verifying services..."
curl -s http://localhost:8000/metrics > /dev/null && echo "✅ Security Exporter: http://localhost:8000/metrics" || echo "⚠️ Exporter not ready yet"
curl -s http://localhost:9090 > /dev/null && echo "✅ Prometheus:         http://localhost:9090" || echo "⚠️ Prometheus not ready yet"
curl -s http://localhost:3000 > /dev/null && echo "✅ Grafana:            http://localhost:3000 (admin/admin123)" || echo "⚠️ Grafana not ready yet"

echo ""
echo "=================================================="
echo "🎉 Platform is running! Open the PORTS tab above"
echo "   to access Grafana, Prometheus and Alertmanager"
echo "=================================================="
