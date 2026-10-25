# PLX installieren — Docker zuerst

[English](INSTALL.md) · [README](README.de.md)

Voraussetzung: Linux-Docker-Host mit `docker compose`, `curl` und Docker-Zugriff, z.B. in einer Administratorshell. Bei Proxmox läuft Docker in einer normalen Linux-VM, nicht auf dem Hypervisor. Portainer verwendet dieselbe Compose-Datei. PLX0.1.2 bleibt eine **Preview**.

## Start

IP oder DNS-Namen des Servers wählen, den du im Browser öffnen möchtest. **192.0.2.10** unten durch diese Adresse ersetzen; kein `https://`, Pfad oder Port in `PLX_HOST`. Ein DNS-Name muss auf deinem Gerät zur IPv4-Adresse des Servers auflösen; IPv6 ist im Standardweg nicht abgenommen. Keine Moduswahl beim Erststart: Einfach ist der voll nutzbare Standard.

```sh
set -eu
mkdir plx && cd plx
curl -fLO https://github.com/square-com-de/plx/releases/download/v0.1.2/compose.yaml
printf 'PLX_HOST=192.0.2.10\n' > .env
docker compose up -d --wait --wait-timeout 90
docker compose exec -T plx cat /data/config/web-password.txt
```

**`https://<dein-server>:8443`** öffnen. Benutzer **`admin`**, Passwort aus dem letzten Befehl. Dieser zeigt dein eigenes erzeugtes Passwort bewusst nur in deiner Serverkonsole; privat aufbewahren. Passwort, TLS-Schlüssel/Zertifikat und Einstellungen entstehen einmalig im persistenten benannten Volume. Keine Secret-Datei, chgrp- oder UID-Nacharbeit nötig. Die Erstellungsbefehle nicht über eine vorhandene Installation ausführen.

**Vor Eingabe von Zugangsdaten:** Das erste Zertifikat ist selbstsigniert und passt zu `PLX_HOST`; private IPs erhalten dadurch kein automatisch öffentlich vertrauenswürdiges Zertifikat. Dem eigenen Serverzertifikat ausdrücklich vertrauen oder ein geeignetes eigenes vertrauenswürdiges Zertifikat nutzen. Fingerabdruck: `docker compose exec -T plx openssl x509 -in /data/tls/cert.pem -noout -fingerprint -sha256`. TLS-Prüfung nicht abschalten. Passt das vorhandene Zertifikat nach Adressänderung nicht mehr, stoppt der Start mit verständlicher Meldung; bestehende Dateien bleiben erhalten.

Standardport **8443 ist aus dem LAN erreichbar**. Nur im vertrauenswürdigen LAN betreiben, keine Internet-Portweiterleitung. Ist er belegt, `PLX_PORT=19443` in `.env` ergänzen und diesen Port öffnen. Bewusst nur lokal: `PLX_BIND_ADDRESS=127.0.0.1` mit `PLX_HOST=localhost`; das ist nicht der LAN-Standard. Eine weitere öffentliche URL-Einstellung braucht PLX nicht. Öffentliches Image ohne GitHub-Token/Registry-Login; Prüfsummen und fester Image-Bezug stehen im versionierten Release.

## Portainer

Separaten Stack mit Release-`compose.yaml` anlegen. Erforderliche Umgebungsvariable **PLX_HOST** auf Server-IP/DNS setzen und deployen. In der PLX-Containerkonsole `cat /data/config/web-password.txt` ausführen. Das Datenvolume entsteht automatisch; keine Secret-Hostpfade oder manuellen Dateirechte. Stacknamen beim Update beibehalten.

## Eigene Daten verbinden

1. Zuerst bei PLX anmelden. Danach unter **Porsche-Konto** anmelden, ggf. CAPTCHA bestätigen, Fahrzeuge laden, auswählen und speichern. Das eigene Porsche-Konto bleibt eine notwendige getrennte Zugangseingabe; PLX erzeugt oder importiert es nicht automatisch.
2. Automatischer Abruf und MQTT starten **deaktiviert**. Erst nach Einrichtung einschalten. PLX liest Status und steuert/weckt das Fahrzeug nicht.
3. Für MQTT echten Brokerhost/Port/Zugangsdaten eintragen, nur gewünschte Werte auswählen und speichern. Ein Abonnement `porsche2lox/#` beziehungsweise eigener Präfix genügt. Zwei gewählte Drücke im einfachen Modus senden zwei Werte. Erweiterte Ausgabe später optional, ohne Neuinstallation.

