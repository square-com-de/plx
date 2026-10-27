# PLX releases / Releases

## 0.1.5 Preview — Docker and LoxBerry plugin

[Release](https://github.com/square-com-de/plx/releases/tag/v0.1.5) · [Changes and installation](docs/RELEASE-0.1.5.md).

- **LoxBerry import:** [PLX-LoxBerry-Plugin-0.1.5.zip](https://github.com/square-com-de/plx/releases/download/v0.1.5/PLX-LoxBerry-Plugin-0.1.5.zip). This dedicated plugin ZIP is the import file; GitHub source archives are not installers.
- **Docker:** [compose.yaml](https://github.com/square-com-de/plx/releases/download/v0.1.5/compose.yaml) and [documentation bundle](https://github.com/square-com-de/plx/releases/download/v0.1.5/PLX-Docker-0.1.5.tar.gz).
- [Checksums](https://github.com/square-com-de/plx/releases/download/v0.1.5/SHA256SUMS) · [source/image/member manifest](https://github.com/square-com-de/plx/releases/download/v0.1.5/manifest.json).

The Docker image is public at `ghcr.io/square-com-de/plx:0.1.5`; the release Compose file pins its accepted immutable digest. No account/token is needed to pull it. Both distributions use the same version and DE/EN UI.

LoxBerry company identity remains **square | com**, matching 0.1.4. Updates from that identity use the plugin manager and retain the same data paths. Historical **dubctrl** installations require a deliberate new installation with private backup first; uninstalling may delete settings/session. Automatic updates remain disabled.

Candidate artifacts are built once and checked before publication; publication reuses their exact bytes and image digest. Current acceptance and remaining limits are recorded in [issue #1](https://github.com/square-com-de/plx/issues/1). This is Preview, without a Stable/latest promotion or claims of a fully qualified physical Miniserver chain, real ARM64, Podman/rootless or native non-LoxBerry runtime.

## Historical previews

## LoxBerry: 0.1.4 Preview — new installation

[Release and dedicated ZIP](https://github.com/square-com-de/plx/releases/tag/v0.1.4) · [New-installation instructions](docs/RELEASE-0.1.4-LoxBerry.md).

Company author **square | com**. New plugin identity: **not** an in-place upgrade or automatic migration of older PLX/Porsche2Lox installations. Remove the earlier plugin before a deliberate fresh installation; settings/session may be deleted. This release publishes no Docker image or container update.

## Docker: 0.1.3 Preview (unchanged)

**[PLX 0.1.3 Preview](https://github.com/square-com-de/plx/releases/tag/v0.1.3)** remains the current Docker version with the exact user-selected original PLX logo.

- [Historical LoxBerry 0.1.3 ZIP — old author identity](https://github.com/square-com-de/plx/releases/download/v0.1.3/PLX-LoxBerry-0.1.3.zip).
- [Docker Compose](https://github.com/square-com-de/plx/releases/download/v0.1.3/compose.yaml) and [Docker bundle](https://github.com/square-com-de/plx/releases/download/v0.1.3/PLX-Docker-0.1.3.tar.gz).
- [Manifest](https://github.com/square-com-de/plx/releases/download/v0.1.3/manifest.json) and [checksums](https://github.com/square-com-de/plx/releases/download/v0.1.3/SHA256SUMS).

[Changes](docs/RELEASE-0.1.3.md) · [Public artifact and separate test-system acceptance](docs/QUICKSTART-0.1.3.md) · [Artwork and cleanup scope](docs/BRANDING.md).

The public source is `a924a8378e938bd46edb2a4fa93eb24b05a241fe`; later documentation does not rebuild or replace versioned assets. Historical [0.1.2 acceptance](docs/QUICKSTART-0.1.2.md) and [0.1.1 acceptance](docs/QUICKSTART-0.1.1.md) describe those versions. Old-logo releases/images are scheduled for targeted withdrawal; Git history, PR refs and external caches are separate residual access paths. No Stable/latest or Taycan/production update.
