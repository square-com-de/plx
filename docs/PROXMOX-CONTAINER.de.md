# PLX-Container in einer Proxmox-Linux-VM

[English](PROXMOX-CONTAINER.md) · [Bevorzugte Installation](../INSTALL.de.md) · [Abnahme-Gate](https://github.com/square-com-de/plx/issues/1)

**Docker/Compose ist der bevorzugte Installationsweg.** Proxmox stellt eine normale Linux-VM bereit; Docker läuft darin. Dies ist keine Anleitung für privilegiertes LXC oder Docker auf dem Proxmox-Host. LoxBerry bleibt eine Alternative. Podman, Rootless und echte ARM64-Laufzeit sind durch diesen Test nicht abgenommen.

## Genaue Umgebung und aktuelle Abnahmegrenze

Die separate Test-VM wurde frisch aus dem offiziellen Ubuntu-26.04-LTS-AMD64-Cloud-Image erstellt, nicht aus einer App-VM geklont. Ubuntu 26.04.1 / Kernel 7.0.0-38-generic, Docker Engine **29.9.2**, Compose **5.6.1**, 2 vCPU / 3 GiB RAM. PLX: `/srv/plx-test`, Projekt `accept-plx`, localhost-HTTPS **19443**. Hue2Lox hatte eigenes Verzeichnis/Projekt/Volume/Secret und HTTPS18443. Der frühere Test als wegwerfbares Projekt auf dem gemeinsam verwendeten Host119 bleibt ein eigener Nachweis und wird nicht zur Clean-Host-Abnahme umbenannt.

Image: `ghcr.io/square-com-de/plx@sha256:5b7a6a7244c9c0e0eb59b79aa021fddb73e2326846d00aa8a64408dca9f0cf5f`, öffentliche **0.1.0 Preview**, kein `latest`. Echtes Release-Archiv und alle Prüfsummen neu geladen; keine bestehende Porsche-Sitzung oder Produktivzugangsdaten übernommen.

**Endstand für den Containerumfang: BESTANDEN.** Der erste veröffentlichte localhost19443-Versuch endete mit TLS-EOF. Ein eigener Mock belegte: Die spezielle RFC1918-OUTPUT-Sperre der VM blockierte auch Host-Zugriffe zur eigenen Docker-Bridge (zwei zusätzliche Reject-Zähler), obwohl DNS/TCP/MQTT zwischen Containern funktionierten. Infra ergänzte eng begrenzte lokale Container-OUTPUT-/DNAT-Ausnahmen; Produktions-LAN- und IPv6-Sperren blieben bestehen. PLX erhielt danach bewusst die LAN-Bindung mit passendem IP-SAN-Zertifikat. Direkter externer Mac-HTTPS-Login und echter Chrome156-Browser mit separater Zertifikats-Vertrauensdatenbank bestanden, ohne Abschalten von TLS-Prüfungen. Neustart, Neuerstellung und Wiederherstellung einer passenden kalten Sicherung wurden über diese echte veröffentlichte LAN-URL wiederholt; Browseranmeldung danach erneut erfolgreich. [Maschinenlesbare Chronologie/Nachweise](evidence/2026-10-24-proxmox-clean.json). Frühere interne `docker exec`-Tests bleiben getrennt erkennbar und ersetzen nicht den abschließenden Browser-/Host-Port-Lauf.

Dies ist Container-/Lebenszyklusabnahme auf frischer VM, keine echte Porsche-Anmeldung/-Messung, Loxone-Engine-Abnahme, Podman-/ARM64-Freigabe, zukünftiger Schema-Downgrade oder produktiver Go-live. Die Instanz blieb zur koordinierten Abnahme laufen; kein globales Cleanup oder Eingriff in Produktivdienste.

## Docker-Installation durch den Provisionierer

Die frische VM erhielt Docker aus dem offiziellen apt-Repository mit den damaligen Kandidatenversionen; unten dieselben installierten Paket-Pins für Ubuntu26.04 AMD64. Als Administrator ggf. zuerst `sudo -i` verwenden. Nicht stillschweigend Docker-Gruppenzugehörigkeit voraussetzen oder sie routinemäßig zur Fehlerbehebung vergeben. Für andere OS-Versionen und vorhandene kollidierende Installationen gilt die [offizielle Docker-Ubuntu-Anleitung](https://docs.docker.com/engine/install/ubuntu/). Keine VM-Firewall-/Provisionierungsregeln in einen App-Installer übernehmen.

```sh
# Fresh Ubuntu 26.04 AMD64 VM only; run as root.
apt-get update
apt-get install -y ca-certificates curl
install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
chmod a+r /etc/apt/keyrings/docker.asc
. /etc/os-release
printf 'Types: deb\nURIs: https://download.docker.com/linux/ubuntu\nSuites: %s\nComponents: stable\nArchitectures: amd64\nSigned-By: /etc/apt/keyrings/docker.asc\n' "$VERSION_CODENAME" > /etc/apt/sources.list.d/docker.sources
apt-get update
apt-get install -y \
  docker-ce=5:29.9.2-1~ubuntu.26.04~resolute \
  docker-ce-cli=5:29.9.2-1~ubuntu.26.04~resolute \
  containerd.io=2.4.2-3~ubuntu.26.04~resolute \
  docker-buildx-plugin=0.38.1-1~ubuntu.26.04~resolute \
  docker-compose-plugin=5.6.1-1~ubuntu.26.04~resolute
systemctl enable --now docker
docker version
docker compose version
```

## Tatsächlicher PLX-Startweg

Diese Operationen wurden als root im reservierten PLX-Testverzeichnis ausgeführt und aus dem Abnahmeharness abgeleitet. Öffentliche Beispiele verwenden neutrale Pfade und die Dokumentationsadresse 192.0.2.10 statt interner Koordinaten. Das Harness nutzte zusätzlich eine leere Docker-Credential-Konfiguration als Nachweis des anonymen Pulls. Bei bestehendem PLX anderes leeres Verzeichnis/Projekt/Port wählen, echtes Secret nicht überschreiben. Compose im Release-Paket pinnt den Digest; die Build-Compose-Datei im Repository ist ein anderer Weg.

```sh
# One clean PLX project. Stop on any error; do not reuse an existing secret.
set -eu
install -d -m 0700 /srv/plx-test
cd /srv/plx-test
release=https://github.com/square-com-de/plx/releases/download/v0.1.0
curl -fL "$release/PLX-Docker-0.1.0.tar.gz" -o PLX-Docker-0.1.0.tar.gz
curl -fL "$release/SHA256SUMS" -o SHA256SUMS
sha256sum --ignore-missing -c SHA256SUMS
tar -xzf PLX-Docker-0.1.0.tar.gz
cd PLX-Docker-0.1.0
sha256sum -c SHA256SUMS
umask 077
mkdir -p secrets
test ! -e secrets/plx_password.txt
openssl rand -base64 32 > secrets/plx_password.txt
chgrp 10001 secrets/plx_password.txt
chmod 640 secrets/plx_password.txt
printf 'PLX_BIND_ADDRESS=127.0.0.1\nPLX_PORT=19443\n' > .env
docker compose -p accept-plx config --quiet
docker compose -p accept-plx pull
docker compose -p accept-plx up -d --wait --wait-timeout 90
docker compose -p accept-plx ps
docker compose -p accept-plx logs --no-color --tail=50 plx
docker compose -p accept-plx exec -T plx python /app/healthcheck.py
```

Standardbenutzer `admin`, Passwort aus der privat erzeugten Datei, niemals aus einem Beispielpasswort. PLX- und Porsche-Anmeldung sind getrennt. Das erste Zertifikat gilt für localhost/127.0.0.1 und muss bewusst vertraut werden; Healthchecks verifizieren es. Für einen entfernten Browser SSH-Tunnel oder bewusst gesetzte LAN-Bindung mit passend vertrauenswürdigem Zertifikat/SAN nutzen. `localhost` auf dem Desktop ist nicht die VM. Keine TLS-Prüfung abschalten oder zur Fehlersuche alle Interfaces freigeben. PLX besitzt kein Hue2Lox-`HUE_PUBLIC_URL`; nur dokumentierte PLX-Variablen verwenden.

## Bewusste LAN-Bindung mit passender TLS-Identität

Die Loopback-Bindung oben ist absichtlich nur lokal und keine erfolgreiche LAN-Konfiguration. Nach Infras gezielter Lab-Firewallkorrektur stellten diese Schritte nur das Testzertifikat für die zugewiesene VM-IP neu aus, sicherten das vorherige Zertifikat und verwendeten denselben privaten Schlüssel. Image, Daten, Passwort und Volume blieben erhalten. Im Produktivbetrieb ein eigenes geeignetes vertrauenswürdiges Zertifikat verwenden; bestehende Zertifikate nicht ohne passenden Sicherungs-/Recoveryplan überschreiben. DHCP-Adressen vor Wiederverwendung prüfen.

```sh
# Documentation address only: replace with your actual assigned LAN IP.
test_ip=192.0.2.10
cid=$(docker compose -p accept-plx ps -q plx)
docker exec "$cid" test ! -e /data/tls/cert.before-lan.pem
docker exec "$cid" cp /data/tls/cert.pem /data/tls/cert.before-lan.pem
docker exec "$cid" openssl req -x509 -new -key /data/tls/key.pem \
  -out /data/tls/cert.lan.new.pem -days 365 -subj '/CN=PLX acceptance localhost' \
  -addext "subjectAltName=DNS:localhost,IP:127.0.0.1,IP:$test_ip"
docker exec "$cid" chmod 600 /data/tls/cert.lan.new.pem
docker exec "$cid" mv /data/tls/cert.lan.new.pem /data/tls/cert.pem
printf 'PLX_BIND_ADDRESS=%s\nPLX_PORT=19443\n' "$test_ip" > .env
docker compose -p accept-plx up -d --force-recreate --wait --wait-timeout 90
```

Direkt geprüft wurde die LAN-IP der Test-VM auf Port19443. `192.0.2.10` ist hier ausschließlich eine Dokumentationsadresse; auf dem eigenen Server dessen echte IP einsetzen. Der externe Mac-Client validierte Zertifikat und IP-SAN und meldete sich erfolgreich an. Chrome for Testing156.0.8078.47 lief auf die separate Test-VM mit derselben LAN-IP-URL; seine temporäre NSS-Datenbank vertraute dem selbstsignierten Serverzertifikat ausdrücklich gemäß [Chromium-Linux-Zertifikatsverwaltung](https://chromium.googlesource.com/chromium/src/+/HEAD/docs/linux/cert_management.md). Kein `ignoreHTTPSErrors` oder Certificate-Error-Ignore-Flag. Browserprüfung: Secure/HttpOnly/SameSite-Cookies, DE/EN, Speichern/Neuladen, erhaltene Entwürfe und 390px-Mobilansicht. Browserwerkzeuge sind nur Testmittel, keine PLX-Laufzeitabhängigkeit.

## Neustart ist kein Image-Update

```sh
# Same Compose directory, project, secret and volume.
docker compose -p accept-plx restart plx
# After selecting a reviewed new image pin in compose.yaml:
docker compose -p accept-plx pull
docker compose -p accept-plx up -d --force-recreate --wait --wait-timeout 90
docker compose -p accept-plx ps
```

Geprüft wurden Neustart desselben Containers und Neuerstellung mit Erhalt von Einstellungen, Auswahl, TLS und Passwort. Ein unveränderliches Release-Image wurde verwendet; kein Nachweis eines zukünftigen Schema-Up-/Downgrades. Nach Prozessneustart ist neue PLX-Webanmeldung normal. Kein Porsche-Token importiert oder authentifiziert; eine allgemeine private Datei prüfte nur die Volume-Persistenz.

## Kalte Sicherung und passender Rückweg

Im Test wurden bei gestopptem Schreiber das komplette Datenvolume außer flüchtigen Sockets/Locks sowie Compose/Umgebung, Webpasswort und Image-Referenz gesichert; das Harness verglich zurückgespielte Hashes und Einstellungen. Sicherungen schützen: echte Installationen können Tokens/Standorte/TLS-Schlüssel enthalten. Kein `down -v` oder globales Prune zum Aktualisieren.

```sh
# Same Compose directory; private cold backup, never upload to GitHub.
set -eu
project=accept-plx
cid=$(docker compose -p "$project" ps -aq plx)
test -n "$cid"
volume=$(docker inspect --format '{{range .Mounts}}{{if eq .Destination "/data"}}{{.Name}}{{end}}{{end}}' "$cid")
case "$volume" in "${project}_plx_data"|"${project}-restored-"*|"${project}-lan-restored-"*) ;; *) echo 'Unexpected data volume'; exit 1;; esac
image=$(docker inspect --format '{{.Config.Image}}' "$cid")
stamp=$(date -u +%Y%m%dT%H%M%SZ)
backup="$PWD/backups/$stamp"
umask 077
mkdir -p "$backup"
docker compose -p "$project" stop plx
docker run --rm --network none --read-only --cap-drop ALL \
  -v "$volume:/data:ro" --entrypoint python "$image" -c \
  "import sys,tarfile;from pathlib import Path;t=tarfile.open(fileobj=sys.stdout.buffer,mode='w|gz');[t.add(p,arcname=str(p.relative_to('/data')),recursive=True,filter=lambda i:None if i.name.endswith(('control.sock','service.lock')) else i) for p in Path('/data').iterdir()];t.close()" \
  > "$backup/data.tar.gz"
cp compose.yaml .env "$backup/"
if [ -f compose.restore.yaml ]; then cp compose.restore.yaml "$backup/"; fi
cp secrets/plx_password.txt "$backup/plx_password.txt"
printf '%s\n' "$image" > "$backup/image-pin.txt"
chmod 600 "$backup/"*
docker compose -p "$project" start plx
```

Nur vertrauenswürdige passende Sicherung in ein neues eigenes Volume zurückspielen. Bei echtem Versionsrückgang auch passenden Compose-Pin, Umgebung und Secret herstellen; alter Code muss keine neuen Daten lesen können. Folgendes prüfte Datenrollback mit demselben Image, keine allgemeine Versionsmigration:

```sh
# Keep $backup/$image from the verified matching backup above.
# Stop only this PLX instance. A fresh target preserves the failed data volume.
docker compose -p accept-plx stop plx
restore="accept-plx-restored-$(date -u +%Y%m%dT%H%M%SZ)"
docker volume create "$restore"
docker run --rm -i --network none --read-only --cap-drop ALL \
  -v "$restore:/data" --entrypoint python "$image" -c \
  "import sys,tarfile;t=tarfile.open(fileobj=sys.stdin.buffer,mode='r|gz');t.extractall('/data',filter='data');t.close()" \
  < "$backup/data.tar.gz"
printf 'volumes:\n  plx_data:\n    external: true\n    name: %s\n' "$restore" > compose.restore.yaml
python3 - <<'PYTHON'
from pathlib import Path
p=Path('.env')
p.write_text('\n'.join(l for l in p.read_text().splitlines() if not l.startswith('COMPOSE_FILE='))+'\nCOMPOSE_FILE=compose.yaml:compose.restore.yaml\n')
p.chmod(0o600)
PYTHON
docker compose -p accept-plx up -d --force-recreate --wait --wait-timeout 90
```

Nach Restore wählt `COMPOSE_FILE` in `.env` **beide** Dateien dauerhaft. Ein anschließendes normales `docker compose -p accept-plx up -d` wurde geprüft und behielt das zurückgespielte Volume; so führt der nächste Aufruf nicht versehentlich zum alten Originalvolume zurück. Rückgespielte Werte, Zertifikat und Passwort vor produktiven Automationen prüfen. Originalvolume separat erhalten, bis Recovery bestätigt ist. Compose kann warnen, dass das alte verwaltete Volume nicht zum externen Restore-Volume passt und unberührt bleibt; das wurde hier beobachtet und ist beabsichtigt. Tatsächlichen `/data`-Mount prüfen, statt das Original zum Unterdrücken der Warnung zu löschen. Ein leeres/anders benanntes Volume kann wie Datenverlust aussehen. Der Test verwendete nur eigene wegwerfbare Daten und entfernte nur eigene Testressourcen.

## Netzwerk- und Mock-Ergebnisse

Das echte öffentliche PLX-Image sandte zwei ausdrücklich simulierte Reifendrücke und zwei fehlende Werte als `null` an einen privaten Protokoll-Mock im eigenen Docker-Netz. DNS/TCP, MQTT CONNECT/PUBACK, QoS1/Retain und genaue Nachrichtenzahl bestanden; keine echte Broker-ACL/TLS- oder Fahrzeugwert-Abnahme. Optionaler Testmock auf localhost1885 wurde entfernt. Kein Produktiv-MQTT-Publish, Porsche-Abruf, Hue-Pairing oder Miniserver-Eingriff.

Ein HTTPS-Webhostname kann statt zum Broker auf einen Reverse Proxy zeigen; echten Broker-Endpunkt/Listener verwenden. Broker-TCP1883/8883 und Gateway-UDP11883 zum Miniserver unterscheiden sich. Docker-Bridge-Netze transportieren mDNS und die `.local`-Namensauflösung des Hosts nicht automatisch; DNS/TCP im Container prüfen. PLX nutzt konfigurierte Endpunkte, verspricht keine automatische lokale Erkennung. Lab-LAN-Sperren erhalten; Infra behob den Portfehler durch gezielte Owner-Ausnahmen ausschließlich für konkrete lokale Bridge, Container/Port und eingehendes übersetztes Ziel. Kein Host-/Macvlan-Netz oder Abschalten der Firewall, um rote Tests grün aussehen zu lassen.
