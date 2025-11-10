## README.md (Complete Documentation)

```markdown
# 🚨 Ticket Spike Monitor

**Zero-ops spike detection for Zendesk with cross-functional incident workflow**

Monitor your Zendesk ticket volume in real-time and automatically trigger incident response workflows when traffic spikes above baseline. Designed for simplicity and reliability—runs via cron, GitHub Actions, or any scheduler with no long-lived servers.

## Features

### 🎯 Core Capabilities
- **Smart Detection**: Time-of-day aware baseline using 7-day rolling average
- **Dual Algorithms**: Simple threshold mode or statistical Z-score detection
- **Hysteresis Control**: Cooldown and suppression to prevent alert flapping
- **Multi-Channel Alerts**: Zenduty incidents, generic webhooks, email, Matrix
- **Zero PII**: Redacts ticket subjects by default
- **Rate Limit Resilient**: Handles Zendesk API 429s with exponential backoff

### 🏗️ Architecture
```
┌─────────────┐      ┌──────────────┐      ┌───────────────┐
│  Zendesk    │─────▶│   Detector   │─────▶│  State        │
│  API Client │      │   Engine     │      │  Machine      │
└─────────────┘      └──────────────┘      └───────────────┘
                                                    │
                     ┌──────────────────────────────┘
                     ▼
              ┌─────────────┐
              │ Action Bus  │
              └─────────────┘
                     │
        ┌────────────┼────────────┬────────────┐
        ▼            ▼            ▼            ▼
   ┌─────────┐  ┌─────────┐  ┌───────┐  ┌────────┐
   │Zenduty  │  │Webhooks │  │Email  │  │Matrix  │
   └─────────┘  └─────────┘  └───────┘  └────────┘
```

## Quick Start

### 1. Installation

```bash
# Clone repository
git clone https://github.com/your-org/spike-monitor.git
cd spike-monitor

# Install with pip
pip install -e .

# Or install with dev dependencies
pip install -e ".[dev]"
```

### 2. Configuration

Create `config.yaml`:

```yaml
zendesk:
  subdomain: "mycompany"
  email: "monitor@company.com"
  api_token: "${ZENDESK_API_TOKEN}"

query:
  bucket_minutes: 5
  brands: []  # Empty = all brands
  groups: []
  tags: []

detection:
  mode: "threshold"  # or "zscore"
  multiplier: 2.0
  min_delta: 10
  cooldown_buckets: 3
  suppress_minutes: 30

actions:
  zenduty:
    enabled: true
    integration_key: "${ZENDUTY_KEY}"
  
  webhooks:
    - name: "internal-api"
      url: "https://api.internal/incidents"
      headers:
        Authorization: "Bearer ${WEBHOOK_TOKEN}"

persistence:
  storage: "sqlite"
  sqlite_path: "./data/spike_monitor.db"

observability:
  log_level: "INFO"

privacy:
  redact_ticket_subjects: true
```

### 3. Set Environment Variables

```bash
export ZENDESK_API_TOKEN="your_token"
export ZENDUTY_KEY="your_integration_key"
export WEBHOOK_TOKEN="your_webhook_token"
```

### 4. Run

```bash
# Validate config
spike-monitor validate --config config.yaml

# Test without triggering actions
spike-monitor dry-run --config config.yaml

# Run once (for cron/CI)
spike-monitor run-once --config config.yaml
```

## Detection Algorithms

### Threshold Mode (Recommended for Most Use Cases)

Triggers when:
```
current_count >= max(min_delta, rolling_avg × multiplier)
```

**Example:**
- Rolling average: 45 tickets/5min
- Multiplier: 2.0×
- Current bucket: 110 tickets
- **Result:** ALERT (110 ≥ 45 × 2.0 = 90)

**Best for:** Clear, explainable thresholds that business stakeholders understand.

### Z-Score Mode (Statistical)

Triggers when:
```
(current_count - mean) / stddev >= k
```

**Example:**
- Mean: 45, StdDev: 12
- k threshold: 3.0
- Current bucket: 81 tickets
- Z-score: (81 - 45) / 12 = 3.0
- **Result:** ALERT (z-score ≥ 3.0)

**Best for:** Noisy baselines with high variance.

## Alert Lifecycle

```
NORMAL ──spike──▶ ALERTING ──emit ALERT──▶ ALERTED
                                                │
                                    3 normal buckets
                                                │
                                                ▼
