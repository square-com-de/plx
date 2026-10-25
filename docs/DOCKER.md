# Docker-Betrieb

[Kurzer Standardstart](../INSTALL.de.md) · [English](../INSTALL.md)

PLX0.1.2 benötigt im neuen Compose-Standard nur `PLX_HOST` (Server-IP/DNS). Der Hostport8443 ist aus dem LAN erreichbar. Datenvolume, privates Webpasswort und passendes selbstsigniertes Zertifikat werden automatisch erstellt; keine externe Secret-Datei oder UID-Nacharbeit. Einfaches MQTT bleibt Standard, ohne Modusfrage beim Start.

Browser müssen dem eigenen selbstsignierten Zertifikat ausdrücklich vertrauen; private IPs erhalten kein öffentliches Zertifikat automatisch. Eigene passende PEM-Dateien können unter `/data/tls/cert.pem` und `/data/tls/key.pem` liegen. Vorhandene Dateien werden nicht bei Adressfehlern überschrieben. Falscher Host, unvollständiges oder unpassendes Zertifikat führen früh zu einer verständlichen Startmeldung. Healthcheck verbindet lokal, prüft aber die konfigurierte Zertifikatsidentität. Kein TLS-/Origin-/CSRF-Bypass.

`PLX_PORT` ändert den Hostport, `PLX_USERNAME` den Webbenutzer. `PLX_BIND_ADDRESS=127.0.0.1` ist die bewusste lokale Alternative. Kein zusätzlicher PUBLIC_URL-Schalter. Portainer nutzt dieselbe Compose-Datei und legt dasselbe benannte Volume an. Projekt/Stacknamen beim Aktualisieren erhalten.

Das gesamte Volume enthält jetzt auch `/data/config/web-password.txt`; private Sicherung vor Updates. Nach Neustart neu bei PLX anmelden, gespeicherte Daten/Passwort bleiben. Für bestehende ausdrücklich eingebundene Secrets gilt weiterhin `PLX_PASSWORD_FILE`; diese fortgeschrittene Kompatibilität ist keine Erststartpflicht.

[Historische geprüfte Backup-/Restore-Mechanik](PROXMOX-CONTAINER.de.md#kalte-sicherung-und-passender-rückweg) erklärt private Kalt-Sicherung und separate Restore-Volumes. Sie ersetzt keine unabhängige Versionsmigrationsabnahme. Kein `down -v`, globales Prune oder Wechsel des Projektnamens für Updates.

MQTT-Host muss zum tatsächlichen Broker führen, nicht bloß zum Webproxy. Docker-Bridge bietet keine automatische mDNS-/`.local`-Weiterleitung. Lab-spezifische Firewallregeln werden nicht zur normalen Installationspflicht. Podman/Rootless und echte ARM64-Laufzeit bleiben gesondert nicht abgenommen; keine physischen Miniserver- oder Produktionsfreigaben aus Image-Manifeste ableiten.
