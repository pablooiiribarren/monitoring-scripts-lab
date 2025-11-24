# monitoring-scripts-lab

Laboratorio sencillo de monitorización para entornos Linux, pensado para demostrar habilidades de **automatización**, **scripting** y **monitorización básica** orientadas a un perfil junior de **Sistemas / DevOps / Cloud**.

El proyecto incluye:

- Script principal en **Python** para checks de servicios y métricas de sistema.
- Script alternativo en **Bash** para chequeos rápidos de servicios.
- Configuración mediante **variables de entorno** (`.env`).
- **Logging profesional** a fichero y consola.
- Sistema de **alertas simples** basado en logs y fichero dedicado.

---

## 1. Arquitectura del proyecto

```bash
monitoring-scripts-lab/
├─ app/
│  ├─ __init__.py
│  ├─ config.py          # Configuración (env/.env)
│  ├─ logger.py          # Configuración de logging
│  ├─ checks.py          # Funciones de monitorización
│  └─ monitor.py         # Script principal (entrypoint)
├─ scripts/
│  └─ quick_service_check.sh   # Script Bash de chequeo rápido
├─ logs/                 # (se crea en runtime)
├─ .env.example          # Ejemplo de configuración
├─ requirements.txt      # Dependencias Python
├─ .gitignore
└─ README.md
```

## 2. Requisitos
- Sistema operativo: Linux (se asume systemd y /proc disponible).
- Python 3.9+.
- Opcional: python3-venv instalado para crear entorno virtual.

## 3. Instalación
```bash
# Clonar el repositorio
git clone https://github.com/tu-usuario/monitoring-scripts-lab.git
cd monitoring-scripts-lab

# (Opcional) Crear entorno virtual
python -m venv .venv
source .venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt

# Crear fichero .env a partir del ejemplo
cp .env.example .env
# Editar .env con tus servicios y umbrales
```

## 4. Configuración
El proyecto se configura mediante variables de entorno. Lo más cómodo es usar un fichero .env:
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
- MONITOR_SERVICES: lista de servicios gestionados por systemd a monitorizar.
- MONITOR_CPU_THRESHOLD: umbral de alerta sobre el load average a 1 minuto.
- MONITOR_MEM_THRESHOLD: umbral de uso de memoria en %.
- MONITOR_DISK_THRESHOLD: umbral de uso de disco en %.
- MONITOR_DISK_PATH: punto de montaje a monitorizar (ej: /, /data).
- MONITOR_LOG_DIR: carpeta donde se guardan los logs.
- MONITOR_ALERTS_FILE: fichero de alertas (por defecto logs/alerts.log).

## 5. Uso
### 5.1 Ejecución del monitor en Python
```bash
# Desde la raíz del proyecto
python -m app.monitor
```
- El script ejecuta una pasada de monitorización:
    - Comprueba cada servicio configurado.
    - Lee métricas de CPU (load avg), memoria y disco.
    - Registra el estado en logs/monitor.log.
    - Genera alertas si se superan umbrales o un servicio está caído.

Código de salida:
- 0 → sin alertas.
- 1 → se ha detectado al menos una alerta o error.
Ejemplo de uso en cron (ejecutar cada 5 minutos):
```bash
*/5 * * * * cd /ruta/a/monitoring-scripts-lab && .venv/bin/python -m app.monitor >> /var/log/monitoring-cron.log 2>&1
```
### 5.2 Script rápido en Bash
```bash
# Chequeo rápido de servicios por defecto
./scripts/quick_service_check.sh

# Chequeo rápido de servicios personalizados
./scripts/quick_service_check.sh nginx ssh docker
```

## 6. Ejemplos de salida
### 6.1 Log de monitorización (logs/monitor.log)
```bash
2025-01-01 10:00:00 | INFO | === Inicio de ejecución de monitorización ===
2025-01-01 10:00:00 | INFO | Servicio 'nginx' activo.
2025-01-01 10:00:00 | WARNING | [ALERT] Servicio 'docker' NO está activo.
2025-01-01 10:00:00 | INFO | CPU load (1m): 0.42
2025-01-01 10:00:00 | INFO | Uso de memoria: 63.21%
2025-01-01 10:00:00 | INFO | Uso de disco (/): 71.34%
2025-01-01 10:00:00 | INFO | === Fin de ejecución de monitorización ===
```

### 6.2 Fichero de alertas (logs/alerts.log)
```bash
Servicio 'docker' NO está activo.
Uso de disco alto en /data: 92.15% (umbral 90.0%)
```

### 6.3 Script Bash
```bash
$ ./scripts/quick_service_check.sh nginx ssh docker
Chequeo rápido de servicios: nginx ssh docker
-----------------------------------
[OK]   nginx está activo
[OK]   ssh está activo
[FAIL] docker NO está activo
```

## 7. Cómo añadir nuevos checks
Los checks de sistema viven en app/checks.py. Para añadir un nuevo check:
- Crear una nueva función en checks.py, por ejemplo:
```bash
def read_swap_usage_percent() -> float:
    # Leer /proc/meminfo y calcular % de uso de swap
    ...
```
- Importar la función en app/monitor.py:
```bash
from app.checks import read_swap_usage_percent
```
- Integrar la llamada en run_once() y añadir la lógica de alerta:
```bash
swap_usage = read_swap_usage_percent()
logger.info("Uso de swap: %.2f%%", swap_usage)

if swap_usage >= 50.0:
    msg = f"Uso de swap alto: {swap_usage:.2f}% (umbral 50%)"
    send_alert(logger, settings.alerts_file, msg)
```
De esta forma el proyecto se mantiene extensible y alineado con buenas prácticas de DevOps: código modular y configuración externa.

## 8. Mejoras futuras sugeridas
Algunas extensiones que podrían formar parte de futuras iteraciones:
- Exportar métricas para Prometheus (ej. exponiendo un endpoint HTTP con prometheus_client) y visualizarlas en Grafana.
- Alertas vía Telegram / Slack / email, usando webhooks o SMTP.
- Containerización con Docker:
    - Imagen ligera que ejecute el monitor.
    - Montaje de volúmenes para logs.
- Scheduler interno:
    - Ejecutar la monitorización en bucle con intervalos configurables.
- Integración con systemd:
    - Crear un systemd service y un timer para ejecutar el script.
- Gestión de multi-host:
    - Desplegar agente ligero en varios servidores y enviar métricas a un servidor central.
    - Tests automatizados con pytest y GitHub Actions para CI.