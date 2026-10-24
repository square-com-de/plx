> Historical 0.1.0 acceptance/operations reference. For 0.1.1 first start use INSTALL.md/INSTALL.de.md; manual secret/certificate setup below is not required by the new default.

# PLX container on a Proxmox Linux VM

[Deutsch](PROXMOX-CONTAINER.de.md) · [Preferred installation](../INSTALL.md) · [Acceptance gate](https://github.com/square-com-de/plx/issues/1)

**Docker/Compose is the preferred deployment path.** Proxmox hosts a normal Linux VM; Docker runs inside that VM. This is not a privileged-LXC or Proxmox-host Docker installation guide. LoxBerry remains an alternative. Podman, rootless and real ARM64 runtime are not qualified by this test.

## Exact environment and current acceptance boundary

The dedicated test VM was created fresh from the official Ubuntu 26.04 LTS AMD64 cloud image, not a clone of an application VM. Ubuntu 26.04.1 / kernel 7.0.0-38-generic, Docker Engine **29.9.2**, Compose **5.6.1**, 2 vCPU / 3 GiB RAM. PLX used `/srv/plx-test`, project `accept-plx`, localhost HTTPS **19443**; Hue2Lox used a different directory/project/volume/secret and HTTPS18443. This differs from the earlier disposable-project acceptance on shared the shared test host; that earlier result is not relabelled as clean-host evidence.

Image: `ghcr.io/square-com-de/plx@sha256:5b7a6a7244c9c0e0eb59b79aa021fddb73e2326846d00aa8a64408dca9f0cf5f`, public **0.1.0 Preview**, not `latest`. Actual public archive and all checksums were fetched anew; no existing Porsche session or production credentials were copied.

**Final container-scope result: PASS.** The initial published localhost19443 attempt failed with TLS EOF. An owned mock proved that the test VM's custom OUTPUT RFC1918 deny also blocked host-to-own-Docker-bridge traffic (two reject counter increments), although container-to-container DNS/TCP/MQTT worked. Infra added narrowly scoped local-container OUTPUT/DNAT exceptions and retained production-LAN/IPv6 restrictions. PLX was then deliberately bound to the VM's LAN IP with a matching certificate SAN. Verified direct external Mac HTTPS/login and a real Chrome156 browser using an isolated certificate-trust database passed, with no TLS-error bypass. Restart, recreation and matching-state cold restore were repeated through that actual published LAN URL; browser sign-in passed again afterward. [Machine-readable chronology and evidence](evidence/2026-10-24-proxmox-clean.json). Earlier internal `docker exec` tests remain separately labelled, not substituted for the final browser/host-port run.

This is clean-VM container/lifecycle acceptance, not a live Porsche login/measurement, physical Loxone engine test, Podman/ARM64 qualification, future-version schema downgrade or production go-live. The instance was left running for coordinated acceptance; no global cleanup or production service change occurred.

## Docker installation used by the provisioner

The fresh VM provisioner installed Docker from its official apt repository, selecting then-current candidate versions; below are the same installed package pins for reproducibility on Ubuntu26.04 AMD64. An administrator can first enter a root shell (`sudo -i`); do not silently depend on Docker-group membership or grant it as a routine workaround. Use the [official Docker Ubuntu guide](https://docs.docker.com/engine/install/ubuntu/) for other OS versions and conflicting existing installations. Do not copy VM firewall/provisioning rules into an application installer.

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

## Actual PLX start path

These operations were executed under root in the reserved PLX test directory and extracted from the acceptance harness. Public examples use generic paths and documentation address 192.0.2.10 rather than internal coordinates. The harness additionally used an empty Docker credential config to prove anonymous pull. Choose a different empty directory/project/port if running this alongside an existing PLX; do not overwrite a real secret. The release bundle's Compose file pins the digest; the repository's build-enabled `compose.yaml` is a different path.

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

Default username is `admin`; password is the generated private file, never a documented example password. PLX login is separate from Porsche login. The first generated certificate covers localhost/127.0.0.1 and must be explicitly trusted; health checks verify it. For a remote browser, use an SSH tunnel or a deliberately chosen LAN binding with a matching trusted certificate/SAN; `localhost` on your desktop does not address the VM. Do not disable TLS checks or bind every interface as a troubleshooting shortcut. PLX has no Hue2Lox `HUE_PUBLIC_URL` setting; use only PLX's documented environment variables.

## Deliberate LAN binding and matching TLS identity

Loopback binding above is intentionally local-only, not a successful LAN configuration. After Infra's narrow lab firewall fix, these operations reissued only the test certificate for the assigned VM IP, backed up the previous certificate and reused the same private key. Image, data, password and volume stayed unchanged. A production deployment should use its own suitable trusted certificate; do not overwrite an established certificate without a matching backup/recovery plan. DHCP addresses must be rechecked before reuse.

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

The directly tested URL used the test VM's LAN IP on port19443. `192.0.2.10` is a documentation address only; replace it with your own server's actual IP. The external Mac client validated the certificate and IP SAN and successfully signed in. Chrome for Testing156.0.8078.47 ran on the dedicated test VM at that same LAN-IP URL; its temporary NSS database explicitly trusted this self-signed server certificate, following [Chromium's Linux certificate management](https://chromium.googlesource.com/chromium/src/+/HEAD/docs/linux/cert_management.md). No `ignoreHTTPSErrors` or certificate-error-ignore flags were enabled. Browser checks included Secure/HttpOnly/SameSite cookies, DE/EN, save/reload, retained drafts and mobile390px layout. Browser tooling is test-only, not a PLX runtime dependency.

## Restart versus image update

```sh
# Same Compose directory, project, secret and volume.
docker compose -p accept-plx restart plx
# After selecting a reviewed new image pin in compose.yaml:
docker compose -p accept-plx pull
docker compose -p accept-plx up -d --force-recreate --wait --wait-timeout 90
docker compose -p accept-plx ps
```

The run verified restart of the same container and force-recreation retaining settings, selection, TLS and password. It used one immutable released image; this is not evidence of a future-version schema upgrade/downgrade. A new PLX web login after process restart is expected. No Porsche token was imported or authenticated; a generic private file tested volume persistence only.

## Cold backup and matching-state restore

The stopped-writer test archived the complete data volume except transient sockets/locks, plus Compose/environment, web password and immutable image reference; the actual harness checked restored hashes and settings. Protect backups: they may contain tokens/locations/TLS keys in a real installation. Do not run `down -v` or a global prune for an update.

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

Restore only a trusted matching backup into a fresh owned volume. For an actual image downgrade, also restore its matching Compose pin, environment and secret; do not assume older code reads newer data. The following exercised the same-image data rollback; no general cross-version migration guarantee is made:

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

After restore, `COMPOSE_FILE` in `.env` selects **both** files persistently. A subsequent bare `docker compose -p accept-plx up -d` was tested and kept the restored volume; this prevents accidentally returning to the stale original volume. Confirm restored values and certificate/password before switching any production automation. Keep the original volume separately until recovery is confirmed. Compose may warn that the old managed volume does not match the restored external volume and is left untouched; that warning was observed here and is intentional. Check the actual `/data` mount instead of deleting the original to silence it. An empty/differently named volume can look like lost settings. The test used only disposable own data and removed only its own test resources.

## Network and mock results

The actual public PLX image published two explicit simulated pressures and two missing-pressure `null` values to a private protocol mock on its own Docker network. DNS/TCP, MQTT CONNECT/PUBACK, QoS1/retain and exact message counts passed; no real broker ACL/TLS or vehicle reading was tested. The optional test mock used localhost1885 and was removed afterward. No production MQTT publish, Porsche fetch, Hue pairing or Miniserver change occurred.

A web HTTPS hostname can point to a reverse proxy instead of the MQTT broker; use the real broker endpoint/listener. Broker TCP1883/8883 and Gateway-to-Miniserver UDP11883 are distinct. Docker bridge networking does not automatically transport mDNS or make a host's `.local` names resolvable; verify DNS/TCP inside the container. PLX uses configured endpoints, not a promise of automatic local discovery. Preserve lab LAN-deny rules; Infra resolved the proven host-port issue using owner-reviewed exceptions for the concrete local bridge, container/port and incoming translated destination only. Never use host/macvlan networking or disable the firewall to turn a red test green.
