#!/bin/bash
set -euo pipefail
PDIR=${3:?Plugin folder missing}
[[ "$PDIR" =~ ^porsche2lox[0-9]*$ ]] || exit 1
UNIT="porsche2lox-${PDIR}.service"
systemctl disable --now "$UNIT" || true
rm -f "/etc/systemd/system/$UNIT"
systemctl daemon-reload
# LoxBerry removes only this plugin's directories. No access to the old app.
