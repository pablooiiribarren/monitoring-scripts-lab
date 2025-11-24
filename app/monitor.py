# app/monitor.py
from pathlib import Path

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
    Envía una alerta simple:
    - Log a nivel WARNING
    - Append al fichero de alertas
    """
    logger.warning("[ALERT] %s", message)

    try:
        alerts_file.parent.mkdir(parents=True, exist_ok=True)
        with alerts_file.open("a", encoding="utf-8") as f:
            f.write(message + "\n")
    except Exception as exc:  # noqa: BLE001
        logger.error("No se pudo escribir en el fichero de alertas: %r", exc)


def run_once() -> int:
    """
    Ejecuta una pasada de monitorización.
    Devuelve 0 si todo OK, 1 si hubo alguna alerta o error.
    """
    settings = load_settings()
    logger = setup_logging(settings.log_dir, settings.log_level)

    logger.info("=== Inicio de ejecución de monitorización ===")

    exit_code = 0

    # --- Checks de servicios ---
    for service in settings.services:
        try:
            ok = check_service(service)
            if ok:
                logger.info("Servicio '%s' activo.", service)
            else:
                msg = f"Servicio '{service}' NO está activo."
                send_alert(logger, settings.alerts_file, msg)
                exit_code = 1
        except MonitoringError as exc:
            msg = f"Error al comprobar servicio '{service}': {exc}"
            send_alert(logger, settings.alerts_file, msg)
            exit_code = 1

    # --- Métricas de sistema ---
    try:
        cpu_load = read_cpu_load()
        mem_usage = read_memory_usage_percent()
        disk_usage = read_disk_usage_percent(settings.disk_path)

        logger.info("CPU load (1m): %.2f", cpu_load)
        logger.info("Uso de memoria: %.2f%%", mem_usage)
        logger.info("Uso de disco (%s): %.2f%%", settings.disk_path, disk_usage)

        # Umbrales (simplificados: usamos load avg como proxy de % CPU)
        if cpu_load >= settings.cpu_threshold:
            msg = f"CPU load alto: {cpu_load:.2f} (umbral {settings.cpu_threshold})"
            send_alert(logger, settings.alerts_file, msg)
            exit_code = 1

        if mem_usage >= settings.mem_threshold:
            msg = f"Uso de memoria alto: {mem_usage:.2f}% (umbral {settings.mem_threshold}%)"
            send_alert(logger, settings.alerts_file, msg)
            exit_code = 1

        if disk_usage >= settings.disk_threshold:
            msg = (
                f"Uso de disco alto en {settings.disk_path}: "
                f"{disk_usage:.2f}% (umbral {settings.disk_threshold}%)"
            )
            send_alert(logger, settings.alerts_file, msg)
            exit_code = 1

    except MonitoringError as exc:
        msg = f"Error al leer métricas de sistema: {exc}"
        send_alert(logger, settings.alerts_file, msg)
        exit_code = 1

    logger.info("=== Fin de ejecución de monitorización ===")
    return exit_code


if __name__ == "__main__":
    raise SystemExit(run_once())
