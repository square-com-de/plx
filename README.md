<p align="center"><img src="icons/plx-logo-original.png" width="112" alt="PLX app icon"></p>
<h1 align="center">PLX</h1>
<p align="center"><strong>Porsche Connect status, with only the MQTT values your smart home needs.</strong></p>
<p align="center"><a href="#quick-start">Quick start</a> · <a href="INSTALL.md">Installation</a> · <a href="docs/MANUAL.md">Manual</a> · <a href="README.de.md">Deutsch</a></p>

**Docker 0.1.3 Preview** · [Downloads & checksums](https://github.com/square-com-de/plx/releases/tag/v0.1.3) · [Release status](RELEASE.md)

Run PLX on your own server, view the data your Porsche reports, and choose what to send to Loxone or another MQTT consumer. Docker and the LoxBerry 4 plugin share the same German/English web interface.

## See it in action

![PLX 0.1.3 dashboard showing a vehicle image, battery and range](docs/preview/public-overview.png)

*The real PLX interface with simulated measurements, not a live account screenshot. The model illustration comes from Porsche Connect. Available data depends on your vehicle and Connect contract.*

## What you can do

- **See the essentials:** battery, range, charge target and measurement age in a compact dashboard.
- **Choose your vehicles:** sign in with your own Porsche account and display its vehicle images.
- **Explore reported data:** search and filter parameters such as tires, charging, doors, climate, trips and maintenance where supported.
- **Send only selected MQTT values:** in Simple mode, two selected tire pressures produce two numeric value topics in bar.
- **Prepare Loxone inputs:** export selected numeric values as XML/CSV; detailed MQTT is available when you need freshness signals.
- **Use the same interface in two languages:** German/English, in Docker or as a LoxBerry 4 plugin.

PLX reads status; it does not remote-control or wake your car. **It still needs Porsche's cloud and a compatible Porsche Connect account.** Hosting PLX yourself does not make the vehicle API local.

## Quick start

For a **fresh installation** on a Linux host with Docker Compose and `curl`. Use an administrator shell with Docker access. The public image needs no GitHub account or registry token.

Replace **192.0.2.10** below with the IP or DNS name of your Docker server, without `https://`, path or port. A DNS name must already resolve to that server from your browser. Run in a new directory:

```sh
set -eu
mkdir plx && cd plx
curl -fLO https://github.com/square-com-de/plx/releases/download/v0.1.3/compose.yaml
printf 'PLX_HOST=192.0.2.10\n' > .env
docker compose up -d --wait --wait-timeout 90
docker compose exec -T plx cat /data/config/web-password.txt
```

1. Open **`https://<your-server>:8443`**.
2. **Before entering credentials, establish trust for your server certificate.** PLX generates a matching self-signed certificate; browsers will not trust it automatically. Check its fingerprint from the server with `docker compose exec -T plx openssl x509 -in /data/tls/cert.pem -noout -fingerprint -sha256`, then use your client's certificate-trust process or your own suitable trusted certificate. Do not disable TLS verification. See [HTTPS and first start](INSTALL.md#start).
3. Sign in as **`admin`** with the password shown by the last command. It is deliberately printed only in your server console; keep it private.

PLX generates its password and TLS files once in a **persistent named volume**, alongside settings and any saved Porsche session. Keep the same Compose directory/project and volume for updates; do not use `down -v`. [Backup, update and recovery](INSTALL.md#update-backup-and-recovery).

This is the documented release Compose workflow, with [historical quickstart evidence](docs/QUICKSTART-0.1.2.md). A fresh deployment of the exact 0.1.3 image also passed [Portainer, login, restart and HTTPS-proxy checks](docs/DEPLOYMENT-0.1.3.md). These records describe their actual scopes, not every host or installation method.

## First use

1. In **Porsche account**, sign in to Porsche and complete a CAPTCHA if requested.
2. Load your vehicles, select the ones to use in **Setup**, and save.
3. Review vehicle status and measurement age. Automatic polling and MQTT start **disabled**; enable polling when you are ready.
4. To send data, configure your actual MQTT broker, select only the values you want, then enable MQTT and save. Simple mode is the default. Subscribe to `porsche2lox/#`, or your own prefix.

A web-proxy address is not automatically an MQTT broker. PLX uses its own session and topics; it does not migrate or replace another integration automatically. [MQTT setup and troubleshooting](docs/MANUAL.md#mqtt-and-loxone).

## Other installation paths

| Your setup | Start here |
| --- | --- |
| Portainer | [Create a separate stack](INSTALL.md#portainer) with the release Compose file; set `PLX_HOST` and read the password in its container console. |
| LoxBerry 4 | [Import PLX-LoxBerry-0.1.4-New-Installation.zip](https://github.com/square-com-de/plx/releases/download/v0.1.4/PLX-LoxBerry-0.1.4-New-Installation.zip) through the plugin manager — not GitHub's source ZIP. **0.1.4 Preview is a new company-identity installation, not an in-place upgrade.** Removing the old plugin can delete its settings and sessions. [Read first](docs/RELEASE-0.1.4-LoxBerry.md). [Installation](INSTALL.md#alternatives-and-limits). |
| LoxBerry behind an HTTPS proxy | [Configure the immediate trusted proxy](docs/REVERSE-PROXY.md); installing the plugin alone does not identify your proxy. |
| Proxmox or a custom container setup | [Container, backup and recovery guide](docs/PROXMOX-CONTAINER.md). Run Docker in a Linux VM, not on the hypervisor. |

Keep PLX on a trusted LAN. Other ports, certificate changes, reverse proxies and existing explicit password secrets are covered in [installation](INSTALL.md) and the [Docker reference (German)](docs/DOCKER.md).

## Preview boundaries

**0.1.3 is Preview, not Stable.** Linux/AMD64 has runtime evidence. AMD64/ARM64 images are published, but real ARM64, Podman/rootless and native installation outside LoxBerry remain unqualified. Complete MQTT Gateway → Loxone Miniserver acceptance remains open. A successful installation is not proof of live Porsche login, token refresh or support for every model. [Release notes](docs/RELEASE-0.1.3.md) · [Tests](docs/TESTS.md).

**For automations that depend on fresh data:** Simple MQTT sends the last reported value, or `null` when missing, without heartbeat/availability topics. Retained broker values can survive a stopped container or failed connection. Check age/status in PLX, or use detailed mode for freshness signals. A cloud refresh is not a new vehicle measurement. [Manual](docs/MANUAL.md).

## Documentation

| Topic | Guide |
| --- | --- |
| Installation, updates and recovery | [Installation](INSTALL.md) · [Container operations](docs/PROXMOX-CONTAINER.md) |
| Everyday use and troubleshooting | [Manual](docs/MANUAL.md) |
| MQTT, XML and Loxone mapping | [Loxone reference (German)](docs/LOXONE.md) |
| Architecture, authentication and data quality | [Technical reference (German)](docs/TECHNICAL.de.md) |
| Releases and changes | [Release overview](RELEASE.md) · [Changelog](CHANGELOG.md) |
| Tested workflows and lessons learned | [Installation lessons](docs/INSTALLATION-LESSONS.md) · [0.1.1](docs/QUICKSTART-0.1.1.md) · [0.1.2](docs/QUICKSTART-0.1.2.md) · [0.1.3 artifacts](docs/QUICKSTART-0.1.3.md) · [0.1.3 deployment](docs/DEPLOYMENT-0.1.3.md) |

## Get help or contribute

Questions, bug reports and feedback are welcome: [GitHub Issues](https://github.com/square-com-de/plx/issues/new/choose) or [plx@square-com.de](mailto:plx@square-com.de), without a GitHub account. Include your PLX version, Docker/LoxBerry setup, vehicle model and a short description.

Remove Porsche IDs, VINs, locations, passwords and tokens from screenshots and logs. Never upload settings files, private keys or backups. Report security issues privately via [SECURITY.md](SECURITY.md).

Want to help? Start with [Contributing](CONTRIBUTING.md) and [automated checks](https://github.com/square-com-de/plx/actions/workflows/docker.yml). Passing CI does not replace vehicle or Miniserver acceptance.

## License

PLX's own code uses the [MIT license](LICENSE), including commercial use under its terms. Dependencies and third-party assets retain their own terms: [Third-party notices](THIRD-PARTY-NOTICES.md). MIT does not grant rights to Porsche trademarks or artwork.

Independent project; not affiliated with or supported by Porsche or Loxone.

<p align="center"><strong>by <a href="https://square-com.de/">square | com</a></strong> · <a href="https://square-com.de/impressum/">Legal notice</a></p>
