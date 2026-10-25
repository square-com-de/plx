# Install PLX — Docker first

[Deutsch](INSTALL.de.md) · [README](README.md)

Requires a Linux Docker host with `docker compose` and `curl`, with Docker access (for example an administrator shell). Proxmox users run Docker in a normal Linux VM, not on the hypervisor. Portainer uses the same Compose file. PLX 0.1.3 remains a **Preview**.

## Start

Choose the server IP or DNS name you will open in your browser. Replace **192.0.2.10** below with that address; no `https://`, path or port in `PLX_HOST`. A DNS name must already resolve to the server IPv4 address on your client; IPv6 is not qualified by this default path. There is no initial Simple/Pro choice: Simple is the usable default.

```sh
set -eu
mkdir plx && cd plx
curl -fLO https://github.com/square-com-de/plx/releases/download/v0.1.3/compose.yaml
printf 'PLX_HOST=192.0.2.10\n' > .env
docker compose up -d --wait --wait-timeout 90
docker compose exec -T plx cat /data/config/web-password.txt
```

Open **`https://<your-server>:8443`**, username **`admin`**, password from the last command. That command deliberately displays your own generated password in your server console; keep it private. Password, TLS key/certificate and settings are generated once in the persistent named volume. No secret-file/chgrp/UID setup is required. Do not reuse the creation commands over an existing installation.

**Before entering credentials:** the first certificate is self-signed and matches `PLX_HOST`; a private-IP certificate is not automatically trusted by browsers. Establish explicit trust for your own server certificate, or use your own suitable trusted certificate. Its fingerprint is available with `docker compose exec -T plx openssl x509 -in /data/tls/cert.pem -noout -fingerprint -sha256`. Do not disable TLS verification. If the existing certificate does not match a changed host, startup stops with a clear message and preserves the existing files.

The default host port is **8443 and LAN-accessible**. Keep it on a trusted LAN; do not forward it from the Internet. If occupied, add `PLX_PORT=19443` to `.env` and open that port. A deliberate local-only alternative is `PLX_BIND_ADDRESS=127.0.0.1` with `PLX_HOST=localhost`; this is not the LAN default. No separate public-URL option is required by PLX. The public image needs no GitHub token or registry login. Checksums and immutable image provenance are attached to the versioned release.

## Portainer

Create a separate stack using the release `compose.yaml`. Set the required environment variable **PLX_HOST** to the server IP/DNS name. Deploy; in the PLX container console run `cat /data/config/web-password.txt`. The named volume is automatic; no host secret path or manual file ownership is needed. Keep the same stack name for updates.

## Connect your data

1. Sign in to the PLX web interface first. Then sign in under **Porsche account**, complete CAPTCHA if requested, load/select your vehicle and save. Your Porsche account is an unavoidable separate credential; PLX cannot create or import it automatically.
2. Status polling and MQTT start **disabled**. Enable them only after setup. PLX reads status and does not wake or control the vehicle.
3. For MQTT, enter the actual broker host/port/credentials, select only desired values and save. Use one subscription, `porsche2lox/#` (or your prefix). Two selected pressures in Simple mode send two values. Advanced output is optional later, without reinstallation.

A web-proxy hostname is not automatically the MQTT broker. Broker TCP1883/8883 differs from the optional Gateway-to-Miniserver UDP port. Container bridge networks do not automatically provide mDNS or host `.local` resolution. These are network prerequisites, not hidden PLX modes; see the [manual](docs/MANUAL.md#mqtt-and-loxone).

## Update, backup and recovery

Keep the same Compose directory, project/stack name and data volume. Back up the complete stopped PLX data volume and the active Compose files/`.env` before updates; it contains the generated web password, TLS key and any Porsche tokens. Never upload backups. Then choose the reviewed release/digest and use:

```sh
docker compose pull
docker compose up -d --wait --wait-timeout 90
docker compose ps
```

`restart` does not update an image. Never use `down -v` to retain data. A new PLX web login after restart is normal; saved data/password persist. For recovery, stop PLX and restore a matching private backup into a separate owned volume; preserve the active Compose file selection. [Tested backup/restore mechanics](docs/PROXMOX-CONTAINER.md#cold-backup-and-matching-state-restore) remain an operations reference, not first-start steps. Do not assume older code reads future data formats. Existing explicitly configured `PLX_PASSWORD_FILE` secrets remain supported; the generated-password command above applies to the new default path.

## Alternatives and limits

**LoxBerry alternative:** import the dedicated `PLX-LoxBerry-0.1.3.zip` through LoxBerry4's plugin manager, over direct HTTPS, using its existing web login. Do not import the generic source ZIP. Keep technical ID `porsche2lox` during updates. For LoxBerry TLS termination with an HTTP backend, configure the explicit trusted proxy peers below; [gate #1](https://github.com/square-com-de/plx/issues/1) remains explicit.

Docker Linux/Proxmox is preferred; prior clean-VM evidence is documented separately from this new first-start flow. Podman/rootless, native outside LoxBerry and real ARM64 runtime are not qualified by manifest availability alone. The laboratory firewall incident in the historical test report is **not** an end-user installation step. No certificate trust, device account, broker credential or multicast reachability is promised automatically. [Manual](docs/MANUAL.md) · [Release notes](docs/RELEASE-0.1.3.md).

[Historical published0.1.1 quickstart acceptance](docs/QUICKSTART-0.1.1.md): fresh volume, verified LAN/browser login, restart/recreation and matching cold restore passed. Test limits remain explicit.

### LoxBerry behind an HTTPS proxy

An HTTPS proxy with an HTTP backend needs an explicit list of trusted immediate proxy addresses. [Configuration and security rules](docs/REVERSE-PROXY.md). The fix is included from0.1.2; public0.1.1 remains unchanged; direct HTTPS remains supported.

[PLX 0.1.2 Preview: tested public Docker and LoxBerry artifacts, results and limits](docs/QUICKSTART-0.1.2.md).
