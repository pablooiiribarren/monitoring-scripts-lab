#!/usr/bin/env bash
set -euo pipefail

# Uso:
#   ./scripts/quick_service_check.sh           # usa defaults
#   ./scripts/quick_service_check.sh nginx ssh docker

SERVICES="${*:-nginx ssh docker}"

if ! command -v systemctl >/dev/null 2>&1; then
  echo "ERROR: systemctl is not available on this system." >&2
  exit 1
fi

echo "Quick service check: $SERVICES"
echo "-----------------------------------"

for svc in $SERVICES; do
  if systemctl is-active --quiet "$svc"; then
    echo "[OK]   $svc is active"
  else
    echo "[FAIL] $svc is NOT active"
  fi
done
