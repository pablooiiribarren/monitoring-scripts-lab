# monitoring-scripts-lab

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)]()
[![Status](https://img.shields.io/badge/Status-Active-success.svg)]()
[![Linux](https://img.shields.io/badge/Platform-Linux-orange.svg)]()
[![License](https://img.shields.io/badge/License-MIT-lightgrey.svg)]()
[![CI](https://github.com/pablooiiribarren/monitoring-scripts-lab/actions/workflows/ci.yml/badge.svg)]()

A lightweight monitoring lab for Linux environments, built to demonstrate 
**automation**, **scripting** and **basic monitoring** skills for junior 
**Systems / DevOps / Cloud** profiles.

The project includes:

- Main **Python** script for service checks and system metrics
- Alternative **Bash** script for quick service checks
- Configuration via **environment variables** (`.env`)
- **Professional logging** to file and console
- Simple **alerting system** based on logs and a dedicated alerts file

---

## 1. Project Structure

```bash
monitoring-scripts-lab/
├─ app/
│  ├─ __init__.py
│  ├─ config.py          # Configuration (env/.env)
│  ├─ logger.py          # Logging setup
│  ├─ checks.py          # Monitoring functions
│  └─ monitor.py         # Main script (entrypoint)
├─ scripts/
│  └─ quick_service_check.sh   # Quick Bash check script
├─ logs/                 # (created at runtime)
├─ .env.example          # Configuration example
├─ requirements.txt      # Python dependencies
├─ .gitignore
└─ README.md
```

## 2. Requirements

- OS: Linux (systemd and /proc assumed available)
- Python 3.9+
- Optional: python3-venv for virtual environment support

## 3. Installation

```bash
# Clone the repository
git clone https://github.com/pablooiiribarren/monitoring-scripts-lab.git
cd monitoring-scripts-lab

# (Optional) Create virtual environment
python -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env file from example
cp .env.example .env
# Edit .env with your services and thresholds
```

## 4. Configuration

The project is configured via environment variables. The easiest way is to use a `.env` file:

```bash
MONITOR_SERVICES=nginx,ssh,docker
MONITOR_CPU_THRESHOLD=4.0
MONITOR_MEM_THRESHOLD=80.0
MONITOR_DISK_THRESHOLD=90.0
MONITOR_LOG_DIR=logs
MONITOR_LOG_LEVEL=INFO
MONITOR_DISK_PATH=/
# MONITOR_ALERTS_FILE=/var/log/monitoring_alerts.log
```

| Variable | Description |
|----------|-------------|
| `MONITOR_SERVICES` | Comma-separated list of systemd services to monitor |
| `MONITOR_CPU_THRESHOLD` | Alert threshold for 1-minute load average |
| `MONITOR_MEM_THRESHOLD` | Memory usage alert threshold (%) |
| `MONITOR_DISK_THRESHOLD` | Disk usage alert threshold (%) |
| `MONITOR_DISK_PATH` | Mount point to monitor (e.g. `/`, `/data`) |
| `MONITOR_LOG_DIR` | Folder where logs are stored |
| `MONITOR_ALERTS_FILE` | Alerts file (default: `logs/alerts.log`) |

## 5. Usage

### 5.1 Python monitor

Single run:
```bash
python -m app.monitor
```

Continuous loop mode:
```bash
python -m app.monitor --loop --interval 10
```

Each run:
- Checks every configured service
- Reads CPU (load avg), memory and disk metrics
- Logs status to `logs/monitor.log`
- Generates alerts if thresholds are exceeded or a service is down

Exit codes:
- `0` → no alerts
- `1` → at least one alert or error detected

Cron example (every 5 minutes):
```bash
*/5 * * * * cd /path/to/monitoring-scripts-lab && .venv/bin/python -m app.monitor >> /var/log/monitoring-cron.log 2>&1
```

### 5.2 Quick Bash check

```bash
# Default services
./scripts/quick_service_check.sh

# Custom services
./scripts/quick_service_check.sh nginx ssh docker
```

## 6. Output examples

### Monitor log (`logs/monitor.log`)
```bash
2025-01-01 10:00:00 | INFO    | === Monitoring run started ===
2025-01-01 10:00:00 | INFO    | Service 'nginx' is active.
2025-01-01 10:00:00 | WARNING | [ALERT] Service 'docker' is NOT active.
2025-01-01 10:00:00 | INFO    | CPU load (1m): 0.42
2025-01-01 10:00:00 | INFO    | Memory usage: 63.21%
2025-01-01 10:00:00 | INFO    | Disk usage (/): 71.34%
2025-01-01 10:00:00 | INFO    | === Monitoring run finished ===
```

### Alerts file (`logs/alerts.log`)
```bash
Service 'docker' is NOT active.
High disk usage on /data: 92.15% (threshold 90.0%)
```

### Bash script output
```bash
Quick service check: nginx ssh docker
[OK]   nginx is active
[OK]   ssh is active
[FAIL] docker is NOT active
```

## 7. Adding new checks

All system checks live in `app/checks.py`. To add a new one:

1. Create a new function in `checks.py`:
```python
def read_swap_usage_percent() -> float:
    # Read /proc/meminfo and calculate swap usage %
    ...
```

2. Import it in `app/monitor.py`:
```python
from app.checks import read_swap_usage_percent
```

3. Call it inside `run_once()` and add alert logic:
```python
swap_usage = read_swap_usage_percent()
logger.info("Swap usage: %.2f%%", swap_usage)

if swap_usage >= 50.0:
    msg = f"High swap usage: {swap_usage:.2f}% (threshold 50%)"
    send_alert(logger, settings.alerts_file, msg)
```

The project stays extensible and aligned with DevOps good practices: 
modular code and external configuration.

## 8. Planned improvements

- Metrics export to Prometheus via `prometheus_client`
- Grafana dashboard
- External alerts via Telegram, Slack, Discord or email
- Dockerisation (lightweight Python image + mounted log volumes)
- Advanced internal scheduler (ticks, jitter, backoff)
- systemd integration (`monitor.service` + `monitor.timer`)
- Multi-host monitoring (agent + central server)
- Extended test suite (pytest + mocks)
- Extended CI with static analysis (ruff, black, mypy)
