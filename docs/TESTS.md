# Testnachweis – PLX 0.1.0

## Erfolgreich ausgeführt

- **48 automatisierte Tests** in einem isolierten Debian-12-Container (ARM64), Python 3.11, PHP 8.2, Mosquitto.
- Installation sämtlicher Runtime-Abhängigkeiten anhand der festgelegten Versionen und SHA-256-Hashes im Container.
- Datenprüfung: fehlender/ungültiger Akkustand, echter 0-%-Wert, deaktivierte Messwerte, falsche VIN, unbekannte/alte/zukünftige Messzeit, Zeitzonen, explizites Ladeziel statt Profil-Mindestladung.
- OAuth gegen lokale HTTP-Mocks: realer Bibliotheksablauf mit Authorization Code, S256-PKCE, CAPTCHA-Unterbrechung und fortgesetzten Cookies; keine Anfrage an Porsche.
- Erneuertes Token bleibt nach folgendem API-Fehler gespeichert; geschützte Dateirechte; Freigabe/Schließen des Anmeldekontexts nach Abschluss und Ablauf.
- Strukturierte Authentifizierungsfehler, Rate-Limit-Pause, manuelle Abfragebegrenzung, MQTT-Fehler unabhängig von Porsche-Status, Abmeldung und ausschließlich eigene Sitzungsdatei.
- Echte PHP-Anfragen an einen lokalen Test-Webserver mit kleinen SDK-Stubs: nicht angemeldeter Zugriff abgewiesen, CSRF-Prüfung, HTTP-Zugangsdaten abgewiesen, HTTPS-Konfigurationspfad, Antwort ohne Passwort.
- Echter Unix-Socket zum laufenden Python-Dienst; Statusabruf und MQTT bleiben bei Erststart deaktiviert. Geregeltes Dienstende geprüft.
- Echter Mosquitto-Broker: QoS-1-Veröffentlichung, retained-Abruf und retained-Löschung.
- Root-Hook mit nummeriertem Pluginordner im Container: eigene systemd-Unit erzeugt, Konfiguration/Sitzung erhalten, ausschließlich eigene Unit deinstalliert. `systemctl` wurde hierbei durch eine Testaufzeichnung ersetzt; der Container betreibt kein vollständiges systemd/LoxBerry.
- PHP-, JavaScript- und Shell-Syntax geprüft.
- Browserprüfung in einem separaten Chrome-Prozess mit ausschließlich simulierten Daten: Desktop 1440 px und Handy 390 px, kein horizontaler Seitenüberlauf, keine JavaScript-Fehler, ungespeicherte Formulare bleiben bei Hintergrundaktualisierungen erhalten, Speichern und CAPTCHA-Anzeige, Passwortfeld nach Abschicken geleert.
- Screenshots der Übersicht, Einrichtung und Anmeldung visuell geprüft. Sie zeigen **Demodaten**, keinen Live-Fahrzeugstatus.
- Das bestehende lokale Sicherungsrepository `taycan-loxone-backup` ist unverändert. Kein Zugriff auf produktive VM, produktiven Broker oder Porsche-Konto während der Entwicklung.

## Reproduzieren

```sh
podman build -f tools/Dockerfile.test -t localhost/porsche2lox-test:0.1 .
podman run --rm -v "$PWD:/plugin:ro" localhost/porsche2lox-test:0.1 /testvenv/bin/python -m pytest -q -p no:cacheprovider tests
```

Auf einem Rechner ohne PHP/Mosquitto werden die drei Linux-Integrationstests ausgelassen; die Root-Hook-Prüfung erfordert den isolierten Container. Browserpfade in tools/preview.cjs sind auf die Entwicklungsumgebung eingestellt.

## Noch ausstehende Abnahme

1. Eigene Anmeldung mit dem echten Porsche-Konto, ggf. CAPTCHA und automatische Token-Erneuerung bestätigen. Abweichende MFA-/Loginvarianten sind noch nicht nachgewiesen.
2. Reale Antwortformate insbesondere für Batteriemesszeit und Ladeziel anhand anonymisierter Daten prüfen. Solange der Messzeitpunkt nicht bekannt ist, bleibt `data_valid=0`.
3. MQTT Gateway und Loxone-Programmierung mit Freigaben und Heartbeat-Watchdog abnehmen; Broker- und VM-Ausfall einschließen.
4. Neustart und vollständige Deinstallation des Plugins auf der echten Test-VM gesondert abnehmen. Die Grundinstallation der Test-LoxBerry wurde neu gestartet; das Plugin wurde bislang installiert und aktualisiert. Deinstallation war bisher nur im isolierten Linux-Test enthalten.

