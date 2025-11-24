#!/usr/bin/env bash
set -euo pipefail

# Uso:
#   ./scripts/quick_service_check.sh           # usa defaults
#   ./scripts/quick_service_check.sh nginx ssh docker

SERVICES="${*:-nginx ssh docker}"

if ! command -v systemctl >/dev/null 2>&1; then
  echo "ERROR: systemctl no está disponible en este sistema." >&2
  exit 1
fi

echo "Chequeo rápido de servicios: $SERVICES"
echo "-----------------------------------"

for svc in $SERVICES; do
  if systemctl is-active --quiet "$svc"; then
    echo "[OK]   $svc está activo"
  else
    echo "[FAIL] $svc NO está activo"
  fi
done
