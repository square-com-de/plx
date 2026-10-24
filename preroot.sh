#!/bin/bash
# LoxBerry purges plugin directories on upgrade. Stop only our writer first.
set -euo pipefail
trap 'exit 2' ERR
PDIR=${3:?Plugin folder missing}
[[ "$PDIR" =~ ^porsche2lox[0-9]*$ ]] || exit 2
UNIT="porsche2lox-${PDIR}.service"
if systemctl cat "$UNIT" >/dev/null 2>&1; then
    systemctl stop "$UNIT"
fi
