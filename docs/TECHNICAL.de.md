# PLX – Porsche Connect für dein Zuhause

[English](../README.md) · [Release-Entwurf](RELEASE-0.1.0.md)

Auch als eigenständiger HTTPS-Docker-Container mit derselben Oberfläche verfügbar (`ghcr.io/square-com-de/plx:edge`, AMD64/ARM64, derzeit privates GitHub-Paket): [Docker-Anleitung](DOCKER.md). Die LoxBerry-Installation bleibt ein separater Betriebsweg.

Statusintegration für Porsche Connect mit geschützter Weboberfläche und eigener Anmeldung. Version **0.1.0 – Testversion**, auf separater LoxBerry-4-Test-VM mit echter Porsche-Sitzung geprüft; Ende-zu-Ende-Abnahme mit einem Miniserver noch ausstehend.

## Sprache

Oben rechts zwischen Deutsch und Englisch wechseln. Die Auswahl bleibt lokal im Browser gespeichert und gilt auch für die Docker-Anmeldeseite. MQTT-Topics, gespeicherte Einstellungen und API-Daten bleiben sprachunabhängig.

## MQTT-Ausgabe

Neue Installationen senden standardmäßig ein Topic je ausgewähltem Wert. Reifendruck wird direkt als Zahl in bar gesendet, ohne zusätzliche Diagnose-/Verfügbarkeitsthemen oder Start-Löschserien. Zwei ausgewählte Reifendrücke ergeben zwei Topics. Fehlende Werte erscheinen als `null`. Der einfache Modus sendet zuletzt gemeldete Werte; Messalter und Verbindungszustand bleiben in PLX sichtbar. Das bisherige ausführliche Format bleibt für bestehende Installationen erhalten und ist unter den erweiterten Ausgabeoptionen wählbar.

## Voraussetzungen und Template für LoxBerry

- LoxBerry **4.0 oder neuer**, Debian 12 oder neuer, Python **3.11+**, systemd, PHP-Weboberfläche.
- Internetzugang zu Porsche und zum Python-Paketindex während der Installation.
- Porsche-ID mit aktivem Porsche Connect und einem Fahrzeug mit Batteriestatus; Schwerpunkt Taycan/BEV. Porsche Car Connect wird nicht unterstützt.
- HTTPS am LoxBerry für Anmeldung und Konfiguration. Die Oberfläche verweigert Zugangsdaten über unverschlüsseltes HTTP.
- MQTT-Broker und LoxBerry MQTT Gateway für die Weitergabe an Loxone.

