# PLX 0.1.5 Preview — Docker and LoxBerry plugin

One version for the public Docker image and the dedicated LoxBerry plugin.

## Changes

- Independent MQTT connection status: connected only after broker login succeeds, with disconnect/reconnect and safe error messages. Porsche status remains independent.
- Clear saving/saved/error feedback in German and English. Broker outages no longer discard a changed MQTT selection; explicitly deselected retained values are queued privately for retry. Reselecting a value protects it from pending deletion.
- No catalogue-wide retained-topic purge. Simple mode sends only selected values; detailed output remains optional.
- Compact transparent browser favicon, taken from the approved original PLX artwork, on login and app pages.
- Updated Docker and LoxBerry packages, installation links and release checksums.

## Downloads

- [**PLX-LoxBerry-Plugin-0.1.5.zip — LoxBerry plugin import**](https://github.com/square-com-de/plx/releases/download/v0.1.5/PLX-LoxBerry-Plugin-0.1.5.zip)
- [Docker Compose](https://github.com/square-com-de/plx/releases/download/v0.1.5/compose.yaml)
- [Docker documentation bundle](https://github.com/square-com-de/plx/releases/download/v0.1.5/PLX-Docker-0.1.5.tar.gz)
- [SHA256SUMS](https://github.com/square-com-de/plx/releases/download/v0.1.5/SHA256SUMS) and [manifest](https://github.com/square-com-de/plx/releases/download/v0.1.5/manifest.json)

The public Docker tag is `ghcr.io/square-com-de/plx:0.1.5`; Compose pins the accepted image digest. The Docker bundle contains Compose and documentation, not an offline image. Download the dedicated plugin ZIP for LoxBerry, not GitHub's automatic source ZIP.

## Installation and updates

[English installation](https://github.com/square-com-de/plx/blob/v0.1.5/INSTALL.md) · [Deutsch](https://github.com/square-com-de/plx/blob/v0.1.5/INSTALL.de.md).

**LoxBerry:** company identity is still square | com, the same as 0.1.4. Back up private settings/session first and use the plugin manager update. Historical dubctrl packages have a different identity and require a deliberate fresh installation; removing those packages may delete their data. No automatic migration or update is enabled. Behind an HTTPS proxy, retain/configure the immediate trusted proxy explicitly; direct HTTP is not accepted for credentials.

**Docker:** retain the same project and named data volume. Back up stopped data and Compose first, then update to the reviewed digest. Do not use `down -v`. Default first start generates a private web password and host-matched self-signed certificate; establish trust or supply your own certificate before entering credentials. A web proxy hostname is not automatically the MQTT broker.

## Acceptance and scope

The immutable candidate image and final plugin ZIP are tested before this release is published, without rebuilding or replacing their bytes during promotion. Exact source, image and package checksums are in the attached manifest. Candidate acceptance evidence and remaining limits are recorded in [release gate #1](https://github.com/square-com-de/plx/issues/1).

This is **Preview**, not Stable/latest. Linux/AMD64 is the supported runtime qualification target. ARM64 image availability alone is not a real ARM64 test. Physical MQTT Gateway → Loxone Miniserver acceptance, Podman/rootless and native non-LoxBerry runtime remain unqualified. A retained session file does not prove live Porsche authentication or token refresh; availability depends on vehicle, account, contract and Porsche cloud. No remote vehicle commands are included.

Existing versioned releases are not overwritten. Existing running integrations are not updated by publication. Own PLX code is MIT; upstream software and Porsche-derived model images retain their separate notices and rights.
