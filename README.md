> **PLX 0.1.3 Preview** — [Downloads and checksums](https://github.com/square-com-de/plx/releases/tag/v0.1.3). Not a stable release. Public Docker image: `ghcr.io/square-com-de/plx:0.1.3` (AMD64/ARM64); public pull without a GitHub token. [Status and acceptance](RELEASE.md).

<p align="center"><a href="README.de.md">Deutsch</a> | <a href="README.md">English</a></p>
<p align="center"><img src="icons/icon.svg" width="112" alt="PLX app icon"></p>
<h1 align="center">PLX</h1>
<p align="center">Your Porsche x Loxone in your smart home.</p>
<p align="center"><a href="docs/MANUAL.md">Manual</a> · <a href="INSTALL.md">Installation</a> · <a href="RELEASE.md">Release status</a></p>

**Your Porsche data in one place. Select what your smart home receives.**

PLX brings Porsche Connect vehicle data into a compact dashboard and into Loxone over MQTT. Check battery level, range and tire pressure, browse the measurements your vehicle reports, and choose exactly which values to send.

Docker/Compose is the preferred way to run PLX; the LoxBerry 4 plugin is an alternative. Both use the same German/English web interface, your own Porsche session and a separate MQTT namespace. Vehicle images come from your signed-in Connect account.

PLX runs on your own server. **Vehicle data still comes from the Porsche cloud** and requires a compatible Porsche Connect account. PLX reads status only; it does not remote-control or wake your car.

## Features

- Sign in to Porsche, complete a CAPTCHA if requested, and keep your session across restarts.
- Select vehicles and see their model image, battery, range and reported measurement age.
- Search and filter available vehicle parameters, including tire pressure, charging, doors, climate, trips and maintenance where supported.
- Select exactly what MQTT sends: two selected tire pressures produce two numeric topics in bar.
- Use optional detailed diagnostics or export selected numeric inputs as Loxone XML/CSV.
- Switch between German and English; your browser remembers your choice.
- Run over HTTPS in Docker on AMD64/ARM64 or as a LoxBerry 4 plugin.

## Preview

![PLX dashboard with simulated vehicle data](docs/preview/public-overview.png)

*Example measurements are simulated; the vehicle illustration comes from Porsche Connect. Available parameters depend on your car and Connect contract.*

## Install and get started

**Docker/Compose is preferred.** Provide the server IP/DNS name once; PLX creates its private password, matching self-signed TLS certificate and persistent data volume automatically. No first-start mode choice or secret-file ownership steps. LAN access is the default; certificate trust and your Porsche account remain explicit prerequisites. Follow the [short installation guide](INSTALL.md).

On a Linux Docker host, run in a new directory; **replace 192.0.2.10 with the server IP or DNS name** (no scheme/port):

```sh
set -eu
mkdir plx && cd plx
curl -fLO https://github.com/square-com-de/plx/releases/download/v0.1.3/compose.yaml
printf 'PLX_HOST=192.0.2.10\n' > .env
docker compose up -d --wait --wait-timeout 90
docker compose exec -T plx cat /data/config/web-password.txt
```

Then open `https://<your-server>:8443` and sign in as `admin` with the private password shown in your console. Explicitly trust your own server certificate before sign-in; [installation](INSTALL.md#start) explains the fingerprint and limits. Do not disable TLS verification.

Portainer uses the same release Compose file. LoxBerry4 remains an [alternative](INSTALL.md#alternatives-and-limits) using its dedicated plugin ZIP. Podman/rootless and real ARM64 runtime keep their separate unqualified status. Existing 0.1.0 installs and artifacts are not silently replaced.

Simple MQTT is the default: select only the wanted values and subscribe to `porsche2lox/#`. Optional advanced settings remain available later without reinstallation. [Manual](docs/MANUAL.md) · [Release 0.1.3 changes](docs/RELEASE-0.1.3.md).

## Feedback & contact

Tried PLX? Feedback is welcome — including what works well!

- **By email, no GitHub account needed:** [plx@square-com.de](mailto:plx@square-com.de)
- [Feedback or questions](https://github.com/square-com-de/plx/issues/new?template=feedback_question.md)
- [Report a bug or suggest an improvement](https://github.com/square-com-de/plx/issues/new/choose)

Include your PLX version, Docker or LoxBerry setup, vehicle model and a short description. Remove Porsche IDs, VINs, locations, passwords and tokens from screenshots or logs. Report security issues privately; see [security reporting](SECURITY.md).

## Release status and limits

**0.1.3 Preview is published.** This change replaces project artwork only. Historical 0.1.2 public-artifact acceptance is recorded separately; no fresh live Porsche login, token refresh or vehicle-fetch acceptance is claimed for 0.1.3.

A complete MQTT Gateway → Loxone Miniserver acceptance test remains open. Tests do not qualify every Porsche model, contract or future API version. See [release notes](docs/RELEASE-0.1.3.md) and [test evidence](docs/TESTS.md).

**Freshness matters:** simple MQTT sends the last reported value and `null` for missing values. It has no heartbeat or availability topics; retained values remain after a stopped container or failed connection. Check age/status in PLX or use detailed mode when your automation requires freshness signals. A cloud refresh is not a new vehicle measurement.

PLX uses its own session and topics. It does not import or replace an existing Taycan integration automatically.

## Documentation

| Topic | Start here |
| --- | --- |
| Setup, Docker and LoxBerry | [Installation](INSTALL.md) |
| Everyday use and troubleshooting | [Manual](docs/MANUAL.md) |
| Container, HTTPS, volumes and registry | [Docker guide (German)](docs/DOCKER.md) |
| MQTT, XML and Loxone mapping | [Loxone guide (German)](docs/LOXONE.md) |
| Architecture, authentication and data quality | [Technical reference (German)](docs/TECHNICAL.de.md) |
| Current preview and downloads | [Release overview](RELEASE.md) |
| Changes | [Changelog](CHANGELOG.md) |
| Tests and contributions | [Contributing](CONTRIBUTING.md) |
| Sources and third-party assets | [Third-party notices](THIRD-PARTY-NOTICES.md) |

## Quality and security

[GitHub checks](https://github.com/square-com-de/plx/actions/workflows/docker.yml) run the tests, build and smoke-test the standalone container, then publish AMD64/ARM64 development images. Release images are public; no registry login is required. Passing CI is not a complete vehicle or Miniserver acceptance test.

Never upload Porsche tokens, private keys, settings files or private backups to issues or pull requests. See [security reporting](SECURITY.md).

## License

PLX’s own code is licensed under [MIT](LICENSE), including commercial use under its terms. Third-party dependencies and Porsche branding retain their own terms; see [notices](THIRD-PARTY-NOTICES.md). The MIT license does not grant rights to Porsche trademarks or artwork.

Independent project; not affiliated with or supported by Porsche or Loxone.

<p align="center"><strong>by <a href="https://square-com.de/">square | com</a></strong> · <a href="https://square-com.de/impressum/">Impressum / Legal notice</a></p>

[Historical0.1.1 quickstart: executed commands, passed checks and limits](docs/QUICKSTART-0.1.1.md).

[PLX 0.1.2 Preview: tested public Docker and LoxBerry artifacts, results and limits](docs/QUICKSTART-0.1.2.md).

[0.1.3 public-artifact branding and test-system acceptance](docs/QUICKSTART-0.1.3.md).
