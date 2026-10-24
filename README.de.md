> **PLX 0.1.0 Preview** — [Downloads und Prüfsummen](https://github.com/square-com-de/plx/releases/tag/v0.1.0). Kein Stable-Release. Öffentliches Docker-Image: `ghcr.io/square-com-de/plx:0.1.0` (AMD64/ARM64), ohne GitHub-Token abrufbar. [Stand und Abnahme](RELEASE.md).

<p align="center"><a href="README.de.md">Deutsch</a> | <a href="README.md">English</a></p>
<p align="center"><img src="icons/icon.svg" width="112" alt="PLX app icon"></p>
<h1 align="center">PLX</h1>
<p align="center">Dein Porsche x Loxone in Deinem intelligenten Zuhause.</p>
<p align="center"><a href="docs/MANUAL.de.md">Handbuch</a> · <a href="INSTALL.de.md">Installation</a> · <a href="RELEASE.md">Release-Stand</a></p>

**Deine Porsche-Daten im Blick. Du entscheidest, was dein Zuhause empfängt.**

PLX bringt die Fahrzeugdaten aus Porsche Connect in eine kompakte Übersicht und per MQTT in Loxone. Sieh Akkustand, Reichweite und Reifendruck, durchsuche die vom Fahrzeug gelieferten Daten und wähle gezielt aus, welche Werte weitergegeben werden.

PLX läuft als eigenständiger Docker-Container oder als LoxBerry-4-Plugin. Beide verwenden dieselbe deutsche und englische Weboberfläche, eine eigene Porsche-Sitzung und eigene MQTT-Topics. Das Fahrzeugbild kommt aus deinem angemeldeten Connect-Konto.

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

## Installieren und loslegen

**LoxBerry-Import:** [PLX-LoxBerry-0.1.0.zip herunterladen](https://github.com/square-com-de/plx/releases/download/v0.1.0/PLX-LoxBerry-0.1.0.zip). Unverändert in der Pluginverwaltung hochladen; nicht das allgemeine GitHub-Quellcode-ZIP verwenden.

| Installationsweg | Für wen? | Anleitung |
| --- | --- | --- |
| **Docker / Compose** | Eigener Server oder vorhandene Container-Umgebung, auch Portainer. Kein LoxBerry nötig. | [Installation](INSTALL.de.md) · [Docker-Details](docs/DOCKER.md) |
| **LoxBerry-Plugin** | Vorhandener LoxBerry 4 mit HTTPS. | [Installation](INSTALL.de.md#loxberry-plugin) |

1. **PLX installieren:** Docker oder Plugin wählen. Ein versioniertes Release-Paket verwenden und die Prüfsumme kontrollieren.
2. **Oberfläche öffnen:** Docker nutzt deine eigenen PLX-Zugangsdaten, das Plugin die LoxBerry-Webanmeldung. Es gibt kein PLX-Standardpasswort.
3. **Porsche verbinden:** Anmelden, Fahrzeuge laden, das gewünschte Fahrzeug in der Einrichtung auswählen und speichern.
4. **MQTT auswählen:** Broker einrichten, unter Loxone nur die gewünschten Werte anhaken und speichern. Abonnement: `<Präfix>/#`, standardmäßig `porsche2lox/#`.

Automatischer Abruf und MQTT sind beim ersten Start ausgeschaltet. Der optionale XML-/CSV-Export hilft bei MQTT Gateway und virtuellen UDP-Eingängen; für MQTT allein ist er nicht erforderlich.

**Bereits installiert?** Vor dem Update die eigenen PLX-Daten sichern. Siehe [Installation und Updates](INSTALL.de.md#updates-und-sicherung). Bestehende ausführliche MQTT-Konfigurationen behalten ihr Format, bis du es selbst umstellst.

## Feedback & Kontakt

Du hast PLX ausprobiert? Ich freue mich über dein Feedback – auch darüber, was gut funktioniert!

- **Per E-Mail, ohne GitHub-Konto:** [plx@square-com.de](mailto:plx@square-com.de)
- [Feedback oder Frage stellen](https://github.com/square-com-de/plx/issues/new?template=feedback_question.md)
- [Fehler melden oder Verbesserung vorschlagen](https://github.com/square-com-de/plx/issues/new/choose)

Hilfreich sind PLX-Version, Docker-/LoxBerry-Umgebung, Fahrzeugmodell und eine kurze Beschreibung. Porsche-ID, Fahrzeugnummer, Standort, Passwörter und Tokens vorher aus Screenshots und Logs entfernen. Sicherheitsprobleme vertraulich melden; siehe [Sicherheit](SECURITY.md).

## Release-Stand und Grenzen

**0.1.0 Preview.** Auf getrennten Docker- und LoxBerry-Testinstallationen sind Anmeldung, Fahrzeug-/Statusabruf, HTTPS, DE/EN, mobile Oberfläche und genau zwei numerische Druckwerte am Broker geprüft. Der echte LoxBerry-Neuinstallations-/Updatetest fand einen Fehler beim Datenerhalt. Dieser ist behoben: Einstellungen und Porsche-Sitzung bleiben über den Löschschritt des offiziellen Installers erhalten.

Die vollständige Abnahme über MQTT Gateway bis zum Loxone-Miniserver bleibt offen. Die Tests bestätigen nicht jedes Porsche-Modell, jeden Vertrag oder zukünftige API-Versionen. Siehe [Release-Hinweise](docs/RELEASE-0.1.0.md) und [Testnachweise](docs/TESTS.md).

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
