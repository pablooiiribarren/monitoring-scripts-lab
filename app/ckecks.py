# app/checks.py
import os
import shutil
import subprocess
from typing import Dict


class MonitoringError(Exception):
    """Excepción genérica de monitorización."""


def check_service(service: str) -> bool:
    """
    Devuelve True si el servicio está activo (systemd).
    Lanza MonitoringError si no existe systemctl.
    """
    if shutil.which("systemctl") is None:
        raise MonitoringError("systemctl no está disponible en este sistema.")

    result = subprocess.run(
        ["systemctl", "is-active", service],
        capture_output=True,
        text=True,
    )
    return result.returncode == 0 and result.stdout.strip() == "active"


def read_cpu_load() -> float:
    """
    Devuelve el load average a 1 minuto (proxy de carga CPU).
    """
    try:
        with open("/proc/loadavg", "r", encoding="utf-8") as f:
            parts = f.read().split()
        # Primer campo = load average 1 min
        return float(parts[0])
    except Exception as exc:  # noqa: BLE001
        raise MonitoringError(f"No se pudo leer /proc/loadavg: {exc}") from exc


def read_memory_usage_percent() -> float:
    """
    Devuelve el uso de memoria RAM en porcentaje.
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
        raise MonitoringError(f"No se pudo leer /proc/meminfo: {exc}") from exc


def read_disk_usage_percent(path: str = "/") -> float:
    """
    Devuelve el uso de disco en porcentaje para el path dado.
    """
    try:
        st = os.statvfs(path)
        total = st.f_blocks * st.f_frsize
        available = st.f_bavail * st.f_frsize
        used = total - available
        return (used / total) * 100 if total > 0 else 0.0
    except Exception as exc:  # noqa: BLE001
        raise MonitoringError(f"No se pudo obtener uso de disco para {path}: {exc}") from exc
