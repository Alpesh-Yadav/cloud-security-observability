# Runbook: Exporter Down

## Symptoms
- `/metrics` endpoint unreachable
- `up{job="security-exporter"}` is 0
- Grafana panels empty for exporter metrics

## Impact
- Security observability is degraded
- Alerting may stop
- Dashboards lose data continuity

## Diagnose
- `kubectl get pods -n security`
- `kubectl describe pod -l app=security-exporter -n security`
- `kubectl logs -l app=security-exporter -n security`
- `kubectl get svc -n security`
- `helm status security-exporter -n security`

## Fix
1. Restart the deployment.
2. Validate `/metrics` connectivity.
3. Check LocalStack health and AWS endpoint reachability.
4. Rebuild and redeploy the exporter image if necessary.
