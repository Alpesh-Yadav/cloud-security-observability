#!/bin/bash
set -e
kubectl port-forward svc/monitoring-grafana 3000:80 -n monitoring >/tmp/port-forward-grafana.log 2>&1 &
kubectl port-forward svc/monitoring-kube-prometheus-prometheus 9090:9090 -n monitoring >/tmp/port-forward-prometheus.log 2>&1 &
kubectl port-forward svc/monitoring-kube-prometheus-alertmanager 9093:9093 -n monitoring >/tmp/port-forward-alertmanager.log 2>&1 &
kubectl port-forward svc/security-exporter 8000:8000 -n security >/tmp/port-forward-exporter.log 2>&1 &
echo "All services port-forwarded"
echo "Grafana: http://localhost:3000 (admin/admin123)"
echo "Prometheus: http://localhost:9090"
echo "Alertmanager: http://localhost:9093"
echo "Exporter: http://localhost:8000/metrics"
