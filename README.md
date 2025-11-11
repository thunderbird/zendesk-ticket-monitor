# Spike Monitor

Zero-ops spike detection for Zendesk.

## Quick Start

1. Install: `pip install -e .`
2. Configure: Edit `config.yaml`
3. Set secrets: `export ZENDESK_API_TOKEN=your_token`
4. Run: `spike-monitor run-once --config config.yaml`

## Deployment

- GitHub Actions: runs every 5 minutes
- Docker: `docker-compose up`
- Cron: `*/5 * * * * spike-monitor run-once`
