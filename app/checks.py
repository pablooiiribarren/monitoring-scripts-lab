# app/checks.py
import os
import shutil
import subprocess
from typing import Dict


class MonitoringError(Exception):
    """Generic monitoring exception."""


def check_service(service: str) -> bool:
    """
    Returns True if the service is active (systemd). 
    Raises MonitoringError if systemctl does not exist.
    """
    if shutil.which("systemctl") is None:
        raise MonitoringError("systemctl is not available on this system.")

    result = subprocess.run(
        ["systemctl", "is-active", service],
        capture_output=True,
        text=True,
    )
    return result.returncode == 0 and result.stdout.strip() == "active"


def read_cpu_load() -> float:
    """
    Returns the load average at 1 minute (CPU load proxy).
    """
    try:
        with open("/proc/loadavg", "r", encoding="utf-8") as f:
            parts = f.read().split()
        # Primer campo = load average 1 min
        return float(parts[0])
    except Exception as exc:  # noqa: BLE001
        raise MonitoringError(f"Could not read /proc/loadavg: {exc}") from exc


def read_memory_usage_percent() -> float:
    """
    Returns the RAM memory usage in percentage.
    """
    try:
        data: Dict[str, int] = {}
        with open("/proc/meminfo", "r", encoding="utf-8") as f:
            for line in f:
                key, value, *_ = line.split()
                data[key.rstrip(":")] = int(value)  # kB

        mem_total = data["MemTotal"]
        mem_available = data.get("MemAvailable", data.get("MemFree", 0))
        used = mem_total - mem_available
        return (used / mem_total) * 100
    except Exception as exc:  # noqa: BLE001
        raise MonitoringError(f"Could not read /proc/meminfo: {exc}") from exc


def read_disk_usage_percent(path: str = "/") -> float:
    """
    Returns the disk usage in percentage for the given path.
    """
    try:
        st = os.statvfs(path)
        total = st.f_blocks * st.f_frsize
        available = st.f_bavail * st.f_frsize
        used = total - available
        return (used / total) * 100 if total > 0 else 0.0
    except Exception as exc:  # noqa: BLE001
        raise MonitoringError(f"Could not get disk usage for {path}: {exc}") from exc
