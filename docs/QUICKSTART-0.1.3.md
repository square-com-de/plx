# PLX 0.1.3 Preview — branding acceptance

Accepted within the scope below on 25 October 2026. This is a branding-only release; previous live vehicle or lifecycle results are not automatically repeated by it.

## Exact public artifacts

- Source/tag `a924a8378e938bd46edb2a4fa93eb24b05a241fe`; [release CI40183516373](https://github.com/square-com-de/plx/actions/runs/40183516373) passed.
- Image `ghcr.io/square-com-de/plx@sha256:e5fbe30974c6e8ac4510438a6d47e38756225e10d3133ec511e029de4ae66542`.
- Compose SHA256 `5c346326f07a2b29129790232bdc59e7ed9ae24a3f818afe2cfc3bdfd281c308`.
- LoxBerry ZIP SHA256 `de13fde03103b06d506b4cb33ce1ca9ce5231f9d36f8d61b78d531729725b8c7`.
- Docker bundle SHA256 `5a5443a1da2359617feea81db8c0e33454254ad28777502d1db04543c95280c0`.

[Versioned downloads](../RELEASE.md). All five files were downloaded anonymously and verified. All 71 ZIP members matched reviewed source bytes; all 48 inner bundle checksums passed and bundled Compose matched the standalone download. Both platform manifests/configurations and all 26 image layers were independently digest-verified. This is image-content validation, not ARM64 runtime execution.

## Artwork and separate runtime checks

The approved 1254×1254 PNG SHA256 `bbd8b07d633b944703f651eacbf96984956b6b6e0f5fb6803e93caaffa63470b` is unchanged. Both SVGs embed byte-identical original bytes. Five new simulated UI PNGs were visually checked; eight obsolete branding screenshots were replaced or removed. Product model illustration remains separately attributed. Source/archive/image checks found no known old project-logo or embedded-crest hashes. Hash scans complement visual checks and cannot prove the absence of every re-encoded motif anywhere on the Internet.

The existing Portainer test stack was updated to the exact public image after a private cold backup. Health, authenticated UI, exact embedded original logo, CA/IP-verified HTTPS and an external-client login passed. Settings, saved Porsche session, web password, TLS, the two pressure selections and existing polling/MQTT flags were preserved. Eight other running containers retained identity/image/start time. No manual vehicle command was issued; existing background settings were retained and are not a new live Porsche acceptance test.

On the separate LoxBerry test VM, official update from the exact public ZIP passed. Actual HTTPS UI/asset reads and the LoxBerry host icon matched the ZIP/original PNG. Settings, saved session and trusted-proxy bytes were preserved. Test polling/MQTT remained disabled; other running units were unchanged. No Porsche cloud or MQTT call was part of that plugin test. This run checked update/logo delivery, not another clean-install or complete proxy matrix qualification.

Local preparation passed 127 existing tests (5 platform skips), three branding/recursive-archive regressions, documentation checks and simulated DE/EN desktop/account/settings/mobile390 rendering without overflow/JS errors/external requests. Final exact source passed CI and independent review before publication.

## Cleanup and limits

Old public releases/images are scheduled for targeted withdrawal after this checked replacement. Current cleanup status is tracked in [gate #1](https://github.com/square-com-de/plx/issues/1); no deletion is implied by this acceptance report. Private rollback copies retain historical artifacts. Historical Git blobs/PR refs, source archives and external caches may remain accessible even after old distribution withdrawal. No automatic history rewrite or absolute Internet-clean claim.

No new live Porsche login/token refresh/vehicle-fetch, production broker/Miniserver, final-image VM cold reboot, Portainer-GUI deployment walkthrough, Podman/rootless or real ARM64 runtime qualification. Taycan app unchanged; no Stable/latest promotion. [Sanitized evidence](evidence/2026-10-25-branding-public.json).
