# PLX 0.1.4 Preview — LoxBerry new installation

**LoxBerry plugin only. This is a new installation with a new company identity, not an in-place update of older PLX/Porsche2Lox plugins.**

The plugin author is now **square | com**, with contact **plx@square-com.de**. LoxBerry uses the author information as part of the plugin identity. Changing it deliberately creates a different identity; an existing installation is not migrated automatically.

## Download and install

- [PLX-LoxBerry-0.1.4-New-Installation.zip](https://github.com/square-com-de/plx/releases/download/v0.1.4/PLX-LoxBerry-0.1.4-New-Installation.zip) — dedicated LoxBerry 4 import package.
- [SHA256SUMS](https://github.com/square-com-de/plx/releases/download/v0.1.4/SHA256SUMS) and [source/package manifest](https://github.com/square-com-de/plx/releases/download/v0.1.4/manifest.json).

If an older PLX/Porsche2Lox plugin is installed, do **not** install this ZIP alongside it or treat it as an upgrade. Use LoxBerry's plugin manager to remove the old installation first. Uninstalling can remove its settings and saved session; keep a private backup first if you may need a return path. Then import the dedicated new-installation ZIP through the plugin manager. Do not use GitHub's generic source ZIP.

Set up your Porsche account and select vehicles again. No old credentials, session, settings or proxy trust file are imported. Initial polling and MQTT are disabled. For an HTTPS proxy to an HTTP LoxBerry backend, explicitly configure its immediate trusted peer: [proxy guide](REVERSE-PROXY.md). Installing the ZIP alone cannot discover that trust relationship.

The technical plugin name/folder preference remains `porsche2lox`; the changed author identity is why old and new packages are distinct. Automatic plugin updates remain disabled.

## What changes

- Company author name and contact in LoxBerry's plugin metadata.
- Plugin version 0.1.4, also rendered into the packaged UI's Preview badge.
- Current documentation and the original approved PLX artwork.

The Porsche/API/authentication/MQTT implementation and installer behavior are unchanged from 0.1.3. No Docker image, Compose bundle or container deployment is part of this release. **Docker remains on [0.1.3 Preview](https://github.com/square-com-de/plx/releases/tag/v0.1.3)**; an existing container does not change when this plugin package is published.

## Validation and limits

The dedicated package workflow builds the ZIP from explicit inputs, checks root layout, author identity, version display, private-state exclusion, archive paths, symlinks, checksums and original artwork, and tests rejection cases. The manifest records source commit/tree, generated version badge and per-member hashes. Publication refuses an existing release/tag instead of replacing older bytes.

This new identity has **not** been installed on a real LoxBerry host in this release process. No new test VM, live Porsche login, token refresh, MQTT publish or physical Miniserver test is claimed. Existing [0.1.3 installer/runtime evidence](QUICKSTART-0.1.3.md) remains historical; it does not prove an upgrade between different author identities. This is still Preview, not Stable.

[Installation](../INSTALL.md) · [Deutsch](../INSTALL.de.md) · [Releases](../RELEASE.md) · [License](../LICENSE)
