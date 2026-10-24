#!/bin/bash
set -euo pipefail
PDIR=${3:?Plugin folder missing}
[[ "$PDIR" =~ ^porsche2lox[0-9]*$ ]] || exit 2
PBIN="${LBPBIN:?}/$PDIR"
PDATA="${LBPDATA:?}/$PDIR"
PCONFIG="${LBPCONFIG:?}/$PDIR"
umask 077
mkdir -p "$PDATA" "$PCONFIG"
chmod 700 "$PDATA" "$PCONFIG"
if ! python3 -c 'import sys; sys.exit(0 if sys.version_info >= (3,11) else 1)'; then
    echo '<ERROR> PLX benötigt Python 3.11 oder neuer (LoxBerry 4 / Debian 12+).'
    exit 2
fi
python3 -m venv "$PDATA/venv"
"$PDATA/venv/bin/python" -m pip install --disable-pip-version-check --require-hashes -r "$PBIN/requirements.lock.txt"
echo '<OK> Eigene Python-Umgebung eingerichtet. Bestehende Porsche-App bleibt unverändert.'
