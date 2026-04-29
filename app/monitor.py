# app/monitor.py
from pathlib import Path
import sys
import time
import argparse

from app.config import load_settings
from app.logger import setup_logging
from app.checks import (
    MonitoringError,
    check_service,
    read_cpu_load,
    read_disk_usage_percent,
    read_memory_usage_percent,
)


def send_alert(logger, alerts_file: Path, message: str) -> None:
    """
    Send a simple alert: 
    - Log at WARNING level 
    - Append to the alerts file
    """
    logger.warning("[ALERT] %s", message)

    try:
        alerts_file.parent.mkdir(parents=True, exist_ok=True)
        with alerts_file.open("a", encoding="utf-8") as f:
            f.write(message + "\n")
    except Exception as exc:  # noqa: BLE001
        logger.error("Could not write to alert file: %r", exc)


def run_once() -> int:
    """
    Run a monitoring pass. 
    Returns 0 if everything OK, 1 if there were any alerts or errors.
    """
    settings = load_settings()
    logger = setup_logging(settings.log_dir, settings.log_level)

    logger.info("=== Inicio de ejecución de monitorización ===")

    # Modo compatibilidad: solo pensado para Linux (systemd + /proc)
    if not sys.platform.startswith("linux"):
        logger.warning(
            "Non-Linux operating system detected." 
            "This project is designed for Linux (systemd + /proc)." 
            "Service and metrics checks are omitted in compatibility mode."
        )
        logger.info("=== End of monitoring run (compatibility mode) ===")
        return 0

    exit_code = 0

    # --- Checks de servicios ---
    for service in settings.services:
        if not service:
            continue

        try:
            ok = check_service(service)
            if ok:
                logger.info("Service '%s' active.", service)
            else:
                msg = f"Service '{service}' is NOT active."
                send_alert(logger, settings.alerts_file, msg)
                exit_code = 1
        except MonitoringError as exc:
            msg = f"Error checking service '{service}': {exc}"
            send_alert(logger, settings.alerts_file, msg)
            exit_code = 1

    # --- Métricas de sistema ---
    try:
        cpu_load = read_cpu_load()
        mem_usage = read_memory_usage_percent()
        disk_usage = read_disk_usage_percent(settings.disk_path)

        logger.info("CPU load (1m): %.2f", cpu_load)
        logger.info("Memory usage: %.2f%%", mem_usage)
        logger.info("Disk usage (%s): %.2f%%", settings.disk_path, disk_usage)

        if cpu_load >= settings.cpu_threshold:
            msg = f"CPU load high: {cpu_load:.2f} (threshold {settings.cpu_threshold})"
            send_alert(logger, settings.alerts_file, msg)
            exit_code = 1

        if mem_usage >= settings.mem_threshold:
            msg = f"Memory usage high: {mem_usage:.2f}% (threshold {settings.mem_threshold}%)"
            send_alert(logger, settings.alerts_file, msg)
            exit_code = 1

        if disk_usage >= settings.disk_threshold:
            msg = (
                f"High disk usage {settings.disk_path}: "
                f"{disk_usage:.2f}% (threshold {settings.disk_threshold}%)"
            )
            send_alert(logger, settings.alerts_file, msg)
            exit_code = 1

    except MonitoringError as exc:
        msg = f"Error reading system metrics: {exc}"
        send_alert(logger, settings.alerts_file, msg)
        exit_code = 1

    logger.info("=== End of monitoring run ===")
    return exit_code


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Basic monitoring of services and system resources."
    )
    parser.add_argument(
        "--loop",
        action="store_true",
        help="Run in continuous loop.",
    )
    parser.add_argument(
        "--interval",
        type=int,
        default=60,
        help="Interval in seconds between executions in --loop mode (default: 60).",
    )

    args = parser.parse_args()

    if not args.loop:
        # Modo normal: una pasada
        raise SystemExit(run_once())

    # Modo loop: se queda corriendo
    while True:
        exit_code = run_once()
        # Aquí podrías tomar decisiones según exit_code (ej. parar si hay error grave)
        time.sleep(max(1, args.interval))


if __name__ == "__main__":
    main()
