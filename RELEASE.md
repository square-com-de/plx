# PLX releases / Releases

**0.1.2 Preview:** [versioned downloads](https://github.com/square-com-de/plx/releases/tag/v0.1.2). No Stable/latest promotion. [Notes and acceptance scope](docs/RELEASE-0.1.2.md).

This separate version contains the reviewed LoxBerry trusted-HTTPS-proxy fix. Dedicated assets: `PLX-LoxBerry-0.1.2.zip`, `PLX-Docker-0.1.2.tar.gz`, pinned `compose.yaml`, `manifest.json`, `SHA256SUMS`. The container reference must be the actual build digest recorded by the release workflow; a prior-version digest is not reused.

The manual release workflow rejects an existing release, Git tag, registry version or indeterminate existence lookup. [Current acceptance gate](https://github.com/square-com-de/plx/issues/1) distinguishes source review from exact public-artifact tests. No live Porsche, physical Miniserver, Podman/ARM64-runtime or production qualification is implied.

The prior [0.1.1 Preview](https://github.com/square-com-de/plx/releases/tag/v0.1.1), its [recorded acceptance](docs/QUICKSTART-0.1.1.md) and all old archives remain unchanged.

[PLX 0.1.2 Preview: tested public Docker and LoxBerry artifacts, results and limits](docs/QUICKSTART-0.1.2.md).
