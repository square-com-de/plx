#!/bin/bash
set -euo pipefail
PDIR=${3:?Plugin folder missing}
[[ "$PDIR" =~ ^porsche2lox[0-9]*$ ]] || exit 2
PBIN="${LBPBIN:?}/$PDIR"
PDATA="${LBPDATA:?}/$PDIR"
PCONFIG="${LBPCONFIG:?}/$PDIR"
UNIT="porsche2lox-${PDIR}.service"
# Existing plugin paths and the actual installation folder are supplied by LoxBerry.
# Reject newline/quote expansion in systemd configuration.
for path in "$PBIN" "$PDATA" "$PCONFIG"; do
    [[ "$path" =~ ^/[a-zA-Z0-9_./-]+$ ]] || exit 2
done
cat > "/etc/systemd/system/$UNIT" <<EOF
[Unit]
Description=PLX status integration ($PDIR)
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=loxberry
Group=loxberry
UMask=0077
WorkingDirectory=$PBIN
ExecStart=$PDATA/venv/bin/python -m porsche2lox.service --config-dir $PCONFIG --data-dir $PDATA
Restart=on-failure
RestartSec=10
TimeoutStopSec=30
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ProtectHome=true
ReadWritePaths=$PCONFIG $PDATA
RestrictAddressFamilies=AF_UNIX AF_INET AF_INET6
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF
chmod 644 "/etc/systemd/system/$UNIT"
chown -R loxberry:loxberry "$PDATA" "$PCONFIG"
systemctl daemon-reload
systemctl enable "$UNIT"
systemctl restart "$UNIT"
echo '<OK> PLX gestartet. Statusabruf und MQTT sind bei Erstinstallation deaktiviert.'
