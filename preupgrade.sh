#!/bin/bash
# Preserve private state in the installer staging tree before its purge step.
set -euo pipefail
trap 'exit 2' ERR
PDIR=${3:?Plugin folder missing}
STAGE=${6:?Installer staging folder missing}
[[ "$PDIR" =~ ^porsche2lox[0-9]*$ ]] || exit 2
PCONFIG="${LBPCONFIG:?}/$PDIR"
PDATA="${LBPDATA:?}/$PDIR"
umask 077
python3 - "$PCONFIG" "$PDATA" "$STAGE" <<'PY'
import os
from pathlib import Path
import shutil
import sys

config, data, stage = map(Path, sys.argv[1:])
# The Python environment is recreated from pinned dependencies. Sockets/locks
# are process resources, not persistent plugin data. No other plugin is read.
for source, destination, skip in ((config, stage/'config', set()),
                                   (data, stage/'data', {'venv','control.sock','service.lock'})):
    destination.mkdir(parents=True, exist_ok=True, mode=0o700)
    destination.chmod(0o700)
    if not source.exists():
        continue
    for path in source.iterdir():
        if path.name in skip or path.is_symlink():
            continue
        if path.is_file():
            target = destination/path.name
            shutil.copyfile(path, target)
            target.chmod(0o600)
        elif path.is_dir():
            # Current state is flat. Refuse silent loss of future state layouts.
            raise SystemExit('Unknown PLX state directory; upgrade stopped before purge.')
print('PLX configuration and private state preserved for upgrade.')
PY
