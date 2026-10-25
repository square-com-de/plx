# PLX 0.1.0 Preview — release draft

> Historical record. Old-logo distributions 0.1.0–0.1.2 are scheduled for withdrawal after the verified 0.1.3 replacement. Do not execute historical download commands; use current [INSTALL](../INSTALL.md). Git history/source access is not erased by release withdrawal.

Release: `v0.1.0` (historical distribution; withdrawal scheduled), marked **pre-release**. LoxBerry metadata keeps numeric version `0.1.0`.

## Release notes / Deutsch

PLX bringt Porsche Connect ins intelligente Zuhause: als eigenständiger Docker-Container und als LoxBerry-4-Plugin, mit derselben kompakten Weboberfläche.

- Porsche-Anmeldung, Fahrzeugauswahl, gespeicherte Sitzung und Token-Erneuerung.
- Fahrzeugbild aus dem eigenen Connect-Konto, Batterie-/Reichweitenübersicht und durchsuchbare Fahrzeugdaten.
- Deutsch und Englisch mit gespeichertem Sprachschalter; roter Verbindungspunkt bei erfolgreicher Porsche-Verbindung.
- MQTT sendet im einfachen Format genau die gewählten Werte. Zwei ausgewählte Reifendrücke ergeben zwei Topics mit Zahlen in bar.
- Optional ausführliche MQTT-Diagnose sowie XML-/CSV-Export zur Loxone-Anbindung.
- Eigene Sitzung und eigene Topics; bestehende Taycan-Installationen werden nicht automatisch übernommen.

## Release notes / English

PLX brings Porsche Connect into your smart home as a standalone Docker container or LoxBerry 4 plugin, sharing the same compact dashboard.

- Porsche sign-in, vehicle selection, persisted session and token renewal.
- Account-provided vehicle image, battery/range overview and searchable vehicle data.
- Persistent German/English switch and red indicator when Porsche Connect is connected.
- Simple MQTT output sends only selected values: two tire pressures mean two numeric topics in bar.
- Optional detailed MQTT diagnostics and Loxone XML/CSV export.
- Independent session and topics; no automatic migration of existing Taycan installations.

## Included artifacts

`python tools/prepare_release.py` prepares `dist/release-v0.1.0/`:

- `PLX-LoxBerry-0.1.0.zip` for the LoxBerry plugin manager.
- `PLX-Docker-0.1.0.tar.gz` with pinned `compose.yaml`, instructions, license and internal checksums. The image is pulled from GHCR; this is not an offline image export.
- `compose.yaml`, also available individually, pinned to the tested multi-platform container digest.
- German/English instructions, MIT LICENSE, these notes and third-party notices.
- `manifest.json` with source/build provenance and `SHA256SUMS`.

The container is built from the release source for AMD64/ARM64 by [Publish PLX Preview](https://github.com/square-com-de/plx/actions/workflows/release.yml). The attached `manifest.json` records its exact source SHA, workflow run and image digest. Public versioned tag: `ghcr.io/square-com-de/plx:0.1.0`.

The release image is public. The preview bundle does not contain credentials, user settings, Porsche tokens, vehicle data or private certificates. The bundled crest is a branding asset; see the decision below.

## Verified

- Local tests: 90 passed, four platform-dependent skips; Linux CI passed additional platform checks.
- CI built and smoke-tested Docker, then published AMD64 and ARM64 images.
- Separate Docker test instance: HTTPS and PLX login, real Porsche login/fetch, exactly two retained numeric pressure topics after migration.
- Browser checks: language persistence, dynamic status, English search, unsaved input preservation, unchanged MQTT selection, mobile layout.
- Configuration, Porsche session, TLS and web-password files unchanged by the latest UI deployment; seven other containers unchanged.
- Final LoxBerry clean install/update acceptance: official installer, persisted settings/session, HTTPS/CSRF, real Porsche fetch, DE/EN/mobile browser and exactly two numeric pressure messages on an isolated loopback MQTT broker. An update state-loss bug was corrected with the official preupgrade hook; see docs/TESTS.md. Exact final ZIP hash is recorded in the external acceptance proof.

## Publication and remaining acceptance

The user approved public repository/image visibility and publication of both distributions. Original code uses MIT; third-party trademarks/artwork retain their own rights and are not relicensed. The release workflow tests the source, builds AMD64/ARM64, pins the produced digest in the Docker bundle, prepares the plugin ZIP and uploads checksums. Runtime/installer files are compared with the VM-accepted program payload; documentation-only archive changes are not called another exact-ZIP VM run.

Full MQTT Gateway → Loxone Miniserver acceptance is still open. This is documented as a preview limitation rather than a claim of stable or universal compatibility. Preserve private backups and data-volume ownership when deploying or rolling back.

## Limits to communicate

Read-only integration; no remote control or wake commands. Available measurements depend on the vehicle/contract. Simple MQTT sends last reported values and has no heartbeat/age flags; retained values remain after shutdown. Use detailed mode when freshness signals are required. No promise of compatibility with all Porsche models or future API versions.
