# PLX installieren

[English](INSTALL.md) · [Projektseite](README.de.md) · [Fehleraufarbeitung und Release-Gate](docs/INSTALLATION-LESSONS.de.md)

**0.1.0 Preview, kein Stable.** [Versioniertes Release](https://github.com/square-com-de/plx/releases/tag/v0.1.0) verwenden. Image und Repository sind öffentlich; kein GitHub-Konto, Registry-Token oder `docker login` nötig. Bestehende Release-Archive behalten ihre ursprüngliche Anleitung; diese Seite korrigiert sie, ohne abgenommene Dateien/Prüfsummen zu ersetzen. [Gate #1](https://github.com/square-com-de/plx/issues/1) verlangt unabhängige Nutzerabnahme vor künftigem Stable/`latest`.

**Bevorzugt: Docker/Compose in einer Linux-VM**, auch auf Proxmox. LoxBerry ist die Alternative. [Ausgeführte Docker-/App-/Recovery-Befehle und Testgrenzen](docs/PROXMOX-CONTAINER.de.md). Die separate Test-VM bestand direkte LAN-HTTPS-/Browser- und Recovery-Prüfung, nachdem Infra eine Lab-Firewallsperre für lokale Dockerzugriffe korrigiert hatte und ein passendes IP-SAN-Zertifikat eingerichtet war. Rein interne Tests bleiben getrennt erkennbar.

## Runtime-Status

| Weg | Preview-Nachweis am 24.10.2026 |
| --- | --- |
| Linux Docker / Compose, AMD64 | Separater Ubuntu-26.04.1-x86_64-Testhost; aktuell Docker Engine 29.8.2, Compose-Plugin 5.6.1. Frühere Abnahmeberichte erfassten keine Runtime-Versionen; dies ist die heutige Inventur, kein rückwirkender Versionsnachweis. |
| LoxBerry-4-Plugin | Separates LoxBerry 4.0.0.15, DietPi/Debian 13.7, Python 3.13.5, PHP 7.4.33; direktes HTTPS, offizielle Neuinstallation/Update, Porsche-Abruf und isoliertes MQTT geprüft. |
| Linux-ARM64-Image | Gebautes/veröffentlichtes Manifest, **keine** protokollierte echte ARM64-Laufzeitabnahme. |
| Portainer | Separater Teststack verwendet; Hostpfade und dasselbe Compose-Projekt/Volume erhalten. Portainer-Version in historischer Abnahme nicht erfasst. |
| Podman / Rootless / Native außerhalb LoxBerry / Docker Desktop | **Für PLX nicht abgenommen.** Kein veröffentlichter geprüfter Installationsablauf. `docker` nicht einfach durch `podman` ersetzen und identische Secret-/Volume-/Healthcheck-Eigenschaften annehmen. Der Fehler eines anderen Projekts ist keine PLX-Diagnose. |

## Linux Docker / Compose: Erstinstallation

Erforderlich: Linux-Docker-Host, `docker compose`, `curl`, GNU `sha256sum`, `tar`, `openssl` und `sudo` für den Dateigruppenwechsel. Porsche-Connect-Konto sowie ausgehendes HTTPS/DNS für Anmeldung/Daten. Nur für die MQTT-Ausgabe wird ein Broker benötigt; PLX installiert keinen Broker.

Die App-Befehle erfordern Docker-Zugriff. Auf der frischen VM liefen sie als root; als normaler Administrator Docker-Befehle mit `sudo` ausführen oder `sudo -i` nutzen. Docker-Gruppenmitgliedschaft nicht stillschweigend vergeben.

Folgendes **einmal, zeilenweise, in einem neuen Verzeichnis ausführen; bei jedem Fehler stoppen**. Bei vorhandener Installation das Secret nicht neu erzeugen. Die Compose-Datei im Release-Paket enthält den festen öffentlichen Image-Digest. Dagegen baut `compose.yaml` im Repository `plx:local`; `compose.registry.yaml` verwendet den Versionstag. Diese drei Wege nicht vermischen.

```sh
set -eu
mkdir plx
cd plx
release=https://github.com/square-com-de/plx/releases/download/v0.1.0
curl -fL "$release/PLX-Docker-0.1.0.tar.gz" -o PLX-Docker-0.1.0.tar.gz
curl -fL "$release/SHA256SUMS" -o SHA256SUMS
sha256sum --ignore-missing -c SHA256SUMS
tar -xzf PLX-Docker-0.1.0.tar.gz
cd PLX-Docker-0.1.0
sha256sum -c SHA256SUMS
umask 077
mkdir -p secrets
test ! -e secrets/plx_password.txt
openssl rand -base64 32 > secrets/plx_password.txt
sudo chgrp 10001 secrets/plx_password.txt
chmod 640 secrets/plx_password.txt
docker compose -p plx config --quiet
docker compose -p plx pull
docker compose -p plx up -d --wait --wait-timeout 90
docker compose -p plx ps
```

Das Secret bleibt im Eigentum des Erstellers, ist für Container-GID **10001** lesbar und nicht weltweit lesbar. Nur `chmod 600` kann den Start unter UID/GID 10001 verhindern. Nicht mit `chmod 777` lösen.

`https://localhost:8443` **auf dem Docker-Host** öffnen. Benutzer `admin`, Passwort aus der erzeugten Secret-Datei, nicht das Porsche-Passwort. Standardzertifikat gilt für localhost/127.0.0.1; lokal vertrauen oder ein passendes vertrauenswürdiges Zertifikat einsetzen. Für LAN-Zugriff die Werte in `.env` **im selben Compose-Verzeichnis** speichern und `docker compose -p plx up -d` ausführen:

```dotenv
PLX_BIND_ADDRESS=192.0.2.10
PLX_PORT=8443
```

Beispieladresse durch die echte LAN-IP ersetzen. `https://<Server-IP>:8443` öffnen; Zertifikat-SAN muss dazu passen. localhost-SAN für den eingebauten Healthcheck erhalten. Siehe [Docker-/TLS-Details](docs/DOCKER.md). `localhost` auf deinem Laptop führt nicht zum entfernten Server.

Für Portainer einen separaten PLX-Stack aus der Release-Compose-Datei anlegen. Das Datei-Secret muss auf dessen Docker-Host vorhanden sein, nicht nur auf dem Desktop. Beim Update **ursprünglichen Stack-/Projektnamen und Datenvolume** beibehalten. Nicht dieselbe Installation zusätzlich als anders benanntes CLI-Projekt starten.

## LoxBerry-Plugin

Voraussetzungen laut Installer: LoxBerry 4, Debian 12+ / Python 3.11+, HTTPS und Internetzugang bei Installation. Vollständiger Plugin-Nachweis nur für die genaue Umgebung oben; keine pauschale Abnahme aller Debian-/LoxBerry-Versionen.

1. [PLX-LoxBerry-0.1.0.zip](https://github.com/square-com-de/plx/releases/download/v0.1.0/PLX-LoxBerry-0.1.0.zip) laden und mit Release-`SHA256SUMS` vergleichen. Nicht das allgemeine GitHub-Quellcode-ZIP oder Docker-Archiv importieren.
2. Unverändertes ZIP über die LoxBerry-Pluginverwaltung installieren.
3. PLX im geschützten LoxBerry-Bereich **über direktes HTTPS** öffnen. LoxBerry-Webanmeldung nutzen, kein Docker-PLX-Passwort.
4. Technische Plugin-ID/Verzeichnis `porsche2lox` beim Update erhalten; PLX ist der Anzeigename.

**Proxy-Grenze in 0.1.0:** Ein HTTPS-Frontend mit internem HTTP zum LoxBerry wird von der veröffentlichten Login-/Speicherprüfung abgewiesen. Direktes LoxBerry-HTTPS oder – sofern vom Proxy unterstützt – verifiziertes HTTPS zum Backend nutzen. Browser–PLX und PLX–Porsche sind getrennte Verbindungen; Porsche-Abfragen laufen weiter über HTTPS. Schutz nicht deaktivieren oder `X-Forwarded-Proto` pauschal vertrauen. Ein Fix mit expliziter Proxy-Vertrauensliste ist nicht im veröffentlichten 0.1.0-ZIP enthalten; siehe [#1](https://github.com/square-com-de/plx/issues/1).

## Erste Einrichtung und Adressen

1. Unter **Porsche-Konto** anmelden, ggf. CAPTCHA bestätigen und Fahrzeuge laden. Fahrzeug in Einrichtung auswählen und **speichern**. Gefunden bedeutet noch nicht ausgewählt.
2. In der Übersicht Status abrufen. Automatischen Abruf separat aktivieren, empfohlen sind 15 Minuten.
3. MQTT mit dem **Broker-Endpunkt** konfigurieren, nicht automatisch mit dem Hostnamen der Webseite. HTTP-/HTTPS-Proxyrouten transportieren ohne eigene MQTT-Konfiguration kein MQTT. `127.0.0.1` in Docker ist PLX selbst. DNS/TCP aus dem PLX-Container prüfen, bevor Kennwörter geändert werden; siehe [Handbuch](docs/MANUAL.de.md#mqtt-und-loxone).
4. Unter Loxone nur gewünschte Werte wählen, speichern und für ein Topic pro Wert **einfaches MQTT** nutzen. Danach MQTT aktivieren. Abonnement `<Präfix>/#`, standardmäßig `porsche2lox/#`. Das Abonnement wählt nicht aus, was PLX sendet.

| Endpunkt | Zweck | Port |
| --- | --- | --- |
| PLX-HTTPS-Webseite | Browseranmeldung, Übersicht | Container 8443, Host-Port einstellbar |
| MQTT-Broker | PLX sendet, Gateway abonniert | Tatsächlicher Broker-Listener; häufig TCP 1883 ohne oder 8883 mit TLS, keine automatische Erkennung |
| MQTT Gateway → Miniserver | Optionale numerische XML-/UDP-Brücke | Beidseitig gleich eingestellter UDP-Port; PLX-Exportvorgabe 11883, nicht Broker-Port |

Keine Fahrzeug-/Weckbefehle. XML/CSV richtet Gateway oder Miniserver nicht automatisch ein. **Absender-IP meint den UDP-Sender (MQTT Gateway)**, nicht automatisch PLX, Broker, LoxBerry oder Miniserver. Leer lassen, solange der Sender nicht sicher bekannt ist.

## Updates, Sicherung und Rückweg

**Docker:** Dasselbe Verzeichnis, Compose-Projekt/Stack, Datenvolume, `.env` und Passwort-Secret erhalten. Die Beispiele verwenden Projekt `plx`; Bestandsinstallationen behalten ihren bestehenden Namen. Ein anderer Projektname kann ein leeres Volume anlegen, das wie Datenverlust aussieht.

Vor dem Update nur PLX stoppen und das komplette `/data`-Volume sowie Compose-Datei, `.env`, Secret und bisherigen Image-Digest privat kalt sichern. `/data` enthält Einstellungen, Porsche-Tokens, Daten/Bilder und TLS-Schlüssel. Echtes Datenvolume per `docker inspect` am PLX-Container bestimmen, nicht aus einem Verzeichnisnamen raten. Bisheriges Image lokal behalten. Sicherungen sind Zugangsdaten: Zugriff beschränken, nicht in GitHub hochladen.

Nur den Image-Pin durch die neue geprüfte Version/den Digest ersetzen (oder die neue geprüfte Release-Compose-Datei übernehmen); andere Einstellungen erhalten. Im selben Verzeichnis:

```sh
docker compose -p plx pull
docker compose -p plx up -d --wait --wait-timeout 90
docker compose -p plx ps
```

`restart` installiert kein neues Image. Kein `down -v`, Volume-Löschen, Secret-Neuerzeugen oder Projektwechsel. Nach Neustart PLX-Webanmeldung erneuern; die Porsche-Sitzung bleibt separat gespeichert.

Rückweg: nur PLX stoppen, Fehlerzustand separat zur Untersuchung erhalten. Alten Compose-Pin/Einstellungen/Secret und **passende Sicherung vor dem Update** in ein separates PLX-Volume zurückspielen, UID/GID 10001 und private Rechte erhalten. Dasselbe Projekt auf dieses Volume verweisen, PLX neu erstellen und HTTPS, gespeicherte Einstellungen, Porsche-Sitzung sowie MQTT-Auswahl prüfen. Ein altes Image muss kein neues Schema lesen können. Kein laufend verwendetes Volume überschreiben. Der neue [Clean-VM-Restore mit passenden Daten](docs/PROXMOX-CONTAINER.de.md#kalte-sicherung-und-passender-rückweg) bestand mit demselben unveränderlichen Image und separatem Zielvolume. Das belegt weder Schema-Downgrade zwischen Versionen noch echte Porsche-Token-Gültigkeit; unabhängige Stable-Kandidatengates bleiben in [#1](https://github.com/square-com-de/plx/issues/1).

**LoxBerry:** Beide Verzeichnisse `/opt/loxberry/config/plugins/porsche2lox/` und `/opt/loxberry/data/plugins/porsche2lox/` sichern, während nur der eigene Dienst gestoppt ist (beim Standardverzeichnis `porsche2lox-porsche2lox.service`). Bei nummerierter Installation tatsächlichen Verzeichnis-/Dienstnamen prüfen. Private Dateien mit Eigentümer/Rechten erhalten; venv ist neu erstellbar, Sockets/Locks gehören nicht in eine portable Sicherung. Vorheriges installierbares ZIP behalten. Neues ZIP **über** das Plugin installieren, nicht vorher deinstallieren. Veröffentlichte preroot/preupgrade-Hooks erhalten privaten Zustand vor dem Löschen durch den Installer und erstellen die venv neu. Für Rollback nur PLX stoppen, altes ZIP mit passender privater Sicherung verwenden und Zustand prüfen; unabhängige Recovery-Abnahme bleibt in [#1](https://github.com/square-com-de/plx/issues/1).

Format-/Auswahländerung kann bekannte alte Retained-Topics einmal entfernen. Einfaches MQTT sendet keine regelmäßigen Lösch-/Heartbeat-Serien. Zur Fehlersuche keinen gemeinsam verwendeten MQTT-Baum löschen.
