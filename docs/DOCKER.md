# PLX als eigenständiger Container

[English installation](../INSTALL.md) · [Deutsche Installation](../INSTALL.de.md) · [Fehleraufarbeitung](INSTALLATION-LESSONS.de.md)

PLX verwendet denselben Status-/MQTT-Kern und dieselbe Weboberfläche wie das LoxBerry-Plugin. Der Container hat einen eigenen HTTPS-Server und eine eigene PLX-Webanmeldung. LoxBerry/PHP/systemd werden dafür nicht benötigt; es gibt keinen nativen Nicht-LoxBerry-Installer mit Abnahmenachweis.

## Welcher Startweg?

| Datei / Paket | Verhalten |
| --- | --- |
| Release `PLX-Docker-0.1.0.tar.gz` | Empfohlener Preview-Pfad: enthaltene `compose.yaml` pinnt `ghcr.io/square-com-de/plx@sha256:5b7a6a7244c9c0e0eb59b79aa021fddb73e2326846d00aa8a64408dca9f0cf5f`. Image wird separat öffentlich geladen, keine Registry-Anmeldung. |
| Repository `compose.yaml` | Quellcode-Build, `plx:local`; nicht dieselbe Datei wie im Release-Paket. Für Entwicklung, nicht als fertig getesteter Release-Befehl ausgeben. |
| Repository `compose.registry.yaml` | Öffentliches Versionsimage `ghcr.io/square-com-de/plx:0.1.0`; für reproduzierbare Installation den Release-Digest bevorzugen. |

Kopierbare Linux-Erstinstallation mit aktiven Secret-Rechten, festem Compose-Projektnamen und Prüfsummen: [Installation](../INSTALL.de.md#linux-docker--compose-erstinstallation). Bei Bestandsinstallation nie versehentlich Projekt/Volume wechseln oder das vorhandene Secret neu erzeugen. Für Update/Persistenz/Recovery gelten die Schritte unter [Updates und Rückweg](../INSTALL.de.md#updates-sicherung-und-rückweg).

**Runtime-Grenzen:** Linux AMD64 und separates LoxBerry sind geprüft. ARM64-Image gebaut/veröffentlicht, echter ARM64-Betrieb nicht abgenommen. Für Podman, Rootless-Docker und Docker Desktop liegt kein PLX-Installations-/Lebenszyklusnachweis vor. OCI-Kompatibilität ist keine Abnahme. [Genaue Testumgebungen](../INSTALL.de.md#runtime-status). `edge` ist Entwicklung, keine Stable-Empfehlung; diese Preview setzt kein `latest`.

## HTTPS und Anmeldung

Nur HTTPS, kein HTTP-Login. Standardbindung: `127.0.0.1:8443`; auf einem entfernten Server führt `localhost` im Laptopbrowser zum Laptop. LAN-Bindung über dauerhafte `.env` mit `PLX_BIND_ADDRESS`/`PLX_PORT`, passenden Firewallregeln und Zertifikat einrichten.

Beim ersten Start erzeugt PLX ein eigenes Zertifikat für localhost/127.0.0.1 und speichert es in `/data/tls/`. Für LAN-Namen/IPs ein eigenes passendes Zertifikat lokal vertrauen beziehungsweise ein vertrauenswürdiges PEM-Zertifikat und dessen unverschlüsselten privaten Schlüssel als `/data/tls/cert.pem` und `/data/tls/key.pem` bereitstellen. Nur UID/GID 10001 darf den Schlüssel lesen. Danach nur PLX neu starten. Der interne Healthcheck verbindet sich verifiziert mit localhost: Eigene Zertifikate benötigen auch localhost als SAN, sofern der Healthcheck nicht gesondert angepasst und geprüft wird. Zertifikatsprüfung nicht als Fehlerbehebung abschalten.

Der Docker-Server akzeptiert weitergereichte Header nicht als HTTPS-Nachweis. Ein Reverse Proxy muss den Container per verifiziertem **HTTPS** erreichen; nicht mit der noch unvollständigen TLS-Terminierungsunterstützung des LoxBerry-PHP-Frontends verwechseln. Die separate Verbindung PLX → Porsche verwendet HTTPS.

Webbenutzer standardmäßig `admin`, eigenes Passwort mindestens 16 Zeichen aus dem Datei-Secret. Kein Standardpasswort und kein Registry-Token für die öffentliche Image-Version. Secret muss UID/GID 10001 lesen können: unter dem dokumentierten Linux-Docker-Pfad gezielt GID 10001 / Modus 0640, nicht weltweit lesbar. Bei Portainer gelten Pfade auf dem Docker-Host.

Websitzungen sind acht Stunden gültig, HttpOnly/Secure/SameSite=Strict und CSRF-geschützt. Fünf Loginversuche je Quelladresse/Minute; beim Proxy teilen sich Nutzer dessen Quelladresse. „PLX abmelden“ beendet nur die Websitzung. „Porsche abmelden“ beendet nur die eigene Porsche-Sitzung. Nach Containerneustart erneut bei PLX anmelden; gespeicherte Porsche-Tokens bleiben unabhängig erhalten.

## Daten und MQTT

Das Datenvolume enthält Einstellungen, Porsche-Tokens, Status, Modellbilder und TLS-Schlüssel. Der Prozess läuft unter UID/GID 10001 mit schreibgeschütztem Containerdateisystem und ohne Linux-Capabilities. Keine laufenden Porsche-/Taycan-Verzeichnisse mounten oder deren Sitzung importieren. Private Kalt-Sicherung vor Updates, bisheriges Image und Compose-Konfiguration für Rückweg erhalten. Kein `down -v` für Datenerhalt. Der [Clean-VM-Restore mit passender Datensicherung](PROXMOX-CONTAINER.de.md#kalte-sicherung-und-passender-rückweg) ist mit demselben Image und separatem Volume geprüft. Das ersetzt keine unabhängige Stable-Kandidaten- oder Versionsmigrationsabnahme; reine Neustartpersistenz war kein Restore-Nachweis.

MQTT und automatischer Abruf starten deaktiviert. Broker-Adresse/TCP-Port/TLS sind unabhängig von der Webadresse. Ein auf den Webproxy auflösender Hostname kann HTTPS bedienen und MQTT trotzdem ablehnen. DNS/TCP **aus dem Container** prüfen: [Handbuch](MANUAL.de.md#mqtt-und-loxone). `127.0.0.1` meint den PLX-Container.

Einfaches MQTT ist Neuinstallationsstandard: ein ausgewählter Druckwert = ein numerisches Topic in bar; fehlend `null`, keine zusätzlichen Heartbeat-/Diagnosethemen. Der letzte gemeldete Wert kann alt sein; Retained-Werte überleben Verbindungsabbrüche. Für frischeabhängige Logik das ausführliche Format samt Freigaben tatsächlich auswerten. Nur ein Abonnement `porsche2lox/#` (beziehungsweise eigener Präfix). Datenauswahl bestimmt den Versand, nicht das Abonnement. Beim bewussten Formatwechsel alte bekannte Topics einmalig bereinigen; keine pauschale Löschung fremder Topics.

[Offene unabhängige Abnahme / Gate #1](https://github.com/square-com-de/plx/issues/1). Dokumentation erweitert keine Runtime-Freigabe und veröffentlicht kein neues Image.