Ein Webproxy-Hostname ist nicht automatisch der MQTT-Broker. Broker-TCP1883/8883 ist nicht der optionale UDP-Port vom Gateway zum Miniserver. Docker-Bridge-Netze transportieren mDNS und die `.local`-Auflösung des Hosts nicht automatisch. Das sind Netzvoraussetzungen, keine versteckten PLX-Modi; siehe [Handbuch](docs/MANUAL.de.md#mqtt-und-loxone).

## Update, Sicherung und Rückweg

Compose-Verzeichnis, Projekt-/Stackname und Datenvolume erhalten. Vor Updates komplettes gestopptes PLX-Volume und aktive Compose-Dateien/`.env` privat sichern; darin liegen Webpasswort, TLS-Schlüssel und ggf. Porsche-Tokens. Sicherungen nicht hochladen. Danach geprüfte Version/Digest wählen und ausführen:

```sh
docker compose pull
docker compose up -d --wait --wait-timeout 90
docker compose ps
```

`restart` aktualisiert kein Image. Kein `down -v` für Datenerhalt. Nach Neustart erneute PLX-Webanmeldung normal; Daten/Passwort bleiben erhalten. Für Recovery PLX stoppen und passende private Sicherung in ein separates eigenes Volume zurückspielen; aktive Compose-Dateiauswahl erhalten. [Geprüfte Sicherungs-/Restore-Mechanik](docs/PROXMOX-CONTAINER.de.md#kalte-sicherung-und-passender-rückweg) ist Betriebsreferenz, keine Erststartpflicht. Alter Code muss keine zukünftigen Datenformate lesen können. Bestehende ausdrücklich konfigurierte `PLX_PASSWORD_FILE`-Secrets bleiben unterstützt; der obige Passwortbefehl gilt für den neuen Standard.

## Alternativen und Grenzen

**LoxBerry als Alternative:** Dediziertes `PLX-LoxBerry-0.1.2.zip` über Pluginverwaltung von LoxBerry4 mit direktem HTTPS und bestehender Webanmeldung importieren, nicht das allgemeine Quellcode-ZIP. Technische ID `porsche2lox` beim Update erhalten. Für LoxBerry-TLS-Terminierung mit internem HTTP müssen die vertrauenswürdigen Proxy-Adressen unten ausdrücklich konfiguriert werden; [Gate #1](https://github.com/square-com-de/plx/issues/1) bleibt ausdrücklich bestehen.

Docker Linux/Proxmox bevorzugt. Frühere Clean-VM-Nachweise bleiben vom neuen Erststart getrennt. Podman/Rootless, Native außerhalb LoxBerry und echter ARM64-Betrieb sind durch verfügbare Manifeste nicht automatisch abgenommen. Die historische Lab-Firewallstörung ist **kein** Endnutzer-Installationsschritt. Zertifikatsvertrauen, Gerätekonto, Brokerzugang oder Multicast-Erreichbarkeit werden nicht magisch zugesagt. [Handbuch](docs/MANUAL.de.md) · [Release-Hinweise](docs/RELEASE-0.1.2.md).

[Historische Abnahme des veröffentlichten 0.1.1-Quickstarts](docs/QUICKSTART-0.1.1.md): frisches Volume, strenger LAN-/Browserlogin, Neustart/Neuerstellung und passende kalte Wiederherstellung bestanden. Die Testgrenzen bleiben dort ausdrücklich genannt.

### LoxBerry hinter HTTPS-Proxy

Ein HTTPS-Proxy mit internem HTTP benötigt eine ausdrückliche Liste vertrauenswürdiger unmittelbarer Proxy-Adressen. [Konfiguration und Sicherheitsregeln](docs/REVERSE-PROXY.md). Der Fix gehört ab0.1.2 zum Plugin; das öffentliche0.1.1 bleibt unverändert; direkte HTTPS-Verbindungen bleiben unterstützt.