Das Paket ist deshalb eine lokal geprüfte **Testversion**, noch keine produktiv abgenommene Veröffentlichung.

## Ergänzung: echte LoxBerry-Test-VM am 22.10.2026

Die Infrastrukturabnahme wurde auf einem eigenen Proxmox-Klon durchgeführt: DietPi/Debian 13, x86_64, LoxBerry 4.0.0.15, Python 3.13.5, PHP 7.4.33 und Apache. Die produktive LoxBerry/Taycan-Installation wurde nicht angesprochen oder verändert.

Erfolgreich:

- Plugin-ZIP über den echten LoxBerry-Paketinstaller installiert und wiederholt aktualisiert. Der finale Installerlauf enthielt keine ERROR/CRITICAL-Meldung. Dienst und Konfiguration blieben funktionsfähig.
- Geschützte Oberfläche über echtes HTTPS und das LoxBerry-PHP-SDK aufgerufen. Testzertifikat im automatischen Test anhand der über verifiziertes SSH abgerufenen Zertifikatsdatei geprüft; keine abgeschaltete TLS-Prüfung.
- Nicht angemeldeter Zugriff: HTTP 401. Anfrage ohne CSRF-Token: HTTP 403. CSS und JavaScript: HTTP 200.
- Einstellungen über PHP → privaten Unix-Socket → Python-Dienst gespeichert. Passwort nicht in der Statusantwort. Einstellungen und Socket mit Modus 600 und Eigentümer loxberry.
- Statusabruf und MQTT bei Erststart deaktiviert; keine Porsche-Sitzung übernommen.
- Übersicht und Anmeldeformular im Browser mit der echten LoxBerry-Seitenumgebung geprüft. Für den Darstellungstest wurde eine lokale Nur-Lese-Verbindung mit serverseitiger Testauthentifizierung verwendet. Keine Porsche-Zugangsdaten eingegeben.
- Mobile Einbindung korrigiert; nach Abschluss der LoxBerry-Seitenleistenanimation kein horizontaler Überlauf bei 390 px. Historische Bilder mit altem Projektlogo wurden aus dem aktuellen Dateibaum entfernt. Neue Branding-Vorschauen sind simulierte UI-Aufnahmen und keine Wiederholung dieser historischen Systemabnahme.
- Klassischen index.cgi-Einstieg ergänzt; dieser leitet ausschließlich zur geschützten index.php weiter.

Die Grundinstallation brauchte zwei Korrekturen ausschließlich im Testklon: DietPis ausstehende Ersteinrichtung abschließen und die vom aktuellen offiziellen Installer erwartete shellinabox.service aus dem offiziellen LoxBerry-Master ergänzen, da sie im ausgewählten Release fehlte. Für den CLI-Paketinstaller muss das Arbeitsverzeichnis für loxberry zugänglich sein; /root erzeugt eine Find-/Dateirechtewarnung.

## Reale Testsitzung am 22.10.2026

Nach der Benutzeranmeldung lieferte die Fahrzeugliste ein Fahrzeug und die Statusabfrage ein JSON-Objekt. Für den Erneuerungstest wurde ausschließlich die Ablaufzeit der eigenen Testsitzung in die Vergangenheit gesetzt, während der Testdienst angehalten war. Der nächste Fahrzeugabruf erneuerte sowohl Access- als auch Refresh-Token, speicherte eine zukünftige Ablaufzeit mit Dateimodus 0600 und lieferte wieder ein Fahrzeug. Anschließend wurde der Testdienst gestartet und die Fahrzeugliste dort erfolgreich erneut geladen. Keine Tokens oder Fahrzeugkennungen wurden protokolliert. Kein Zugriff auf die produktive Taycan-App.

Die Fahrzeugauswahl wird jetzt auch bei ungespeicherten Einstellungen aktualisiert; vorhandene Eingaben bleiben dabei erhalten.

