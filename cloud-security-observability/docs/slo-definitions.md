# SLO Definitions

## SLIs

| SLI | PromQL | Description |
| --- | --- | --- |
| Exporter availability | `up{job="security-exporter"}` | Fraction of successful exporter scrapes |
| Alertmanager latency | `histogram_quantile(0.99, rate(alertmanager_http_request_duration_seconds_bucket[5m]))` | 99th percentile Alertmanager latency |
| Prometheus scrape success | `sum(rate(prometheus_scrape_duration_seconds_count[5m])) / sum(rate(prometheus_scrape_duration_seconds_count[5m]) + prometheus_scrape_failures_total[5m]))` | Scrape success rate |

## SLOs

| SLO | Target | 30-day error budget |
| --- | --- | --- |
| Exporter uptime | 99.9% | 43.2 minutes |
| Alert delivery reliability | 99.9% | 43.2 minutes |
| Prometheus scrape success | 99.9% | 43.2 minutes |

## Multi-burn-rate alert

A multi-burn-rate alert compares short-term error consumption to the long-term budget.

Example math:
- 30-day budget = 0.1% downtime = 43.2 minutes
- 1-hour budget = 0.1% * (1/720) = 10.8 seconds
- If the service is down for 30 seconds in one hour, burn rate = 30 / 10.8 ≈ 2.8
- Burn rate > 2 means errors are consuming budget too fast.
