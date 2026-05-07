# Cloud-Native Security Observability Platform

[![Python](https://img.shields.io/badge/Python-3.9-blue)](https://www.python.org/)
[![Prometheus](https://img.shields.io/badge/Prometheus-enabled-orange)](https://prometheus.io/)
[![Grafana](https://img.shields.io/badge/Grafana-enabled-brightgreen)](https://grafana.com/)
[![Kubernetes](https://img.shields.io/badge/Kubernetes-kind-blue)](https://kubernetes.io/)
[![Terraform](https://img.shields.io/badge/Terraform-enabled-623ce4)](https://terraform.io/)
[![Helm](https://img.shields.io/badge/Helm-enabled-0f1016)](https://helm.sh/)
[![LocalStack](https://img.shields.io/badge/LocalStack-enabled-yellowgreen)](https://localstack.cloud/)
[![Docker](https://img.shields.io/badge/Docker-enabled-2496ed)](https://docker.com/)

## Architecture

```
[LocalStack] -> [security exporter] -> [Prometheus] -> [Grafana]
       |                  |                |
       +-> S3/SQS/CloudWatch/SNS + Loki + Alertmanager
```

## Quick Start

```bash
make full-setup
```

## Metrics

| Name | Type | Labels | Description |
| --- | --- | --- | --- |
| `security_exporter_s3_object_count` | Gauge | environment, region, source | S3 object count from LocalStack bucket |
| `security_exporter_sqs_queue_depth` | Gauge | environment, region, source | Visible SQS queue depth |
| `security_exporter_cloudwatch_metric_count` | Gauge | environment, region, source | CloudWatch metrics count from LocalStack |
| `security_exporter_failed_auth_rate` | Gauge | environment, region, source | Simulated failed authentication rate |
| `security_exporter_iam_policy_changes_total` | Gauge | environment, region, source | Simulated IAM policy changes |
| `security_exporter_unauthorized_api_calls_total` | Gauge | environment, region, source | Simulated unauthorized API calls |
| `security_exporter_privilege_escalation_attempts` | Gauge | environment, region, source | Simulated privilege escalation attempts |
| `security_exporter_suspicious_ip_count` | Gauge | environment, region, source | Simulated suspicious IP count |

## Alerts

| Name | Severity | Condition |
| --- | --- | --- |
| ExporterDown | critical | `up{job="security-exporter"} == 0` |
| HighFailedAuthRate | warning | `security_exporter_failed_auth_rate > 5` |
| SuspiciousIPSpike | warning | `security_exporter_suspicious_ip_count > 10` |

## SLO Summary

| Objective | Target | Error Budget |
| --- | --- | --- |
| Exporter uptime | 99.9% | 43.2 minutes |
| Alert delivery reliability | 99.9% | 43.2 minutes |
| Prometheus scrape success | 99.9% | 43.2 minutes |

## Helm Deployment

```bash
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo add grafana https://grafana.github.io/helm-charts
helm repo update
helm install monitoring prometheus-community/kube-prometheus-stack --namespace monitoring --create-namespace --set grafana.adminPassword=admin123 --set prometheus.prometheusSpec.scrapeInterval=15s --set alertmanager.enabled=true --wait --timeout 5m
helm install loki grafana/loki-stack --namespace logging --create-namespace --set grafana.enabled=false --wait --timeout 3m
helm install security-exporter ./helm/security-exporter --namespace security --create-namespace --wait --timeout 3m
```

## Terraform

```bash
cd terraform
terraform init
terraform apply -auto-approve
```

## Production Differences

- Production uses real AWS resources instead of LocalStack mocks.
- LocalStack exposes AWS APIs locally on `http://localhost:4566`.
- Production requires valid AWS credentials and real networking.
- LocalStack is for local development and testing only.
- Prometheus/Grafana behavior stays consistent across environments.

## What I Learned

1. Kind provides local Kubernetes for secure development.
2. LocalStack enables AWS API testing without real AWS accounts.
3. Helm packages services and monitoring into reusable charts.
4. Terraform can provision resources to mocked AWS endpoints.
5. SLO definitions and burn-rate math improve reliability reasoning.
