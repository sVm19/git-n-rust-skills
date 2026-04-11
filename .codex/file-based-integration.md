---
name: file-based-integration
description: Implement Stageira's file-based integration strategy: exporting metrics to Datadog, Prometheus, and Slack without using any external APIs. Use when adding export targets, implementing the --export-to-datadog or --export-to-prometheus flags, writing webhook triggers, or explaining how Stageira integrates with third-party tools without network access beyond one-direction pushes. Triggers on \"datadog export\", \"prometheus metrics\", \"slack webhook\", \"file-based integration\", \"export pipeline\", or \"push metrics\".
---


# File-Based Integration

Stageira's integration strategy is file-based, not API-based. The tool writes files that other systems consume. This is what makes it enterprise-safe.

## The Core Insight

```
Traditional SaaS approach:
  Your code → GitHub API → Third-party dashboard
  (Requires OAuth, internet, rate limits)

Stageira approach:
  .git/ → stageira binary → JSON/CSV file → tool reads locally
  (Zero network calls from the analysis step)
```

## Datadog Export

```python
# src/datadog_export.py
import json
from pathlib import Path
from datetime import datetime

def export_to_datadog_json(metrics: dict, output_path: Path):
    """
    Write metrics in Datadog's custom metrics JSON format.
    Enterprise teams feed this file to the Datadog agent via file tail or API.
    """
    series = []
    
    for file, churn in metrics["churn"]:
        series.append({
            "metric": "stageira.code_churn",
            "points": [[int(datetime.now().timestamp()), churn]],
            "tags": [f"file:{file}", "source:stageira"],
            "type": "gauge",
        })
    
    series.append({
        "metric": "stageira.bus_factor.min",
        "points": [[int(datetime.now().timestamp()), metrics["min_bus_factor"]]],
        "tags": ["source:stageira"],
        "type": "gauge",
    })
    
    payload = {"series": series}
    output_path.write_text(json.dumps(payload, indent=2))
    return output_path
```

**Usage in CI:**
```bash
stageira analyze --export-to-datadog metrics.json
# Then the Datadog agent picks up metrics.json automatically
```

## Prometheus Export

```python
# src/prometheus_metrics.py
from pathlib import Path

def export_to_prometheus(metrics: dict, output_path: Path):
    """
    Write OpenMetrics/Prometheus text format.
    Prometheus node_exporter can scrape from a file.
    """
    lines = [
        "# HELP stageira_code_churn File edit frequency",
        "# TYPE stageira_code_churn gauge",
    ]
    
    for entry in metrics["churn"]:
        safe_file = entry["file"].replace("/", "_").replace(".", "_")
        lines.append(
            f'stageira_code_churn{{file="{entry["file"]}"}} {entry["churn_score"]}'
        )
    
    lines.append("")
    lines.append("# HELP stageira_bus_factor Minimum bus factor across all files")
    lines.append("# TYPE stageira_bus_factor gauge")
    lines.append(f"stageira_bus_factor {metrics['min_bus_factor']}")
    
    output_path.write_text("\n".join(lines))
```

**Prometheus scrape config:**
```yaml
- job_name: stageira
  static_configs:
    - targets: ['localhost:9100']
  metrics_path: /metrics
  # OR use file-based collector in node_exporter
```

## Slack Webhook Trigger

```python
# src/slack_webhook.py
import urllib.request
import json

def send_slack_alert(webhook_url: str, metrics: dict, thresholds: dict):
    """
    Fire a Slack webhook when alert thresholds are exceeded.
    Only outbound HTTP call in the entire pipeline.
    """
    alerts = []
    
    if metrics["min_bus_factor"] < thresholds["bus_factor_min"]:
        alerts.append(
            f"⚠️ Bus factor is {metrics['min_bus_factor']} "
            f"(threshold: {thresholds['bus_factor_min']})"
        )
    
    if not alerts:
        return  # no alerts, no webhook call
    
    payload = {
        "text": f"*Stageira Alert* for `{metrics['repo']}`\n" + "\n".join(alerts)
    }
    
    req = urllib.request.Request(
        webhook_url,
        data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json"},
    )
    urllib.request.urlopen(req)
```

## CLI Flags

```bash
# All integration exports
stageira analyze . --export-to-datadog ./dd_metrics.json
stageira analyze . --export-to-prometheus ./metrics.txt
stageira analyze . --webhook https://hooks.slack.com/T.../B.../xxx
stageira analyze . --format json --out report.json  # basic JSON
```

## Security Note

The only outbound HTTP call is the Slack webhook (optional). Datadog and Prometheus integrations write local files — zero network. Enterprise security teams can audit this in < 5 minutes.