NORMAL ◀──emit ALL-CLEAR── RESOLVING ◀────────┘
```

**Key Properties:**
- **Suppression**: After ALERT, no new alerts for `suppress_minutes`
- **Cooldown**: Requires `cooldown_buckets` consecutive normal buckets before ALL-CLEAR
- **Hysteresis**: Prevents alert flapping

## Action Integrations

### Zenduty (Recommended for Incident Management)

```yaml
actions:
  zenduty:
    enabled: true
    integration_key: "${ZENDUTY_KEY}"
    service_id: "svc_abc123"
```

**Sends:**
- Incident title with severity (P0-P3)
- Current vs. baseline stats
- Zendesk search deep links
- Auto-resolves on ALL-CLEAR

### Generic Webhooks (Vendor-Neutral)

```yaml
actions:
  webhooks:
    - name: "ops-webhook"
      url: "https://yourapi.com/incidents"
      headers:
        Authorization: "Bearer ${TOKEN}"
```

**Payload Schema:**
```json
{
  "event_type": "ALERT",
  "severity": "P1",
  "timestamp": "2025-11-07T14:35:00Z",
  "bucket_start": "2025-11-07T14:30:00Z",
  "current_count": 110,
  "rolling_avg": 45.2,
  "rolling_stddev": 12.3,
  "detector": "threshold",
  "multiplier": 2.0,
  "scope": {"brands": [], "groups": [], "tags": []},
  "links": {
    "zendesk_search": "https://..."
  }
}
```

### Email

```yaml
actions:
  email:
    enabled: true
    from: "alerts@company.com"
    to: ["oncall@company.com"]
    smtp:
      host: "smtp.sendgrid.net"
      port: 587
      username: "apikey"
      password: "${SMTP_PASSWORD}"
```

### Matrix (Chat)

```yaml
actions:
  matrix:
    enabled: true
    homeserver: "https://matrix.org"
    room_id: "!abc123:matrix.org"
    access_token: "${MATRIX_TOKEN}"
```

## Deployment

### GitHub Actions (Recommended)

Create `.github/workflows/spike-monitor.yml`:

```yaml
name: Spike Monitor

on:
  schedule:
    - cron: '*/5 * * * *'  # Every 5 minutes
  workflow_dispatch:  # Manual trigger

jobs:
  monitor:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          pip install -e .
      
      - name: Run monitor
        env:
          ZENDESK_API_TOKEN: ${{ secrets.ZENDESK_API_TOKEN }}
          ZENDUTY_KEY: ${{ secrets.ZENDUTY_KEY }}
        run: |
          spike-monitor run-once --config config.yaml
      
      - name: Upload logs
        if: always()
        uses: actions/upload-artifact@v3
        with:
          name: spike-monitor-logs
          path: logs/
```

**Setup:**
1. Add secrets in repo settings: `ZENDESK_API_TOKEN`, `ZENDUTY_KEY`
2. Commit `config.yaml` (without secrets—use `${ENV_VAR}` syntax)
3. Enable workflow

### Docker

```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY . /app

RUN pip install --no-cache-dir -e .

CMD ["spike-monitor", "run-once", "--config", "config.yaml"]
```

**Build and run:**
```bash
docker build -t spike-monitor .
docker run --rm \
  -e ZENDESK_API_TOKEN=your_token \
  -e ZENDUTY_KEY=your_key \
  -v $(pwd)/data:/app/data \
  spike-monitor
```

### Cron (Self-Hosted)

```bash
# Run every 5 minutes
*/5 * * * * cd /opt/spike-monitor && /usr/bin/python3 -m spike_monitor run-once --config config.yaml >> /var/log/spike-monitor.log 2>&1
```

## Configuration Examples

### Lean (Minimal)

```yaml
zendesk:
  subdomain: "company"
  email: "bot@company.com"
  api_token: "${ZENDESK_API_TOKEN}"

query:
  bucket_minutes: 5

detection:
  mode: "threshold"
  multiplier: 2.0
  min_delta: 15

actions:
  zenduty:
    enabled: true
    integration_key: "${ZENDUTY_KEY}"

persistence:
  storage: "sqlite"
```

### Ops-Light (No External Tools)

```yaml
# Uses only generic webhook + Google Sheets
zendesk:
  subdomain: "company"
  email: "bot@company.com"
  api_token: "${ZENDESK_API_TOKEN}"

query:
  bucket_minutes: 5

detection:
  mode: "zscore"
  z_k: 3.0
  min_delta: 10

actions:
  webhooks:
    - name: "internal"
      url: "https://internal.api/alerts"
  
  matrix:
    enabled: true
    homeserver: "https://matrix.company.com"
    room_id: "!ops:company.com"
    access_token: "${MATRIX_TOKEN}"

persistence:
  storage: "sheets"
  sheets:
    creds_json_env: "GOOGLE_SHEETS_CREDS"
    spreadsheet_id: "1abc..."