**Weiter offen:** fachliche Prüfung aller Messwerte, Fahrzeugauswahl durch den Benutzer sowie Ende-zu-Ende-Abnahme mit einem Miniserver. Der erzwungene Ablauf prüft den Erneuerungspfad; ein längerer Dauerbetrieb bleibt separat zu beobachten.

## Web-Aktionen und kompakte Oberfläche

Realer Browser-Klick auf „Fahrzeuge laden“ reproduzierte `Ungültige Anfrage`: PHP serialisierte die leeren Objektparameter als Array. Der Endpunkt erhält jetzt den Objekttyp. Nach Installation auf der Test-VM lieferte derselbe Browser-Klick erfolgreich „Fahrzeugliste aktualisiert“ und ein Fahrzeug in der Auswahl. Die 30-Sekunden-Sperre wurde ebenfalls geprüft; ihre Fehlermeldung bleibt über folgende Statusabfragen hinweg sichtbar. PHP-Syntax gültig, keine JavaScript-Fehler, mobile Ansicht bei 390 px ohne horizontalen Überlauf. Seitenkopf und Formulare verkleinert, Shell-Abstände entfernt, Statusmeldung unter die Reiter verschoben und beim Scrollen fixiert. Regressionstest für leere Objektparameter im PHP/Unix-Socket-Test ergänzt; dieser Linux-Test wird lokal auf macOS übersprungen. Lokale Suite: 44 bestanden, 4 übersprungen.

Anmeldeablauf: Gefundene Fahrzeuge werden mit Anzahl und Modellliste direkt oberhalb des Anmeldeformulars gezeigt. „Weiter zur Einrichtung“ öffnet die hervorgehobene Fahrzeugauswahl vor Statusabruf und MQTT. Automatischer Wechsel nach Login/Fahrzeugabruf bleibt bei der Ergebnisliste im Kontobereich. Realer Browser-Test der bestehenden Testsitzung: Ergebnisliste vor Loginformular, Weiter-Button, sichtbare Checkbox vor Statusoptionen, Mobilansicht ohne Überlauf. Keine erneute Porsche-Anmeldung für diesen UI-Test.

Verbindungsdarstellung: bestätigte Anmeldung als grünes „Porsche Connect verbunden“ im Seitenkopf und „Keine erneute Anmeldung nötig“ im Kontobereich. Bei gespeicherter, nach Neustart noch ungeprüfter Sitzung eigene neutrale Anzeige „Sitzung gespeichert“. Loginformular bei beiden Zuständen zunächst verborgen, über „Andere Porsche-ID anmelden“ erreichbar. Gefundene Fahrzeuge und Einrichtung ohne roten Rahmen, kleinere Überschriften und Abstände. Browser-Test prüft Verbindungsanzeige, verborgenes und optional geöffnetes Formular sowie Fahrzeugauswahl und mobile Breite.

## Gestaltung: Connected performance

Eigenes skalierbares Verbindungsmonogramm in icons/icon.svg und webfrontend/htmlauth/logo.svg, einheitlich im Seitenkopf und im LoxBerry-Plugin-Symbolpfad. Oberfläche neu strukturiert mit heller Basis, schwarzen Primäraktionen, kleinen roten Logoakzenten, feinen Konturen, tabellarischen Messziffern und dunklen Fahrzeugstatuskarten. Referenzen: https://www.porsche.com/germany/ sowie https://designsystem.porsche.com/v3/styles/introduction/, /theme/ und /typography/. Gestaltung ist daran orientiert, keine behauptete offizielle CI-Zertifizierung. Eigene Vektorgrafik und lokale Systemschriften; keine externen Schrift- oder Designsystem-Runtime-Abhängigkeiten.

Realer Browser-Test auf der separaten Test-VM: Logo erfolgreich geladen, Verbindungsanzeige, verborgenes/optional geöffnetes Loginformular, gefundene Fahrzeuge, Weiterleitung zur Einrichtung und Auswahl geprüft. Mobil bei 390 px ohne horizontalen Überlauf; keine JavaScript-Fehler. Live-Sitzung und Produktions-App nicht geändert.

## Manueller Statusabruf und Speichern

