# app/config.py
from dataclasses import dataclass
from pathlib import Path
from typing import List
import os

try:
    # Carga opcional de .env si python-dotenv está instalado
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass


@dataclass
class Settings:
    services: List[str]
    cpu_threshold: float
    mem_threshold: float
    disk_threshold: float
    log_dir: Path
    log_level: str
    alerts_file: Path
    disk_path: str


def load_settings() -> Settings:
    services_raw = os.getenv("MONITOR_SERVICES", "nginx,ssh,docker")
    services = [s.strip() for s in services_raw.split(",") if s.strip()]

    cpu_threshold = float(os.getenv("MONITOR_CPU_THRESHOLD", "80"))
    mem_threshold = float(os.getenv("MONITOR_MEM_THRESHOLD", "80"))
    disk_threshold = float(os.getenv("MONITOR_DISK_THRESHOLD", "90"))

    log_dir = Path(os.getenv("MONITOR_LOG_DIR", "logs"))
    log_level = os.getenv("MONITOR_LOG_LEVEL", "INFO").upper()

    alerts_env = os.getenv("MONITOR_ALERTS_FILE", "")
    if alerts_env:
        alerts_file = Path(alerts_env)
    else:
        alerts_file = log_dir / "alerts.log"

    disk_path = os.getenv("MONITOR_DISK_PATH", "/")

    return Settings(
        services=services,
        cpu_threshold=cpu_threshold,
        mem_threshold=mem_threshold,
        disk_threshold=disk_threshold,
        log_dir=log_dir,
        log_level=log_level,
        alerts_file=alerts_file,
        disk_path=disk_path,
    )