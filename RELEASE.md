# PLX releases / Releases

**0.1.2 Preview is prepared, not published.** [Preparation notes and remaining gates](docs/RELEASE-0.1.2.md). No Stable/latest or production promotion. The last published release remains [0.1.1 Preview](https://github.com/square-com-de/plx/releases/tag/v0.1.1).

The new release will contain the reviewed LoxBerry trusted-HTTPS-proxy fix. Intended dedicated assets: `PLX-LoxBerry-0.1.2.zip`, `PLX-Docker-0.1.2.tar.gz`, pinned `compose.yaml`, `manifest.json`, `SHA256SUMS`. The registry image must be newly built and pinned by its actual digest; no unpublished digest is invented.

The release workflow is manual and refuses an existing release/image or indeterminate existence check. Keep this preparation branch separate from the accepted0.1.1 documentation until controlled publication and exact-artifact acceptance. [0.1.1 acceptance](docs/QUICKSTART-0.1.1.md) and old archives remain unchanged.