Manuelle Statusabfrage von der Automatik-Einstellung getrennt; benötigt weiterhin gespeichertes Fahrzeug und gültige Sitzung, bestehende Fünf-Minuten-Sperre bleibt erhalten. Erstes fehlendes Fahrzeug in der Übersicht zeigt gezielt die noch ausstehende Speicherung statt erneut eine Anmeldung zu verlangen. Technischen MQTT-Namen klar beschriftet und Eingaben bei Änderung auf zulässige Kleinbuchstaben/Unterstriche normalisiert. Speichern bestätigt die Übernahme direkt im Formular und entfernt alte Fehlermeldungen erst bei Erfolg.

Test-VM: Einziges geladenes Fahrzeug unter Alias taycan gespeichert, MQTT und Automatik weiterhin aus. Echter Browser: Speichern bestätigt, Auswahl nach Seiten-Neuladen erhalten, manueller Abrufbutton aktiv. Python-Regression für manuellen Abruf ohne Automatik ergänzt. Lokale Suite: 45 bestanden, 4 Linux-Tests übersprungen. Beim ersten realen Statusabruf temporär keine verwendbaren Messwerte; nachfolgende Diagnosen meldeten aktivierte Batterie-/Reichweitenmessungen. Keine Rohdaten oder Tokens protokolliert.

Erneuter regulärer Abruf nach Ablauf der Fünf-Minuten-Sperre erfolgreich: API erfolgreich, Akkustand und Reichweite vorhanden, Messalter bekannt. Bestehende Altersgrenze kennzeichnet die gelieferten älteren Fahrzeugdaten korrekt als ungültig. Keine Fahrzeug-Weckfunktion ausgeführt. Anschließender Nur-Lese-Browsertest bestätigt sichtbare Batterie-/Reichweitenwerte und bedienbaren manuellen Abruf.

## Kompakte graue Ansicht und Modellbilder

Porsche stellt für das Testfahrzeug frontView/sideView/rearView/topView über /connect/v1/vehicles/{vin}/pictures bereit. Frontansicht wird optional im eigenen privaten Datenverzeichnis zwischengespeichert (0600, einmal pro Tag erneuern). Nur HTTPS zum tatsächlich geprüften Porsche-CDN erlaubt, keine Weiterleitungen, keine OAuth-Header am Bildserver, maximal 2 MB und PNG/JPEG/WebP-Signaturprüfung. Lokaler PHP-Bildendpunkt setzt LoxBerry-Anmeldung voraus, akzeptiert ausschließlich konfigurierte Fahrzeugaliasnamen, prüft MIME-Typ und gibt keine signierten Bildadressen oder VIN im Bildlink aus. Bildfehler verhindern keinen Statusabruf.

Übersicht auf helle graue Fahrzeugkarten umgestellt, Status- und Erfolgsanzeigen neutral grau, Kopf/Formulare/Abstände kompakter. Echtes fahrzeugspezifisches Bild mit Batterie und Reichweite im Browser geladen, Desktop und 390-px-Mobilansicht ohne horizontalen Überlauf geprüft. Erfolgreicher Statusabruf bestätigt den Verbindungsstatus; Modellnamen werden nach Neustart erneut geladen. Tests für privaten Bildcache, Wiederverwendung, fehlende Autorisierungsheader und Ablehnung fremder/unsicherer Bildserver ergänzt. Lokale Suite 49 bestanden, 4 Linux-Tests übersprungen. Produktion weiterhin unverändert.

## Gesamter lesbarer Parameterkatalog

80 Statusparameter aus MEASUREMENTS, TRIP_STATISTICS, HISTORY_MEASUREMENTS und DESTINATIONS angefragt. Zugangsschlüssel/Kopplungspasswörter und digitale Key-Payloads bewusst ausgeschlossen, verschachtelte Secret-Felder entfernt. Neue Parameter besitzen eigene Verfügbarkeit, Messzeit und Freigabe; unbekanntes Alter bleibt ungültig. Fehlende Batterie verhindert nicht mehr die Anzeige anderer gültiger Statusparameter. Begrenzte Datenstruktur und aufklappbare, gegen Status-Refresh stabile Detailansichten. Erweiterte MQTT-Topics liefern JSON-Wert und eigene Metadaten, CSV-Export ergänzt.

