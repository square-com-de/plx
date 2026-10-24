# PLX ohne LoxBerry

Dieselbe Weboberfläche und derselbe Status-/MQTT-Kern, mit eigenem HTTPS-Server und PLX-Anmeldung. Kein PHP, LoxBerry, systemd oder Zugriff auf eine bestehende Taycan-Installation erforderlich. Statusabruf und MQTT sind bei Erststart ausgeschaltet. Fahrzeugbefehle werden weiterhin nicht unterstützt.

## Start aus dem Repository

Docker Engine mit Compose v2 vorausgesetzt. Im Repository-Verzeichnis:

```sh
mkdir -p secrets
openssl rand -base64 32 > secrets/plx_password.txt
chmod 600 secrets/plx_password.txt
# Linux: dem Container gezielt Leserechte geben
# sudo chgrp 10001 secrets/plx_password.txt && chmod 640 secrets/plx_password.txt
docker compose up -d --build
```

Aufrufen: **https://localhost:8443**. Benutzername: **admin**, Passwort: Inhalt der selbst erzeugten Datei `secrets/plx_password.txt`. Das ist das PLX-Passwort; die Porsche-ID wird erst anschließend unter „Porsche-Konto“ eingegeben. Es gibt kein Standardpasswort. Mindestens 16 Zeichen erforderlich. Das Passwort wird als Compose-Secret eingebunden, nicht in das Image kopiert.

Linux-Hinweis: Datei-Secrets sind Bind-Mounts; der Containerbenutzer UID/GID 10001 muss die Datei lesen können. Bei fehlender Leseberechtigung gezielt GID 10001 und Modus 0640 setzen (`sudo chgrp 10001 secrets/plx_password.txt; chmod 640 secrets/plx_password.txt`). Keine weltweit lesbaren Kennwortdateien verwenden.

Standardmäßig ist der Port nur am lokalen Rechner erreichbar. Für einen eigenen LAN-Server:

```sh
PLX_BIND_ADDRESS=0.0.0.0 docker compose up -d --build
```

Dann `https://<Server-IP>:8443` öffnen. Port und Benutzername können mit `PLX_PORT` beziehungsweise `PLX_USERNAME` geändert werden. Der MQTT-Broker muss aus dem Container erreichbar sein: seine LAN-Adresse oder einen Compose-Servicenamen verwenden; `127.0.0.1` bezeichnet den Container selbst. MQTT wird bewusst nicht automatisch aktiviert.

## MQTT-Auswahl

Bei einer neuen Installation gilt die einfache Ausgabe: pro gewähltem Parameter ein Topic, Reifendruck direkt in bar. Es gibt dabei keine zusätzlichen Diagnose-/Heartbeat-Themen. Fehlende Werte werden als `null` gesendet. Der einfache Modus sendet zuletzt gemeldete Werte; Messalter und Verbindungszustand bleiben in PLX sichtbar. Vorhandene Installationen behalten ohne bewusste Formatumstellung ihre ausführliche Ausgabe; unter Loxone → Erweiterte Ausgabeoptionen lässt sich das Format auswählen. Die UI-Anzeige der Fahrzeugdaten bleibt vollständig.

## HTTPS und Anmeldung

Beim ersten Start erzeugt PLX ein eigenes Zertifikat und speichert es dauerhaft. Der Browser meldet das selbst signierte Zertifikat; im eigenen LAN bewusst bestätigen oder ein eigenes vertrauenswürdiges Zertifikat einsetzen. Generierte Zertifikate gelten für localhost/127.0.0.1; für LAN-Namen/IPs eigene passende Zertifikate verwenden. Unter `/data/tls/cert.pem` und `/data/tls/key.pem` können eigene PEM-Dateien hinterlegt werden, lesbar nur für UID 10001; anschließend Container neu starten. Der private Schlüssel darf nicht passwortgeschützt sein. Der interne Healthcheck verwendet dieselbe CA und localhost, daher muss auch ein eigenes Zertifikat localhost als SAN enthalten oder der Healthcheck passend angepasst werden.

