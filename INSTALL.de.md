# PLX installieren

[English](INSTALL.md) · [Projektseite](README.de.md)

**0.1.0 Preview:** `PLX-Docker-0.1.0.tar.gz`, `PLX-LoxBerry-0.1.0.zip` und `SHA256SUMS` aus dem [versionierten Release](https://github.com/square-com-de/plx/releases/tag/v0.1.0) laden. Das Docker-Image ist öffentlich und ohne GitHub-Konto oder Registry-Token abrufbar. Dies ist eine Preview, kein Stable-Release.

## Docker / Compose

Vorausgesetzt sind Docker Engine mit Compose v2 auf AMD64 oder ARM64, ein kompatibles Porsche-Connect-Konto und Internetzugang. Ein MQTT-Broker ist nur für MQTT nötig. Mac oder Windows können zur Bedienung des Servers verwendet werden.

1. Docker-Paket in ein eigenes Verzeichnis entpacken. Die enthaltene `compose.yaml` verweist auf den geprüften Image-Digest. Vor dem Entpacken die Archiv-Prüfsumme kontrollieren; danach die Dateien anhand von `SHA256SUMS` prüfen.
2. Eigenes PLX-Passwort erzeugen:

   ```sh
   mkdir -p secrets
   openssl rand -base64 32 > secrets/plx_password.txt
   chmod 600 secrets/plx_password.txt
   # Linux: gezielte Leserechte für Containergruppe 10001:
   # sudo chgrp 10001 secrets/plx_password.txt
   # chmod 640 secrets/plx_password.txt
   ```

3. Für das öffentliche Release-Image ist kein Registry-Login nötig.
4. `docker compose pull` und danach `docker compose up -d` ausführen.
5. `https://localhost:8443` öffnen. Benutzername: `admin`; Passwort: Inhalt der eigenen Secret-Datei. Das erzeugte Zertifikat muss lokal vertraut oder durch ein geeignetes eigenes Zertifikat ersetzt werden. Siehe [HTTPS und SAN-Anforderungen](docs/DOCKER.md#https-und-anmeldung).

Standardmäßig ist der Port nur lokal erreichbar. Für LAN-Zugriff `PLX_BIND_ADDRESS` auf die LAN-Adresse des Servers setzen. `PLX_PORT` ändert den Host-Port, `PLX_USERNAME` den Benutzernamen. Kein produktives Porsche-/Taycan-Verzeichnis einbinden.

In Portainer die Compose-Datei als eigenen Stack verwenden. Das Datei-Secret muss in dieser Portainer-Umgebung verfügbar sein; Dateipfade beziehen sich auf den Containerhost. Beim Update das Datenvolume erhalten.

**Alternativ aus Quellcode bauen:** Im Repository-Verzeichnis dasselbe Secret anlegen und mit dessen Build-Compose-Datei `docker compose up -d --build` ausführen. Das Quellcode-Repository ist öffentlich.

## LoxBerry-Plugin

Erforderlich sind LoxBerry 4, Debian 12 oder neuer, Python 3.11+, HTTPS und Internetzugang während der Installation.

1. `PLX-LoxBerry-0.1.0.zip` herunterladen und Prüfsumme kontrollieren. Nicht das allgemeine GitHub-Quellcode-ZIP als Plugin installieren.
2. ZIP über die LoxBerry-Pluginverwaltung installieren.
3. PLX in der geschützten LoxBerry-Oberfläche **über HTTPS** öffnen. Es gelten deine LoxBerry-Webzugangsdaten, nicht das Docker-PLX-Passwort.
4. Beim Update die technische Plugin-ID `porsche2lox` beibehalten. Der Anzeigename ist PLX; die technischen Verzeichnisse bleiben kompatibel.

## Erste Einrichtung

1. Unter **Porsche-Konto** mit der Porsche-ID anmelden und bei Bedarf CAPTCHA bestätigen.
2. Fahrzeuge laden, zur Einrichtung wechseln, Fahrzeug auswählen und speichern.
3. In der Übersicht **Status abrufen** wählen. Automatischen Abruf bei Bedarf separat aktivieren; empfohlen sind 15 Minuten.
4. MQTT-Broker mit seiner Netzwerkadresse und Zugangsdaten eintragen. In Docker bezeichnet `127.0.0.1` den Container selbst.
5. Unter **Loxone** nur die gewünschten Werte auswählen und speichern. Anschließend MQTT-Ausgabe in der Einrichtung aktivieren. Abonnement: `<Präfix>/#`, standardmäßig `porsche2lox/#`.

PLX sendet keine Fahrzeugbefehle und keine Weckanforderungen. Einfaches/ausführliches MQTT und Datenalter erklärt das [Handbuch](docs/MANUAL.de.md).

## Updates und Sicherung

Vor Updates PLX-Daten und Zugangsdaten sichern. Die Sicherung enthält private Tokens und TLS-Schlüssel.

- **Docker:** Datenvolume und Web-Passwort-Secret erhalten. Auf den geprüften Image-Digest beziehungsweise die Version wechseln, Image laden und nur den PLX-Dienst neu erstellen. Für Datenerhalt kein `docker compose down -v` ausführen. Nach Neustart ist eine neue PLX-Webanmeldung nötig; die Porsche-Sitzung bleibt erhalten.
- **LoxBerry:** Neueres Plugin-ZIP über das vorhandene Plugin installieren. Der Vorbereitungshook stoppt nur den eigenen Dienst; der preupgrade-Hook übernimmt die privaten Daten vor dem Löschen alter Verzeichnisse. Die neue Installation übernimmt sie und erstellt ihre Python-Umgebung neu. Für Datenerhalt nicht vorher deinstallieren.
- **Rückweg:** Vorheriges geprüftes Image/Plugin und eigene Sicherung verwenden. Nicht voraussetzen, dass ältere Versionen zukünftige Datenformate lesen können. Dateirechte und Eigentümer aus der [technischen Referenz](docs/TECHNICAL.de.md) beachten.

Beim Ändern der MQTT-Auswahl können vorher ausgewählte Topics einmal gelöscht werden. Einfaches MQTT sendet keine regelmäßigen Löschserien und keine zusätzlichen Heartbeat-Themen.