Realer Abruf auf der Test-VM: 80 katalogisierte Parameter, davon 51 verfügbar; sechs Gruppen, Statusantwort ca. 37 KB. Browser prüft 80 Parameter, sechs Gruppen, Batterie-Detailwerte, nach Status-Refresh weiter geöffnete Bereiche, geladenes Modellbild und 390-px-Mobilansicht ohne Überlauf. Python-Tests für voneinander unabhängige Zeitstempel, alternde Messwerte, echte 0/false-Werte, fehlende Werte, Secret-Filter und MQTT-JSON ergänzt. 52 Tests bestanden, 4 Linux-Tests lokal übersprungen. MQTT-Gateway/Miniserver für neue JSON-Topics noch nicht Ende-zu-Ende geprüft. Keine Fahrzeugbefehle oder Weckfunktion ausgeführt.

Fahrzeugkarte weiter verdichtet: Modellbild und Akku-/Reichweitenwerte nebeneinander, kurze gemeinsame Zeitzeile, auf Desktop zweispaltige Detailgruppen. Geöffnete Gruppen nutzen volle Breite, damit daneben keine große leere Spalte bleibt. Mobil ebenfalls Bild/Werte nebeneinander mit kompakter Typografie. Reiner UI-Deploy ohne Dienstneustart oder zusätzlichen Cloudabruf. Browser-Test mit Bild, 80 Parametern, geöffneten Details und mobiler Breite erfolgreich.

Übersicht von Detailparametern getrennt: neuer Tab „Fahrzeugdaten“ zeigt die sechs Statusgruppen je Fahrzeug einschließlich Anzahl verfügbarer Parameter. Übersicht enthält ausschließlich Bild, Hauptwerte, Zeitzeile und Integrationsstatus. Browser-Test prüft keine Parameter im Übersichts-DOM, 80 Parameter/6 Gruppen im neuen Tab, Details nach Statusaktualisierung weiterhin geöffnet, Tabwechsel und Mobilansicht ohne Überlauf. Reiner Frontend-Deploy, kein Dienstneustart.

## MQTT-Datenauswahl

84 Checkboxen (vier Hauptwerte und 80 Parameter) in Gruppen im Loxone-Tab; Alles/Keine, Zähler, explizites Speichern. Anzeige und Cloud-Abruf bleiben vollständig. Server validiert die Auswahllisten, alte Konfigurationen ohne Listen behalten bisherige Themen. Publisher lässt ungewählte Nutzwerte aus, hält Diagnosesignale aktiv und löscht abgewählte retained-Routen. Beim Einschalten nach einer Offline-Auswahl werden ausgeschlossene Topics einmalig bereinigt. Fehlgeschlagene Bereinigung verhindert die Speicherung. Force-invalid setzt auch parameterbezogene Freigaben auf 0.

Realer Browser auf Test-VM mit MQTT aus: zwei Nutzwerte ausgewählt, ungespeicherten Entwurf über Statusaktualisierung erhalten, gespeichert und nach Neuladen bestätigt; vorherige Auswahl danach wiederhergestellt. 390-px-Ansicht ohne Überlauf. Unit-Tests für Defaults/Keine, verbotene Schlüssel, gefilterten Versand, erhaltene Diagnosewerte, Retained-Bereinigung vor Speicherung und einmalige Bereinigung beim Einschalten. 57 Tests bestanden, 4 Linux-Tests lokal übersprungen. Die neuen Retained-Bereinigungsfälle wurden mit aufgezeichnetem Publisher geprüft, nicht gegen einen externen Broker/Miniserver.

## Einzelwerte und Loxone-XML

Stabile Einzelwertpfade unter fields/<parameter>/<pfad>/value und available zusätzlich zu bisherigen JSON-Themen. Echte Zahlen/Booleans, bekannte gepaarte Zustände und Zeitzonen-Zeitstempel in numerischer Darstellung; unbekannte Texte bleiben Text. Beobachtete Feldschemata bleiben erhalten, damit verschwundene Werte gelöscht werden. Ein zuvor numerisches Feld mit unbekanntem Text wird als nicht verfügbar behandelt. XML und CSV berücksichtigen gespeicherte Datenauswahl; empfohlener XML-Umfang Hauptwerte/Überwachung mit 17 Eingängen, volle Auswahl optional. Textfelder und zu lange UDP-Topics werden aus der numerischen Vorlage ausgelassen und gezählt. Keine aktuellen Messwerte werden in CSV/XML übernommen.

