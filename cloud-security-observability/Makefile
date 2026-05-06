.PHONY: help up down logs restart clean test

help:
	@echo "Cloud-Native Security Observability Platform"
	@echo ""
	@echo "Usage:"
	@echo "  make up          - Start the stack"
	@echo "  make down        - Stop the stack"
	@echo "  make restart     - Restart the stack"
	@echo "  make logs        - View logs from all services"
	@echo "  make clean       - Stop stack and remove volumes"
	@echo "  make test-alerts - Test alert generation"

up:
	docker compose up -d
	@echo "Stack started. Access:"
	@echo "  Prometheus: http://localhost:9090"
	@echo "  Grafana: http://localhost:3000 (admin/admin)"
	@echo "  Alertmanager: http://localhost:9093"

down:
	docker compose down

restart: down up

logs:
	docker compose logs -f

clean:
	docker compose down -v
	@echo "Stack removed with volumes"

test-alerts:
	@echo "Testing alerts..."
	curl -s http://localhost:9090/api/v1/alerts | jq '.data.alerts[] | {name: .labels.alertname, state: .state}'
	@echo ""
	@echo "Alertmanager alerts:"
	curl -s http://localhost:9093/api/v2/alerts | jq '.'