```

## Business Hours Support

```yaml
detection:
  # ...
  business_hours:
    enabled: true
    timezone: "America/New_York"
    weekdays: [1, 2, 3, 4, 5]  # Mon-Fri
    start: "09:00"
    end: "17:00"
    thresholds_override:
      multiplier: 1.5  # More sensitive during business hours
```

## Troubleshooting

### "No historical data for baseline"

**Cause:** First run or database empty.

**Solution:** Run `spike-monitor backfill --days 7 --config config.yaml` to populate baseline, or wait 7 days for natural accumulation.

### Rate limiting (429 errors)

**Cause:** Zendesk API limits exceeded.

**Solution:**
- Monitor logs for `X-Rate-Limit-Remaining` headers
- Increase `bucket_minutes` to reduce API calls
- The client auto-retries with backoff

### Alerts not triggering

**Debug steps:**
1. Run `spike-monitor dry-run --config config.yaml` and check logs
2. Verify `rolling_avg` is reasonable (not 0)
3. Lower `multiplier` or `z_k` temporarily to test
4. Check `suppress_minutes`—may be suppressing alerts

### Time zone issues

Zendesk API uses UTC. Ensure your `business_hours.timezone` matches your support team's location.

## Security

### Secrets Management
- ✅ All secrets via environment variables
- ✅ Never commit secrets to git
- ✅ Use GitHub Actions secrets or secret managers

### Privacy
- ✅ `redact_ticket_subjects: true` by default
- ✅ Logs never contain full ticket content
- ✅ Minimal data retention (7-day rolling window)

### Network
- ✅ TLS for all API calls
- ✅ No inbound listeners (push-only architecture)

## Testing

```bash
# Run full test suite
pytest

# With coverage
pytest --cov=spike_monitor --cov-report=html

# Run specific test
pytest tests/test_detectors.py::test_threshold_detector
```

## CLI Reference

### `validate`
Validate configuration schema.
```bash
spike-monitor validate --config config.yaml
```

### `run-once`
Run one detection cycle (for cron/CI).
```bash
spike-monitor run-once --config config.yaml
```

### `dry-run`
Test detection logic without triggering actions.
```bash
spike-monitor dry-run --config config.yaml
```

### `backfill`
Rebuild historical baseline.
```bash
spike-monitor backfill --days 14 --config config.yaml
```

## Contributing

1. Install dev dependencies: `pip install -e ".[dev]"`
2. Run tests: `pytest`
3. Format code: `black spike_monitor tests`
4. Lint: `ruff check spike_monitor`
5. Type check: `mypy spike_monitor`

## License

MIT License - see LICENSE file

## Support

- Issues: https://github.com/your-org/spike-monitor/issues
- Docs: https://docs.company.com/spike-monitor
- Slack: #incident-response

---

**Built with ❤️ by Support Engineering**
```

---

## 📄 Sample Config Files

### config.sample.yaml
*(Full-featured example - see README above)*

### config.lean.yaml
```yaml
zendesk:
  subdomain: "mycompany"
  email: "monitor@company.com"
  api_token: "${ZENDESK_API_TOKEN}"

query:
  bucket_minutes: 5

detection:
  mode: "threshold"
  multiplier: 2.0
  min_delta: 15

actions:
  zenduty:
    enabled: true
    integration_key: "${ZENDUTY_KEY}"

persistence:
  storage: "sqlite"
```

### config.ops-light.yaml
*(See README "Ops-Light" example above)*

---

## 🐳 Dockerfile

```dockerfile
FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy and install Python dependencies
COPY pyproject.toml ./
COPY spike_monitor ./spike_monitor

RUN pip install --no-cache-dir -e .

# Create data directory
RUN mkdir -p /app/data

# Run as non-root
RUN useradd -m -u 1000 monitor && chown -R monitor:monitor /app
USER monitor

CMD ["spike-monitor", "run-once", "--config", "config.yaml"]
```

---

## ⚙️ .github/workflows/spike-monitor.yml

*(See README deployment section for complete workflow)*

---

## 🧪 tests/conftest.py

```python
"""Pytest configuration and fixtures."""

import pytest
from spike_monitor.config import Config


@pytest.fixture
def sample_config():
    """Minimal valid config for testing."""
    return Config(
        zendesk={
            "subdomain": "test",
            "email": "test@test.com",
            "api_token": "test_token",
        },
        query={"bucket_minutes": 5},
        detection={"mode": "threshold"},
        actions={},
        routing={},
        persistence={"storage": "memory"},
        observability={},
        privacy={},
    )
```
