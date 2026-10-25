> **Nur Release-Vorbereitung:**0.1.2 ist noch nicht veröffentlicht. Die Befehle unten gelten für das kommende Release; bis zur kontrollierten Veröffentlichung und Abnahme [öffentliches0.1.1](https://github.com/square-com-de/plx/releases/tag/v0.1.1) verwenden.

> **PLX 0.1.2 Preview** — [Downloads und Prüfsummen](https://github.com/square-com-de/plx/releases/tag/v0.1.2). Kein Stable-Release. Vorgesehenes Docker-Image: `ghcr.io/square-com-de/plx:0.1.2` (AMD64/ARM64), nach Veröffentlichung ohne GitHub-Token abrufbar. [Stand und Abnahme](RELEASE.md).

<p align="center"><a href="README.de.md">Deutsch</a> | <a href="README.md">English</a></p>
<p align="center"><img src="icons/icon.svg" width="112" alt="PLX app icon"></p>
<h1 align="center">PLX</h1>
<p align="center">Dein Porsche x Loxone in Deinem intelligenten Zuhause.</p>
<p align="center"><a href="docs/MANUAL.de.md">Handbuch</a> · <a href="INSTALL.de.md">Installation</a> · <a href="RELEASE.md">Release-Stand</a></p>

**Deine Porsche-Daten im Blick. Du entscheidest, was dein Zuhause empfängt.**

PLX bringt die Fahrzeugdaten aus Porsche Connect in eine kompakte Übersicht und per MQTT in Loxone. Sieh Akkustand, Reichweite und Reifendruck, durchsuche die vom Fahrzeug gelieferten Daten und wähle gezielt aus, welche Werte weitergegeben werden.

Docker/Compose ist der bevorzugte PLX-Installationsweg; das LoxBerry-4-Plugin bleibt eine Alternative. Beide verwenden dieselbe deutsche und englische Weboberfläche, eine eigene Porsche-Sitzung und eigene MQTT-Topics. Das Fahrzeugbild kommt aus deinem angemeldeten Connect-Konto.

PLX läuft auf deinem eigenen Server. **Die Fahrzeugdaten kommen weiterhin aus der Porsche-Cloud**; ein kompatibles Porsche-Connect-Konto ist erforderlich. PLX liest Statusdaten, steuert das Fahrzeug nicht fern und weckt es nicht auf.

## Was PLX kann

- Bei Porsche anmelden, bei Bedarf CAPTCHA bestätigen und die Sitzung über Neustarts erhalten.
- Fahrzeuge auswählen und Modellbild, Batterie, Reichweite und Messalter anzeigen.
- Fahrzeugparameter durchsuchen und filtern: je nach Unterstützung etwa Reifendruck, Laden, Türen, Klima, Fahrten und Wartung.
- MQTT-Werte gezielt auswählen: Zwei angehakte Reifendrücke ergeben zwei numerische Topics in bar.
- Optional ausführliche Diagnose verwenden oder ausgewählte numerische Werte als Loxone-XML/CSV exportieren.
- Zwischen Deutsch und Englisch wechseln; der Browser merkt sich die Sprache.
- Über HTTPS als Docker-Container für AMD64/ARM64 oder auf LoxBerry 4 betreiben.

## So sieht es aus

![PLX-Übersicht mit simulierten Fahrzeugdaten](docs/preview/public-overview.png)

*Simulierte Messwerte, Modellbild aus Porsche Connect. Welche Parameter verfügbar sind, hängt vom Fahrzeug und Connect-Vertrag ab.*

## Installieren und starten

**Docker/Compose ist bevorzugt.** Einmal Server-IP/DNS angeben; PLX erzeugt privates Passwort, passendes selbstsigniertes TLS-Zertifikat und persistentes Datenvolume automatisch. Keine Erststart-Moduswahl oder Secret-Dateirechte-Nacharbeit. LAN-Zugriff ist Standard; Zertifikatsvertrauen und eigenes Porsche-Konto bleiben klar benannte Voraussetzungen. Zur [kurzen Installation](INSTALL.de.md).

Auf einem Linux-Docker-Host in einem neuen Verzeichnis ausführen; **192.0.2.10 durch die Server-IP oder den DNS-Namen ersetzen** (ohne Protokoll/Port):

```sh
set -eu
mkdir plx && cd plx
curl -fLO https://github.com/square-com-de/plx/releases/download/v0.1.2/compose.yaml
printf 'PLX_HOST=192.0.2.10\n' > .env
docker compose up -d --wait --wait-timeout 90
docker compose exec -T plx cat /data/config/web-password.txt
```

Danach `https://<dein-server>:8443` öffnen, Benutzer `admin` und das in deiner Konsole ausgegebene private Passwort. Vor der Anmeldung dem eigenen Serverzertifikat ausdrücklich vertrauen; die [Installation](INSTALL.de.md#start) erklärt Fingerabdruck und Grenzen. Keine TLS-Prüfung abschalten.

Portainer verwendet dieselbe Release-Compose-Datei. LoxBerry4 bleibt [Alternative](INSTALL.de.md#alternativen-und-grenzen) mit dediziertem Plugin-ZIP. Podman/Rootless und echter ARM64-Betrieb behalten ihren getrennten nicht abgenommenen Status. Bestehende0.1.0-Installationen/-Dateien werden nicht heimlich ersetzt.

Einfaches MQTT ist Standard: gewünschte Werte auswählen, `porsche2lox/#` abonnieren. Erweiterte Einstellungen später optional ohne Neuinstallation. [Handbuch](docs/MANUAL.de.md) · [Änderungen0.1.2](docs/RELEASE-0.1.2.md).

## Feedback & Kontakt

Du hast PLX ausprobiert? Ich freue mich über dein Feedback – auch darüber, was gut funktioniert!

- **Per E-Mail, ohne GitHub-Konto:** [plx@square-com.de](mailto:plx@square-com.de)
- [Feedback oder Frage stellen](https://github.com/square-com-de/plx/issues/new?template=feedback_question.md)
- [Fehler melden oder Verbesserung vorschlagen](https://github.com/square-com-de/plx/issues/new/choose)

Hilfreich sind PLX-Version, Docker-/LoxBerry-Umgebung, Fahrzeugmodell und eine kurze Beschreibung. Porsche-ID, Fahrzeugnummer, Standort, Passwörter und Tokens vorher aus Screenshots und Logs entfernen. Sicherheitsprobleme vertraulich melden; siehe [Sicherheit](SECURITY.md).

## Release-Stand und Grenzen

**0.1.2 Preview.** Der Start mit automatischem Passwort und hostpassendem TLS wurde für0.1.1 abgenommen; die exakte0.1.2-Artefaktabnahme bleibt in [#1](https://github.com/square-com-de/plx/issues/1) geführt. Frühere0.1.0-Nachweise zu Anmeldung, Fahrzeugabruf und zwei Druckwerten bleiben historisch und sind kein neuer echter Porsche-Test von0.1.2.

Die vollständige Abnahme über MQTT Gateway bis zum Loxone-Miniserver bleibt offen. Die Tests bestätigen nicht jedes Porsche-Modell, jeden Vertrag oder zukünftige API-Versionen. Siehe [Release-Hinweise](docs/RELEASE-0.1.2.md) und [Testnachweise](docs/TESTS.md).

**Datenalter beachten:** Einfaches MQTT sendet den zuletzt gemeldeten Wert und bei fehlenden Werten `null`. Es hat keinen Heartbeat und keine zusätzlichen Verfügbarkeitsthemen. Gespeicherte Brokerwerte bleiben auch nach Verbindungsabbruch oder Dienstende erhalten. Alter/Status in PLX prüfen oder für entsprechende Automationen das ausführliche Format verwenden. Ein Cloud-Abruf ist keine neue Messung des Fahrzeugs.

PLX nutzt eine eigene Sitzung und eigene Topics. Eine bestehende Taycan-Integration wird nicht automatisch importiert oder ersetzt.

## Dokumentation

| Thema | Einstieg |
| --- | --- |
| Einrichtung, Docker und LoxBerry | [Installation](INSTALL.de.md) |
| Bedienung und Fehlerbehebung | [Handbuch](docs/MANUAL.de.md) |
| Container, HTTPS, Daten und Registry | [Docker-Anleitung](docs/DOCKER.md) |
| MQTT, XML und Loxone-Zuordnung | [Loxone-Anleitung](docs/LOXONE.md) |
| Architektur, Anmeldung und Datenqualität | [Technische Referenz](docs/TECHNICAL.de.md) |
| Preview und Downloads | [Release-Übersicht](RELEASE.md) |
| Änderungen | [Changelog](CHANGELOG.md) |
| Tests und Mitarbeit | [Entwicklung](CONTRIBUTING.md) |
| Quellen und Drittanbieterbestandteile | [Dritthinweise](THIRD-PARTY-NOTICES.md) |

## Tests und Sicherheit

[Automatische GitHub-Prüfungen](https://github.com/square-com-de/plx/actions/workflows/docker.yml) führen Tests aus, bauen und starten den Container und erzeugen anschließend AMD64-/ARM64-Entwicklungsimages. Release-Images sind öffentlich; ein Registry-Login ist nicht nötig. Ein grüner Lauf ersetzt keine vollständige Fahrzeug- oder Miniserver-Abnahme.

Keine Porsche-Tokens, privaten Schlüssel, Einstellungsdateien oder privaten Sicherungen in Issues oder Pull Requests hochladen. Siehe [Sicherheit](SECURITY.md).

## Lizenz

Der eigene PLX-Code steht unter [MIT](LICENSE), einschließlich kommerzieller Nutzung unter den Lizenzbedingungen. Fremdbibliotheken und Porsche-Markenzeichen behalten ihre eigenen Bedingungen; siehe [Dritthinweise](THIRD-PARTY-NOTICES.md). Die MIT-Lizenz erteilt keine Rechte an Porsche-Markenzeichen oder -Grafiken.

Unabhängiges Projekt; keine offizielle Verbindung zu oder Unterstützung durch Porsche oder Loxone.

<p align="center"><strong>by <a href="https://square-com.de/">square | com</a></strong> · <a href="https://square-com.de/impressum/">Impressum / Legal notice</a></p>

[Historischer 0.1.1-Quickstart: tatsächliche Befehle, bestandene Prüfungen und Grenzen](docs/QUICKSTART-0.1.1.md).
