# Cloud-Native Security Observability Platform

A comprehensive observability platform for cloud security monitoring, built with Prometheus, Grafana, Alertmanager, and Loki.

## Features

- **Real-time Security Metrics**: Failed authentication rates, IAM policy changes, unauthorized API calls
- **Dashboards**: Security Events, Infrastructure Overview, SLO Tracking, and Alerts Summary
- **Alerting**: Automated alert generation and routing via Alertmanager
- **Logging**: Log aggregation with Loki and Promtail
- **Exporters**: Custom Python security exporter generating realistic security metrics

## Project Structure

```
cloud-security-observability/
├── exporter/              # Security metrics exporter
│   ├── security_exporter.py
│   ├── Dockerfile
│   └── requirements.txt
├── prometheus/            # Prometheus configuration
│   ├── prometheus.yml
│   └── alerts.yml
├── grafana/               # Grafana dashboards
│   └── dashboards/
│       ├── security_events_dashboard.json
│       ├── infrastructure_overview_dashboard.json
│       ├── slo_dashboard.json
│       └── alerts_summary_dashboard.json
├── alertmanager/          # Alert management
│   └── alertmanager.yml
├── loki/                  # Log aggregation
│   └── loki-config.yml
├── promtail/              # Log forwarder
│   └── promtail-config.yml
├── docker-compose.yml
├── Makefile
└── README.md
```

## Quick Start

### Prerequisites

- Docker and Docker Compose
- Terraform, kubectl, Helm (for Kubernetes deployments)
- Python 3.9+ (for local development)

### Installation

1. **Start the stack**:
   ```bash
   make up
   # or
   docker compose up -d
   ```

2. **Access the services**:
   - **Prometheus**: http://localhost:9090
   - **Grafana**: http://localhost:3000 (login: admin/admin)
   - **Alertmanager**: http://localhost:9093
   - **Loki**: http://localhost:3100

3. **Import Grafana Dashboards**:
   - Open Grafana
   - Click **+** → **Import**
   - Upload JSON files from `grafana/dashboards/`

### Usage

```bash
# View logs
make logs

# Restart services
make restart

# Stop the stack
make down

# Clean up volumes
make clean

# Test alert generation
make test-alerts
```

## Metrics Overview

### Security Exporter (`security_exporter.py`)

Exposes three key security metrics on port 8000:

1. **failed_auth_rate** (Gauge): Rate of failed authentication attempts
   - Alert: Fires if > 5 for 1 minute

2. **iam_policy_changes_total** (Counter): Total IAM policy modifications
   - Alert: Fires if increases by > 10 in 5 minutes

3. **unauthorized_api_calls_total** (Counter): Total unauthorized API calls
   - Alert: Fires if > 10

## Alert Rules

All alerts are defined in `prometheus/alerts.yml`:

- **HighFailedAuthRate**: Failed authentication spike
- **IAMPolicySpike**: Rapid IAM policy changes
- **UnauthorizedAPIBurst**: Surge in unauthorized API calls

Alerts route to Alertmanager, configured to send to Slack (placeholder webhook in `alertmanager/alertmanager.yml`).

## Configuration Files

### Prometheus (`prometheus/prometheus.yml`)
- Scrape interval: 15 seconds
- Data retention: 200 hours
- Alert rules: `prometheus/alerts.yml`
- Alert manager endpoint: `alertmanager:9093`

### Alertmanager (`alertmanager/alertmanager.yml`)
- Routes alerts by severity
- Slack webhook integration (configure with real webhook)
- Alert grouping and repeat intervals

### Grafana Dashboards
Four pre-built dashboards visualize:
- Security events (auth, IAM, API calls)
- Infrastructure metrics (CPU, memory)
- SLO and error budget tracking
- Active alert summary

## Troubleshooting

### Check service health
```bash
docker compose ps
```

### View service logs
```bash
docker compose logs [service_name]
# Examples:
docker compose logs prometheus
docker compose logs grafana
docker compose logs alertmanager
```

### Verify metrics are being scraped
```bash
curl http://localhost:9090/api/v1/targets
```

### Check active alerts
```bash
curl http://localhost:9090/api/v1/alerts
curl http://localhost:9093/api/v2/alerts
```

### Reset Grafana password
```bash
docker compose down
docker volume rm cloud-security-observability_grafana_data
docker compose up -d
```

## Enhancement Ideas

### Real Data Sources
- **AWS CloudWatch Integration**: Monitor actual IAM changes via AWS SDK
- **Application Logs**: Forward application security logs to Loki
- **Kubernetes Audit Logs**: Integrate with K8s audit logging

### Additional Exporters
- Node Exporter (system metrics)
- Custom metrics for your applications
- Container/orchestration metrics

### Kubernetes Deployment
```bash
# Build Helm chart for deployment:
terraform apply  # Infrastructure provisioning
helm install security-observability ./helm-chart -n security
```

### Slack/PagerDuty Integration
Update `alertmanager/alertmanager.yml` with real webhook URLs:
```yaml
slack_configs:
  - api_url: 'https://hooks.slack.com/services/YOUR/WEBHOOK/URL'
    channel: '#security-alerts'
```

## Development

### Modify Metrics
Edit `exporter/security_exporter.py`:
- Add new metrics using `prometheus_client`
- Restart exporter: `docker compose restart security_exporter`

### Update Dashboards
Edit JSON files in `grafana/dashboards/` and re-import or use Grafana UI.

### Add Alert Rules
Edit `prometheus/alerts.yml` and restart Prometheus:
```bash
docker compose restart prometheus
```

## Security Considerations

- Change default Grafana password in production
- Use real Slack/PagerDuty webhooks (not placeholders)
- Implement authentication for Prometheus and Alertmanager
- Use TLS for all external communications
- Restrict dashboard access with RBAC

## License

MIT

## Support

For issues or enhancements, refer to individual component documentation:
- [Prometheus](https://prometheus.io/docs/)
- [Grafana](https://grafana.com/docs/)
- [Alertmanager](https://prometheus.io/docs/alerting/latest/overview/)
- [Loki](https://grafana.com/docs/loki/latest/)