Formatprüfung anhand des echten installierten MQTT Gateways: build_udp_name erhält Schrägstriche; send_udp_bundled erzeugt MQTT:-Pakete bis 220 Zeichen. Originalfunktionen in isoliertem Namensraum mit abgefangener Sendefunktion ausgeführt: 1503 numerische Paare in 700 Paketen, Kennungen passen zum XML. Null Pakete an einen Miniserver gesendet. Voller Export in diesem Snapshot: 1546 numerische Einträge, 29 Textfelder ausgelassen. Schemareferenz: VirtualInUdp/Info/VirtualInUdpCmd aus https://github.com/AES-Concepts-GmbH/loxone2hue/blob/2dd0b74438de0d23fb5bc39fafcb9351f0a0cfe0/internal/api/export.go sowie unabhängige öffentliche Beispielvorlagen; Implementierung eigenständig.

Echter temporärer Mosquitto auf 127.0.0.1 und zufälligem Port ausschließlich in der Test-VM: 1656 Nachrichten (1655 verschiedene Topics) mit Quittierung in 0,62 s veröffentlicht und empfangen. Danach Auswahl auf Reichweite beschränkt: abgewählte Felder/JSON-Werte vollständig aus Retained-Speicher entfernt, 21 Themen verbleiben. Testbroker anschließend beendet, keine Produktivbroker-/Miniserver-Nachrichten.

Browser: authentifizierte XML-/CSV-Downloads mit UTF-8 BOM, Schema-Header, UDP-Port und optionalem Absenderfilter. Standardvorlage 17 Eingänge, volle Auswahl mit Einzelwertfeldern zusätzlich geprüft. Mobil ohne Überlauf. Unit-Tests für fehlende/wechselnde Feldtypen, Schemaerhalt, Escape-Zeichen, Exportauswahl, ungültige IP/Ports, Texte und schmale Abonnements. 68 Tests bestanden, 4 Linux-Tests lokal übersprungen. Der tatsächliche Import in Loxone Config und Ende-zu-Ende-Miniserver-Abnahme bleiben offen.

## Durchsuchbare Fahrzeugdaten-Karten

Detailkatalog in eigenständige weiße Gruppenkarten mit grauen Symbolfeldern, Verfügbarkeitszähler, Statusbadges und kurzen Wertevorschauen umgestaltet. Volltextsuche lokal im Browser über Parametername, API-Kennung, Gruppe, Alias und rohe/formatierte Werte; Umlaute und Groß-/Kleinschreibung normalisiert. Statusfilter für verfügbar, aktuell, veraltet, nicht verfügbar, unbekanntes Messalter und gespeicherte MQTT-Auswahl. Trefferzahl, Zurücksetzen und Leerzustand ergänzt. Filter/Suche bleiben bei Statusaktualisierungen erhalten; passende Gruppen öffnen sich automatisch. Kelvin-Zieltemperatur wird entsprechend der Bibliothekssemantik als Celsius dargestellt, explizite Bar/kW/km/min-Felder mit Einheit; keine Änderung der API-/MQTT-Werte.

Realer Nur-Lese-Browsertest auf Test-VM: sechs Karten/80 Parameter, Reifendrucksuche mit vier Treffern, Suche nach CHARGING_RATE, Volltextsuche nach NORMAL, keine Treffer, verfügbare/nicht verfügbare Filter, Erhalt über 3-Sekunden-Refresh, mobile Details ohne Überlauf und keine JavaScript-Fehler. JavaScript-Syntax geprüft. Reiner UI-Deploy ohne Dienstneustart, zusätzliche Porsche-Abfrage oder Konfigurationsänderung. Keine Produktionsänderungen.

## Kompakte Parameterliste

Gruppen durchgehend untereinander, auch geöffnet ohne Wechsel der Spaltenbreite. Parameterzeilen nutzen die gesamte Kartenbreite mit Name/Status links und Wertevorschau rechts; mobile Darstellung gestapelt. Realer Browsercheck auf Test-VM: gleiche Gruppenbreiten, Reihenfolge ohne Überlappung, volle Parameterbreite; Suche, Filter, Refresh-Erhalt und mobile Details weiterhin geprüft. Reiner UI-Deploy ohne Dienstneustart oder Änderungen an Sitzung/Konfiguration.