Grundlage ist die Paketstruktur des offiziellen [SamplePlugin V4](https://github.com/mschlenstedt/LoxBerry-Plugin-SamplePlugin-V4), geprüft am 21.10.2026 am Stand `8d665d3d902cfc56b9bf377624dd434e187c0045`: plugin.cfg, htmlauth, PHP-SDK, postinstall/postroot und Deinstallation. Die LoxBerry-Umgebungsvariablen und der tatsächliche Installationsordner aus Argument 3 werden verwendet; nummerierte Pluginordner sind möglich. Statt eines zweiten Bootskripts übernimmt ein eigener systemd-Dienst den Start und die Überwachung. Es wird kein fremder Beispielcode samt Platzhaltern installiert.

## Installation auf einem getrennten Test-LoxBerry

1. `dist/PLX-LoxBerry-0.1.0.zip` in der LoxBerry-Pluginverwaltung installieren. Die ZIP-Prüfsumme liegt daneben.
2. Die Installation erstellt eine eigene virtuelle Umgebung und einen Dienst `porsche2lox-<tatsächlicher Pluginordner>.service`, standardmäßig `porsche2lox-porsche2lox.service`.
3. Plugin über die geschützte LoxBerry-Oberfläche **mit HTTPS** öffnen.
4. Unter **Porsche-Konto** anmelden. CAPTCHA bei Bedarf eingeben. Der Vorgang bleibt maximal fünf Minuten aktiv. Bei abweichenden Porsche-Anmeldeschritten ist eine Anpassung des unabhängigen API-Clients nötig.
5. Nach der Anmeldung gefundene Fahrzeuge prüfen und **Weiter zur Einrichtung** wählen. Fahrzeugauswahl speichern, danach unter Übersicht manuell Status abrufen. Automatischen Abruf und MQTT bei Bedarf separat einschalten.
6. Unter **Loxone** nur die gewünschten Werte auswählen und speichern. Für MQTT das angezeigte Abonnement `<Präfix>/#` verwenden. Die XML-/CSV-Vorlage ist optional für das MQTT Gateway und virtuelle UDP-Eingänge in Loxone Config; siehe [Loxone-Anleitung](LOXONE.md).

Statusabruf und MQTT sind bei einer Erstinstallation deaktiviert. Die Anmeldung allein aktiviert keinen Timer. Es findet kein Fahrzeug-Aufwecken statt.

## Bestehende Taycan-App

Die vorhandenen Pfade `/opt/loxberry/data/porsche`, `/opt/porsche-loxone/venv`, die Sitzung dort, die Dienste `porsche-taycan.*` und die Topics `porsche/taycan/*` werden weder gelesen noch verändert. Es gibt keinen automatischen Import und keine automatische Ablösung. PLX verwendet eine eigene Sitzung und eigene Topics. Ein späterer Wechsel muss separat geplant werden.

## Status und Datenqualität

- Eigene Modellbilder aus Porsche Connect, privat lokal zwischengespeichert; kompakte neutrale Oberfläche mit aufklappbaren Statuskarten, Volltextsuche und Filtern für Verfügbarkeit, Messalter und MQTT-Auswahl.
- Alle 80 lesbaren Statusparameter des Bibliothekskatalogs einschließlich Fahrtstatistik, Wartung, Klima, Türen/Fenster, Reifendruck und Standort angefragt. Verfügbarkeit hängt vom Fahrzeug und Vertrag ab. Kopplungspasswörter und digitale Zugangsschlüssel sind ausgeschlossen.
- Nur GET-Aufrufe für Fahrzeugliste und gespeicherte Messwerte; der Adapter verweigert Porsche-Schreibmethoden. Keine Fernsteuerung, kein `wakeUpJob`.
- Rohdaten werden geprüft: fehlender oder ungültiger Akkustand bleibt unbekannt und wird niemals als 0 % ausgegeben. Andere verfügbare Statusparameter bleiben trotzdem sichtbar; echte 0 % werden korrekt erkannt.
- `target_soc` enthält nur ein explizites `targetSoC` oder `CHARGING_SETTINGS.targetSoc`. Ein Profil-Mindestwert ist kein Ladeziel.
- Fehlender Direktlademodus ist unbekannt, nicht automatisch ausgeschaltet. Der Modus ist kein Nachweis eines laufenden Ladevorgangs.
- Messalter wird aus `BATTERY_LEVEL.value.lastModified` mit Zeitzone ermittelt. Fehlt dieser Zeitstempel, bleiben Werte sichtbar, aber `data_valid=0`. Es wird kein Cloud-Abrufzeitpunkt als Messzeit ausgegeben. Zusätzliche Porsche-Zeitstempelformate müssen anhand anonymisierter realer Antworten verifiziert werden.
- `data_valid` auf Fahrzeugebene bezieht sich auf den Batteriemesszeitpunkt und den letzten Abruf. Die 80 erweiterten Statusparameter haben jeweils eigene Verfügbarkeit und Altersprüfung. Im optionalen ausführlichen MQTT-Format stehen sie unter `parameters/<parameter>/value` als JSON, ergänzt um `available`, `data_valid` und `measurement_epoch`. Unbekanntes Messalter wird nicht als gültig ausgegeben.
- API-Ausfälle behalten den letzten Messwert in der Oberfläche. Einfaches MQTT sendet zuletzt gemeldete Werte, fehlende Werte als `null`; Alter und Verbindungszustand müssen in PLX geprüft werden. Das ausführliche Format ergänzt Freigabesignale und löscht nicht verfügbare retained-Werte.
- Zugangsdatenfehler pausieren automatische Abrufe. Rate Limits führen zu längeren Pausen. Manuelle Statusabfragen sind auf höchstens einmal in fünf Minuten begrenzt.
- Unter **Loxone** lassen sich vier Hauptwerte und alle 80 Detailparameter einzeln für MQTT auswählen. Die Anzeige bleibt vollständig. Im einfachen Format gibt es keine zusätzlichen Überwachungsthemen. Nur tatsächlich abgewählte alte Topics werden einmal bereinigt; CSV berücksichtigt die Auswahl.
- Einfaches MQTT sendet genau ein Topic pro Auswahl, Reifendruck numerisch in bar. Strukturierte Werte bleiben je Auswahl ein JSON-Topic. Die optionale XML-Vorlage enthält ausgewählte numerische Werte; Texte bleiben MQTT/CSV vorbehalten. Zusätzliche einzelne Felder und Überwachung stehen nur im ausführlichen Format bereit.
- MQTT wird quittiert; ein Brokerfehler wird getrennt vom Porsche-Status angezeigt.

## Sicherheit und Sitzung

Der Python-Dienst läuft als `loxberry`, ohne Rootrechte und ohne offenen TCP-Steuerport. PHP kommuniziert über einen privaten Unix-Socket. Die Weboberfläche verwendet LoxBerrys `htmlauth`, eine authentifizierte Benutzerkennung und PHP-Sitzungen mit CSRF-Schutz. Passwörter werden nicht an die Oberfläche zurückgegeben.

Porsche-Passwort, Cookies und PKCE/CAPTCHA-Kontext bleiben während des Loginvorgangs nur im Arbeitsspeicher; die Zugangsdatenreferenzen werden bei Abschluss/Abbruch/Timeout geleert. Sitzungstokens und MQTT-Passwort liegen in Dateien mit Modus 600 in privaten Pluginverzeichnissen. Eine LoxBerry-Gesamtsicherung kann diese Dateien enthalten und muss entsprechend geschützt werden. Bibliothekslogs mit potenziellen Geheimnissen werden unterdrückt.

Token-Erneuerungen werden atomar und **vor** dem eigentlichen Messwertabruf gespeichert. Die HTTP-Verbindungen werden geschlossen. Eine Dateisperre verhindert parallele Dienstinstanzen. Abmelden löscht ausschließlich die eigene PLX-Sitzung.

## Updates und Deinstallation

Das Paket enthält keine settings.json, Sitzung oder Laufzeitdaten. Beim Update stoppt der Root-Vorbereitungshook ausschließlich den eigenen Dienst. Der LoxBerry-preupgrade-Hook sichert Konfiguration und private Daten in den geschützten Installer-Zwischenstand, bevor LoxBerry die bisherigen Plugin-Verzeichnisse löscht. Die Python-Umgebung wird neu erstellt; Einstellungen und Sitzung werden wieder übernommen. Der Dienst wird nach erfolgreichem Installieren neu gestartet. Autoupdates sind bis zu einem veröffentlichten Release deaktiviert.

Deinstallation stoppt und entfernt ausschließlich die eigene systemd-Unit. Die Pluginverzeichnisse entfernt LoxBerry. Im ausführlichen MQTT-Format werden retained-Daten beim geregelten Dienstende als ungültig markiert; bei einem harten Ausfall muss dort der Heartbeat-Watchdog greifen. Im einfachen Format bleiben zuletzt gesendete Werte am Broker gespeichert, auch nach Dienstende; es gibt keinen Heartbeat und keine automatische Offline-Kennung. Bei unerreichbarem Broker kann keine abschließende MQTT-Nachricht garantiert werden.

## Lokale Entwicklung

```sh
python3.11 -m venv .venv
.venv/bin/pip install --require-hashes -r bin/requirements.lock.txt
.venv/bin/pip install pytest==8.4.2
.venv/bin/python -m pytest -q tests
python3 tools/build.py
```

Die Laufzeitabhängigkeiten sind exakt mit SHA-256-Hashes festgelegt. Der Builder verwendet eine ausdrückliche Dateiliste und packt keine Testumgebung, Zugangsdaten oder Laufzeitdateien ein.

Ein isolierter Linux-Test ist mit `tools/Dockerfile.test` möglich. Er ist kein vollständiges LoxBerry-System. Installation, Aktualisierung und HTTPS-Weboberfläche wurden inzwischen auf einer separaten echten LoxBerry-4-Test-VM geprüft. Porsche-Login, Fahrzeugabruf und MQTT zum Broker wurden auf der getrennten Docker-Testinstanz geprüft. Die Ende-zu-Ende-Prüfung mit MQTT-Gateway/Miniserver bleibt offen. Die produktive App wird dafür nicht verwendet.

Siehe `docs/TESTS.md` für ausgeführte Prüfungen und verbleibende Abnahme.

Der Anzeigename ist PLX (vormals Porsche2Lox). Technische Plugin-ID, Dienst- und Datenpfade sowie bestehende MQTT-Präfixe bleiben für Update-Kompatibilität unverändert.

## Lizenz

Eigener PLX-Code: [MIT](../LICENSE), einschließlich kommerzieller Nutzung. Fremdbibliotheken und Porsche-Markenzeichen sind davon ausgenommen; siehe [Dritthinweise](../THIRD-PARTY-NOTICES.md).
