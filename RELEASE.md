# PLX release overview / Release-Übersicht

**PLX 0.1.0 Preview — [release downloads](https://github.com/square-com-de/plx/releases/tag/v0.1.0). Not a stable release.**

**PLX 0.1.0 Preview — [Release-Downloads](https://github.com/square-com-de/plx/releases/tag/v0.1.0). Kein Stable-Release.**

| Distribution / Paket | Purpose / Zweck |
| --- | --- |
| `PLX-Docker-0.1.0.tar.gz` | Pinned Compose definition, instructions, MIT license and checksums. Image is pulled separately from GHCR. / Feste Compose-Datei, Anleitung, MIT-Lizenz und Prüfsummen; das Image wird aus GHCR geladen. |
| `PLX-LoxBerry-0.1.0.zip` | Installable LoxBerry plugin package, not the generic GitHub source ZIP. / Installierbares LoxBerry-Paket, nicht das allgemeine GitHub-Quellcode-ZIP. |
| `SHA256SUMS` | Checksums for the prepared artifacts. / Prüfsummen der vorbereiteten Pakete. |

Public image: `ghcr.io/square-com-de/plx:0.1.0` for AMD64/ARM64. Pull without a registry login; the Docker bundle pins the release digest. No `latest` tag is promoted for this preview.

Öffentliches Image: `ghcr.io/square-com-de/plx:0.1.0` für AMD64/ARM64. Ohne Registry-Login abrufbar; das Docker-Paket verwendet den festen Release-Digest. Für diese Preview wird kein `latest`-Tag gesetzt.

## Acceptance / Abnahme

- Docker: real separate test-container acceptance, HTTPS sign-in, Porsche fetch, DE/EN and selected pressure output. / Echte separate Testcontainer-Abnahme, HTTPS-Anmeldung, Porsche-Abruf, DE/EN und ausgewählte Druckwerte.
- LoxBerry: clean install and update with preserved settings/session, real HTTPS/PHP interface, mobile browser, Porsche fetch and exactly two numeric messages on an isolated broker. A state-loss update bug was fixed with preroot/preupgrade hooks. / Neuinstallation und Update mit Datenerhalt, echte HTTPS-/PHP-Oberfläche, Mobilansicht, Porsche-Abruf und genau zwei numerische Werte am isolierten Broker; Updatefehler durch preroot/preupgrade-Hooks behoben.
- Loxone: full MQTT Gateway → Miniserver acceptance still open. / Vollständige Abnahme bis zum Miniserver noch offen.

Only documentation and packaging were revised for the new public-facing project pages. Runtime and installer-hook contents are compared with the VM-accepted package; a documentation-only ZIP revision has a different checksum and is not represented as another exact-ZIP VM run.

Für die neue Projektseite wurden Dokumentation und Paketinhalt angepasst. Programmdateien und Installer-Hooks werden mit dem auf der VM abgenommenen Paket verglichen. Ein allein durch Dokumentation geändertes ZIP hat eine andere Prüfsumme und wird nicht als zusätzlicher exakter VM-ZIP-Test ausgegeben.

[Detailed release notes / Release-Hinweise](docs/RELEASE-0.1.0.md) · [Tests](docs/TESTS.md) · [Changes / Änderungen](CHANGELOG.md)