Es gibt ausschließlich HTTPS, keine unsichere HTTP-Anmeldung. Weiterleitungsheader werden nicht als Nachweis für HTTPS akzeptiert. Ein Reverse Proxy kann die HTTPS-Verbindung zum Container nutzen. Websitzungen sind acht Stunden gültig, HttpOnly/Secure/SameSite=Strict und gegen CSRF geschützt. Fünf Anmeldeversuche pro Quelladresse und Minute; bei Reverse-Proxy-Betrieb gilt dessen gemeinsame Quelladresse. „PLX abmelden“ beendet ausschließlich die Websitzung. „Porsche abmelden“ im Konto beendet ausschließlich die eigene Porsche-Sitzung. Nach Containerneustart muss man sich bei PLX neu anmelden; die gespeicherte Porsche-Sitzung bleibt bestehen.

## Daten, Updates und Sicherung

Das Volume `plx_data` enthält eigene Einstellungen, Porsche-Token, Fahrzeugdaten, Modellbilder und TLS-Dateien. Keine Produktionsverzeichnisse einhängen und keine vorhandene Porsche-Sitzung importieren. Der Prozess läuft als UID/GID 10001, mit schreibgeschütztem Containerdateisystem, ohne Linux-Capabilities. Das Volume vor Updates sichern; es enthält private Daten und Zugangstoken.

```sh
docker compose logs --tail=50 plx
docker compose ps
docker compose down
docker compose up -d --build
```

`down` behält das Volume. `down -v` löscht sämtliche PLX-Daten. Das PLX-Passwort kann durch Ersetzen der Secret-Datei und anschließendes `docker compose up -d --force-recreate` geändert werden. Einstellungen und Porsche-Token sind davon unabhängig.

Ein vorgebautes Image ist unter `ghcr.io/square-com-de/plx:edge` für Linux AMD64 und ARM64 veröffentlicht. Alternativ bleibt der lokale Build (`plx:local`) möglich. Die LoxBerry-ZIP bleibt ein eigener Installationsweg; Docker-Dateien werden darin nicht mitgeliefert.

## Fertiges GitHub-Image verwenden

Erste Veröffentlichung erfolgreich geprüft: [GitHub Actions #1](https://github.com/square-com-de/plx/actions), Quellstand `2636646506dcdfa5bd42bc8c9f32c55c6bfc8626`. Unterstützt werden `linux/amd64` und `linux/arm64`. Tags: `ghcr.io/square-com-de/plx:edge` und `ghcr.io/square-com-de/plx:sha-542f627fb3ccbc58f9335c6fcea8e78e8af80cb2`. `edge` ist ein Entwicklungsstand, kein stabiler Release.

Das Release-Image `ghcr.io/square-com-de/plx:0.1.0` ist öffentlich für AMD64/ARM64 verfügbar. Kein GitHub-Konto und kein Registry-Token erforderlich. Das Docker-Releasepaket enthält eine Compose-Datei mit festem Image-Digest. Secret-Datei wie oben vorbereiten und starten:

```sh
docker compose -f compose.registry.yaml pull
docker compose -f compose.registry.yaml up -d
```

Beim Login das GitHub-Paket-Token als Passwort verwenden, nicht das Porsche-Passwort. Der Container bekommt dieses Registry-Token nicht. Auch diese Variante bindet standardmäßig nur localhost; für LAN-Zugriff `PLX_BIND_ADDRESS=0.0.0.0` vor dem Compose-Aufruf setzen.

Der Workflow „PLX Docker“ testet bei relevanten Änderungen auf `main` und veröffentlicht erst nach bestandenen Linux-Tests und Container-Smoke-Test beide Architekturen sowie einen commitbezogenen Tag. Für einen festgelegten Stand den SHA-Tag statt `edge` in der Compose-Datei eintragen. Beide Compose-Dateien verwenden dieselbe Volume- und Secret-Struktur; nicht gleichzeitig im selben Projekt starten. Updates über `pull` und `up -d`, Stoppen über `down` mit derselben `-f`-Datei.