## PLX-Branding

Anzeigename, Exporttitel und Installationspaket auf PLX umbenannt; technische Plugin-ID und vorhandene MQTT-/Datenpfade bleiben kompatibel. App-Icon mit eingebettetem Porsche-Wappen aus dem öffentlichen Porsche Design System, ohne externe Bildanfrage beim Seitenaufruf. Test-VM: Frontend und LoxBerry-Anzeigename aktualisiert, keine Dienstneustarts oder Änderungen an Anmeldung/Konfiguration. PHP-Syntax, realer Desktop-/Mobil-Browsertest und 68 Unit-Tests bestanden; 4 Linux-Tests lokal übersprungen.

## Eigenständiger Docker-Betrieb

Gemeinsame Dashboard-Dateien und Statusdienst unverändert als Basis; separater Python-HTTPS-Adapter mit eigener PLX-Webanmeldung, CSRF, achtstündigen privaten Websitzungen, Login-Begrenzung und privater Bildauslieferung. Nur explizite API-Aktionen und statische Dateien erreichbar. PLX-Abmeldung beendet keine Porsche-Sitzung. Docker-Image enthält keine Projekt-/Testdaten oder Zugangsdaten; eigener persistenter Datenspeicher.

Lokales ARM64-Image tatsächlich mit vorhandener Podman-Laufzeit im Docker-Format gebaut, mit schreibgeschütztem Dateisystem, entfernten Capabilities und UID/GID 10001 gestartet. Healthcheck erfolgreich. Reales Chrome: HTTPS, PLX-Anmeldung/Abmeldung, CSRF-Abweisung, frische abgemeldete Porsche-Sitzung, fünf gemeinsame Tabs, mobile 390px ohne Überlauf und keine JavaScript-Fehler. Einstellungen und Zertifikat im eigenen Testvolume über Neustart geprüft. Keine Porsche-Anmeldung/Cloud-Anfrage, keine Verbindung zu Test-LoxBerry oder produktiver Taycan-App. 74 lokale Tests bestanden, vier bestehende Linux/PHP/Mosquitto-Tests lokal übersprungen. GitHub-Linux-Lauf: 77 Tests bestanden, ein bereits bestehender Plattformtest übersprungen; Docker-Compose-Build und Healthcheck erfolgreich. Multiarch-Veröffentlichung von AMD64/ARM64 erfolgreich: GitHub Actions #1, Quellcommit 2636646506dcdfa5bd42bc8c9f32c55c6bfc8626, ghcr.io/square-com-de/plx:edge. Anonymer Manifestabruf wird entsprechend der privaten Paketsichtbarkeit abgelehnt. Eine erneute echte Porsche-Anmeldung im Docker-Betrieb ist noch nicht durchgeführt.

## Einfaches MQTT-Abonnement

Anzeige und Exportmetadaten verwenden einheitlich `<konfiguriertes Präfix>/#`, unabhängig vom XML-Exportumfang. Kurzer Hinweis erklärt den Unterschied zwischen Empfangsabonnement und Versand-Auswahl. Versand-Auswahl, Topics und Nutzdaten bleiben unverändert. Bestehende Exporttests auf Hauptwerte, ausgewählte Parameter und eigenes Präfix angepasst.

## Einfache MQTT-Werteausgabe

Explizites Format `simple`: ein Topic je gespeicherter Auswahl; Reifendruck projiziert ausschließlich `actualPressureBar` in bar. Keine Heartbeat-/Metadaten-/Verfügbarkeits-/JSON-Doppelthemen oder katalogweiten Startlöschungen. Fehlende/ungültige Werte ergeben `null`, echte0bleibt0. Bestehende Konfigurationen ohne Format bleiben `detailed`, Neuinstallationen starten einfach. Format bleibt beim Speichern beider Formulare erhalten. Einzelne Abwahlen löschen nur tatsächlich vorher gewählte Routen, Migration kennt die alten ausgewählten Meta-/Überwachungsthemen. Einfacher XML-/CSV-Export enthält nur gewählte Werte. Neue Regressionstests: exakte Zweierausgabe trotz großer ungewählter Historie, fünf ungültige Druckfälle, echtes0, Neuversand/Shutdown/Restart ohne Löschserie, Brokerreparatur ohne alte-Ziel-Invalidierung, gezielte Abwahl,29→2-Migration sowie Exportumfang/Kompatibilität. Einfaches MQTT-Speichern erhält vorhandene Messwerte und den Cloud-Abrufplan; keine zusätzliche Porsche-Abfrage. Lokaler Stand: 90 bestanden, vier Linuxplattformtests übersprungen. Browser: zwei ausgewählte Reifendrücke, ausgeblendete Diagnose-/Exportumfangselemente, eingeklappte erweiterte Optionen, beide Speicherformulare erhalten Modus und Auswahl, mobile390px ohne Überlauf und keine JavaScript-Fehler.

