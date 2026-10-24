# Install PLX

[Deutsch](INSTALL.de.md) · [Project page](README.md) · [Lessons and release gate](docs/INSTALLATION-LESSONS.md)

**0.1.0 Preview, not Stable.** Use the [versioned release](https://github.com/square-com-de/plx/releases/tag/v0.1.0). Image and repository are public; no GitHub account, registry token or `docker login` is needed. Existing release archives keep their original documentation; this page corrects it without replacing signed-off artifacts/checksums. [Gate #1](https://github.com/square-com-de/plx/issues/1) tracks independent end-user acceptance before any future Stable/`latest` promotion.

**Preferred path: Docker/Compose in a Linux VM**, including Proxmox. LoxBerry is an alternative. [Executed fresh-VM Docker/app/recovery commands and test limits](docs/PROXMOX-CONTAINER.md). The VM121 published-host-port check is still blocked by its custom host OUTPUT rules; internal application checks do not replace that end-user test.

## Runtime status

| Path | Preview qualification, 2026-10-24 |
| --- | --- |
| Linux Docker / Compose, AMD64 | Dedicated Ubuntu 26.04.1 x86_64 test host; currently Docker Engine 29.8.2, Compose plugin 5.6.1. Earlier acceptance reports did not record runtime versions; these are today's inventory, not retroactive version claims. |
| LoxBerry 4 plugin | Dedicated LoxBerry 4.0.0.15, DietPi/Debian 13.7, Python 3.13.5, PHP 7.4.33; direct HTTPS, official clean install/update, Porsche fetch and isolated MQTT tested. |
| Linux ARM64 image | Built/published manifest, **not** a recorded real ARM64 deployment acceptance. |
| Portainer | Separate test stack used; host paths and same Compose project/volume must be preserved. Portainer version was not captured in the historical acceptance. |
| Podman / rootless / native outside LoxBerry / Docker Desktop | **Not qualified for PLX.** No published tested install procedure. Do not substitute `podman` for `docker` and assume equivalent secrets, volumes or health checks. Another project's failure is not a PLX diagnosis. |

## Linux Docker / Compose: first install

Requires a Linux Docker host, `docker compose`, `curl`, GNU `sha256sum`, `tar`, `openssl` and `sudo` for the file's group change. A compatible Porsche Connect account and outbound HTTPS/DNS are needed for sign-in/data. An MQTT broker is required only for MQTT output; PLX does not install one.

The application commands require Docker access. In the clean VM they ran as root; a normal administrator should prefix Docker commands with `sudo` or enter `sudo -i`. Do not grant Docker-group membership implicitly.

Run the following **once, line by line, in a new directory; stop at any error**. Do not regenerate a secret for an existing installation. The release bundle's Compose definition pins the public image digest. The repository's `compose.yaml` instead builds `plx:local`; `compose.registry.yaml` uses the version tag. Do not mix these three paths.

```sh
set -eu
mkdir plx
cd plx
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
sudo chgrp 10001 secrets/plx_password.txt
chmod 640 secrets/plx_password.txt
docker compose -p plx config --quiet
docker compose -p plx pull
docker compose -p plx up -d --wait --wait-timeout 90
docker compose -p plx ps
```

The secret stays owned by its creator, is readable by container GID **10001**, and is not world-readable. A copied `chmod 600` alone can prevent the container's UID/GID 10001 from starting. Do not solve this with `chmod 777`.

Open `https://localhost:8443` **on the Docker host**. Username `admin`; password is the generated secret, not your Porsche password. Default certificate covers localhost/127.0.0.1; establish local trust or provide a trusted matching certificate. For a LAN host, persist the chosen settings in `.env` **in the same Compose directory**, then run `docker compose -p plx up -d`:

```dotenv
PLX_BIND_ADDRESS=192.0.2.10
PLX_PORT=8443
```

Replace the documentation address with the server's actual LAN IP. Open `https://<server-IP>:8443`; provide a certificate whose SAN matches that address. Preserve localhost SAN for the built-in health check. See [Docker/TLS details](docs/DOCKER.md). A browser on another computer cannot reach the server through its own `localhost`.

For Portainer, deploy a separate PLX stack with the release Compose definition. The file secret must exist on that environment's Docker host, not only on your desktop. Reuse the **original stack/project name and data volume** during updates. Do not run the same installation simultaneously through a differently named CLI project.

## LoxBerry plugin

Prerequisites: LoxBerry 4, Debian 12+ / Python 3.11+ as required by the installer, HTTPS and installation-time internet access. Only the exact environment above has an end-to-end plugin record; this does not qualify every Debian/LoxBerry version.

1. Download [PLX-LoxBerry-0.1.0.zip](https://github.com/square-com-de/plx/releases/download/v0.1.0/PLX-LoxBerry-0.1.0.zip) and compare its checksum with the release `SHA256SUMS`. Do not import GitHub's generic source ZIP or the Docker archive.
2. Install the ZIP unchanged through LoxBerry's plugin manager.
3. Open PLX in the authenticated LoxBerry area **over direct HTTPS**; use your LoxBerry web login, not a Docker PLX password.
4. Keep technical plugin ID/directory `porsche2lox` for updates; PLX is the display name.

**0.1.0 proxy limitation:** an HTTPS frontend that forwards HTTP to LoxBerry is rejected by the released login/save guard. Use direct LoxBerry HTTPS, or a verified HTTPS backend where your proxy supports it. Browser -> PLX and PLX -> Porsche are separate connections; Porsche requests still use HTTPS. Do not disable the guard or blindly trust `X-Forwarded-Proto`. A trusted-proxy code change is not included in the published 0.1.0 ZIP; tracked in [#1](https://github.com/square-com-de/plx/issues/1).

## First setup and addresses

1. Under **Porsche account**, sign in and complete CAPTCHA if requested. Load vehicles; select your car in Setup and **save**. Discovery alone is not selection.
2. Refresh status in Overview. Enable polling separately if wanted; 15 minutes is recommended.
3. Set MQTT to the **broker endpoint**, not automatically the web UI's hostname. HTTP/HTTPS proxy routes do not forward MQTT unless explicitly configured to do so. `127.0.0.1` inside Docker means PLX itself. Test name resolution and TCP from PLX's container before changing passwords; see the [manual](docs/MANUAL.md#mqtt-and-loxone).
4. Select only the desired values under Loxone and save; choose **simple output** for one topic per value. Then enable MQTT. Subscribe to `<prefix>/#`, default `porsche2lox/#`. Subscription does not select what PLX publishes.

| Endpoint | Purpose | Port |
| --- | --- | --- |
| PLX HTTPS UI | Browser login, dashboard | Container 8443; host port configurable |
| MQTT broker | PLX publishes, Gateway subscribes | Broker's actual listener; commonly TCP 1883 plain or 8883 TLS, not automatic discovery |
| MQTT Gateway -> Miniserver | Optional numeric XML/UDP bridge | Matching configured UDP port, PLX export default 11883; not the broker's port |

No commands/wake requests are sent to the vehicle. The optional XML/CSV export does not configure your Gateway or Miniserver. The **source-IP filter means the UDP sender (MQTT Gateway)**, not automatically PLX, the broker, LoxBerry or the Miniserver. Leave it empty unless that sender is known.

## Updates, backup and rollback

**Docker:** keep the same directory, Compose project/stack name, named volume, `.env` and password secret. For the command examples the project is `plx`; existing installations must retain their existing name. A different project name can create an empty volume that looks like lost settings.

Before updating, stop only PLX and take a private cold backup of its entire `/data` volume plus Compose file, `.env`, secret and previous image digest. `/data` includes settings, Porsche tokens, cached data/images and TLS keys. Check the real named volume with `docker inspect` on PLX's container; do not guess it from a directory name. Keep the previous image locally. Backups are credentials: restrict access and do not upload them to GitHub.

Replace only the Compose image pin with the reviewed new version/digest (or the new reviewed release Compose definition); retain the other settings. Then run from the same directory:

```sh
docker compose -p plx pull
docker compose -p plx up -d --wait --wait-timeout 90
docker compose -p plx ps
```

`restart` does not install a new image. Do not use `down -v`, delete the volume, regenerate the secret, or switch project names. After restart sign in to PLX again; the Porsche session is persisted separately.

For rollback, stop only PLX; preserve the failed state separately for investigation. Restore the prior Compose pin/settings/secret and a **matching pre-update data backup** into a separate PLX-only volume, preserving UID/GID 10001 and private modes. Point that same project at the restored volume, recreate PLX, and verify HTTPS, saved settings, Porsche session and selected MQTT values. Never assume an old image reads a newer schema. Do not overwrite a live mounted volume. The exact backup/restore procedure must be independently exercised for a Stable candidate in [#1](https://github.com/square-com-de/plx/issues/1); the existing restart/update evidence is not a restore test.

**LoxBerry:** back up both `/opt/loxberry/config/plugins/porsche2lox/` and `/opt/loxberry/data/plugins/porsche2lox/` while only this plugin's service is stopped (`porsche2lox-porsche2lox.service` for the default directory). Check the real directory/service name for numbered installations. Private config and runtime files must retain ownership/modes; the venv is rebuildable, sockets/locks are not portable backups. Keep the prior installable ZIP. Install the newer ZIP **over** the plugin; do not uninstall first. Released preroot/preupgrade hooks preserve private state before the official installer purges directories and rebuilds the venv. If rolling back, stop only PLX, use the prior ZIP and its matching private backup, then verify restored state; independent recovery acceptance remains in [#1](https://github.com/square-com-de/plx/issues/1).

A selection/format change can remove known old retained topics once. Simple mode has no periodic deletion/heartbeat burst. Never clear a shared MQTT tree to troubleshoot another application.