Nachprüfung: fehlendes Formatfeld eines älteren Clients bewahrt den gespeicherten Modus. Einfache Ausgabe liefert zuletzt gemeldete vorhandene Werte auch bei unbekanntem/hohem Messalter und nach Neustart; Alter/Verbindungsstatus bleiben in PLX. Keine erfundenen Null-Druckwerte.


## Deutsch / Englisch

`tools/check-language.cjs` prüft mit simulierten Fahrzeugdaten den DE/EN-Wechsel, Speicherung nach Neuladen, englische Suche, dynamische Statusmeldungen nach Polling, Erhalt ungespeicherter Eingaben und der zwei MQTT-Auswahlen, Handyansicht ohne Überlauf sowie beide Sprachen der Docker-Anmeldeseite. Benötigt Playwright (über NODE_PATH), Chrome und Python mit den Projektabhängigkeiten (PYTHON). Kein Zugriff auf Porsche oder MQTT.


## Finale LoxBerry-4-Abnahme am 24.10.2026

Auf dem zugeordneten, isolierten Testklon (DietPi/Debian 13.7, LoxBerry 4.0.0.15) wurde ein echter Updatefehler entdeckt und behoben: Der LoxBerry-Installer löscht bei Updates Konfigurations- und Datenverzeichnisse. `preroot.sh` stoppt jetzt ausschließlich den eigenen Dienst; `preupgrade.sh` übernimmt Einstellungen, Sitzung, Status und Bilder vor der Löschung in den geschützten Installer-Zwischenstand. Venv, Socket, Lock und Symlinks werden nicht übernommen. Unbekannte Unterverzeichnisse stoppen das Update vor der Löschung. Regressionstests prüfen den tatsächlichen Purge-Zyklus, private Dateirechte und die Beschränkung auf die eigene nummerierte Plugin-Unit.

Erfolgreich geprüft: Neuinstallation und erneute Installation als Update über den offiziellen LoxBerry-Installer, Erststart mit ausgeschaltetem Abruf/MQTT und einfacher Ausgabe, HTTP 401 ohne Anmeldung, HTTP 403 ohne CSRF, HTTPS mit geprüftem Testzertifikat, gespeicherte Sitzung und zwei MQTT-Auswahlen über Update erhalten, installierte Programm-/Frontenddateien gleich ZIP-Inhalt, Speichern über die echte PHP-Oberfläche, Fahrzeug- und Statusabruf mit eigener Testsitzung.

Realer Browser: DE/EN samt Neuladen, Header-Ausrichtung, dezenter Verbindungsstatus, ungespeicherte Eingaben über Refresh/Sprachwechsel erhalten, zwei Auswahlen, mobile390px ohne Überlauf und keine JavaScript-Fehler. Installierter echter MQTT-Publisher gegen einen ausschließlich an Loopback gebundenen temporären Mosquitto: genau zwei numerische Reifendruckwerte, keine Zusatz- oder Löschmeldungen. Danach temporären Broker beendet und ursprüngliche Testeinstellungen wiederhergestellt. Keine Verbindung zur produktiven Taycan-App oder ihrem Broker. Der vorhandene Docker-Testcontainer bleibt unverändert.

Der genaue ZIP-Hash und die einzelnen Laufnachweise werden außerhalb des Pluginpakets im Release-Abnahmeprotokoll festgehalten, damit keine Zugangsdaten oder realen Fahrzeugdaten ins Release gelangen. Eine Ende-zu-Ende-Prüfung bis zum Loxone-Miniserver bleibt getrennt offen.
