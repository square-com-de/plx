# PLX-Handbuch

[English](MANUAL.md) · [Installation](../INSTALL.de.md) · [Projektseite](../README.de.md)

## Übersicht und Porsche-Konto

Die Übersicht zeigt ausgewählte Fahrzeuge, Batterie, Reichweite und Messalter, soweit verfügbar. „Cloud-Abruf“ ist der Zeitpunkt der Abfrage durch PLX, nicht der Messzeitpunkt im Fahrzeug. Der Verbindungsstatus beschreibt die Porsche-Sitzung, nicht die Aktualität sämtlicher Messwerte.

Im Porsche-Konto anmelden, bei Bedarf CAPTCHA bestätigen und Fahrzeuge laden. Eine gespeicherte/verbundene Sitzung erfordert normalerweise keine erneute Anmeldung; PLX erneuert die Tokens automatisch. Abmelden löscht nur diese PLX-Porsche-Sitzung. „PLX abmelden“ in Docker beendet dagegen nur die Websitzung.

## Einrichtung

Gewünschte Fahrzeuge oben auswählen und **speichern**. Ein gefundenes Fahrzeug ist noch nicht automatisch ausgewählt. Der technische Name dient als MQTT-Topic-Bestandteil: Kleinbuchstaben, Ziffern, `_` und `-`, höchstens 32 Zeichen, Beginn mit einem Buchstaben.

Automatischer Abruf und MQTT sind getrennte Schalter. Empfohlen sind 15 Minuten; manuelle Statusabfragen sind auf einmal in fünf Minuten begrenzt. „Maximales Alter der Fahrzeugdaten“ betrifft die Gültigkeitsanzeige, nicht die Meldehäufigkeit des Autos. Ein schlafendes Fahrzeug kann auch bei neuer Cloud-Abfrage alte Daten liefern.

## Fahrzeugdaten

Die Suche findet Namen, technische Kennungen und Werte. Filter zeigen verfügbare, aktuelle, veraltete, fehlende oder für MQTT ausgewählte Parameter. Ein fehlender Wert ist kein eindeutiger Nachweis fehlender Hardwareunterstützung: Ausstattung, Vertrag, Berechtigungen, Cloud-Antwort und Zeitstempel können die Verfügbarkeit beeinflussen. Eine leere Historie kann schlicht keine Einträge enthalten.

Die Oberfläche zeigt unabhängig von der MQTT-Auswahl alle Parameter. Gruppen haben eigene Angaben zu Messalter und Verfügbarkeit.

## MQTT und Loxone

Den **tatsächlichen MQTT-Broker** eintragen, nicht einen Hostnamen, der nur die HTTPS-Webseite bedient. Ein Webproxy kann korrekt per DNS auflösen und TCP/1883 trotzdem ablehnen; HTTPS/443 belegt keine MQTT-Erreichbarkeit. Port/TLS müssen zum Broker passen (häufig 1883 ohne oder 8883 mit TLS, maßgeblich ist dessen Listener). `127.0.0.1` im Container ist kein Broker auf einem anderen Host.

Nach Speichern der Brokeradresse **im selben Compose-Verzeichnis und Projekt** prüfen (`-p plx` bei Bestandsinstallation durch den echten Projektnamen ersetzen). Der Befehl liest nur Host/Port/TLS, gibt keine Zugangsdaten aus und sendet/abonniert kein MQTT:

```sh
docker compose -p plx exec -T plx python - <<'PYTHON'
import json, socket, ssl
c = json.load(open('/data/config/settings.json'))['mqtt']
host, port = c['host'], c['port']
print('Broker:', host, 'Port:', port)
print('Resolved:', sorted({a[4][0] for a in socket.getaddrinfo(host, port, type=socket.SOCK_STREAM)}))
with socket.create_connection((host, port), timeout=5) as connection:
    if c.get('tls'):
        with ssl.create_default_context().wrap_socket(connection, server_hostname=host):
            print('TCP and verified TLS connected')
    else:
        print('TCP connected; TLS is disabled in PLX')
PYTHON
```

TCP-/TLS-Erfolg belegt Erreichbarkeit, **keine** MQTT-Zugangsdaten oder Publish-ACL. Bei abgelehntem TCP zuerst Adresse/Listener/Firewall prüfen statt Kennwörter ändern. Zertifikatsprüfung nicht abschwächen. Bei Portainer die entsprechende Prüfung in der PLX-Containerkonsole ausführen.

Danach unter Loxone Werte wählen und speichern. Vollständiges Abonnement beim Standardpräfix:

```text
porsche2lox/#
```

Bei eigenem Präfix `<Präfix>/#` verwenden. Das Abonnement empfängt passende Nachrichten; es veranlasst PLX nicht zum Versand aller Parameter. Gespeicherte Auswahl und einfaches/ausführliches Format bestimmen den Versand.

**Einfache Ausgabe (Standard bei Neuinstallation):** ein Topic pro gewähltem Wert. Reifendruck wird als tatsächlicher Druck in bar gesendet, nicht als Druckabweichung. Fehlende Werte sind JSON `null`; eine echte numerische Null bleibt Null. Strukturierte andere Parameter bleiben jeweils ein JSON-Topic. Zwei ausgewählte Reifendrücke ergeben genau zwei Topics.

Einfaches MQTT sendet den zuletzt gemeldeten Wert auch bei unbekanntem oder hohem Messalter. Es gibt keine zusätzlichen Heartbeat-, Verfügbarkeits- oder Altersthemen. Retained-Werte können nach Verbindungsabbruch oder Dienstende bestehen bleiben. Für Automationen, die aktuelle Daten voraussetzen, das ausführliche Format mit Freigabe-/Verfügbarkeitssignalen verwenden.

**Ausführliche Ausgabe:** unter „Erweiterte Ausgabeoptionen“ wählbar. Ergänzt Diagnose, Verfügbarkeit, Zeitstempel und einzelne Detailfelder. Bestehende Installationen ohne Formatangabe behalten dieses Verhalten. Beim Formatwechsel oder Abwählen werden bekannte alte Topics einmal bereinigt; das ist keine regelmäßige Löschserie.

XML/CSV ist optional. XML dient numerischen virtuellen UDP-Eingängen über ein MQTT Gateway; CSV beschreibt auch nichtnumerische Felder. UDP-Port einstellen, auf dem der Miniserver die Gateway-Nachrichten erhält (Exportvorgabe 11883), und optional die **UDP-Absender-IP**. Gemeint ist der MQTT-Gateway-Host aus Sicht des Miniservers, nicht automatisch Docker-Host, Broker, LoxBerry oder Miniserver. Im Zweifel den Filter leer lassen; ein falscher Filter verwirft möglicherweise alle Werte. Broker-TCP-Port und UDP-Brückenport sind verschiedene Einstellungen. Ein XML-Import bestätigt noch nicht den gesamten Weg bis zum Miniserver; diesen vor Ort testen. Siehe [Loxone-Zuordnung](LOXONE.md).

## Häufige Fragen

| Beobachtung | Prüfen |
| --- | --- |
| Angemeldet, aber keine Übersichtswerte | Fahrzeug in der Einrichtung auswählen, speichern und Status abrufen. |
| Broker nicht erreichbar | Container-DNS/TCP wie oben prüfen. Ein Webproxy-Hostname kann als MQTT-Ziel falsch sein; abgelehntes TCP belegt kein falsches Passwort. Port/TLS und danach MQTT-Berechtigung prüfen. |
| Unerwartet viele Topics | Format und gespeicherte Datenauswahl prüfen. Alte Monitorzeilen sind nicht zwingend aktuell gespeicherte Broker-Topics. |
| Trotz Abruf alte Daten | Messalter und Cloud-Abruf unterscheiden. PLX weckt das Auto nicht auf. |
| Anderes Auto liefert andere Parameter | Ausstattung, Vertrag und Porsche-Antwort unterscheiden sich. Fehlend nicht als Null behandeln. |
| Image lässt sich nicht laden | Öffentliches Release `ghcr.io/square-com-de/plx:0.1.0` oder dessen Digest verwenden; Schreibweise, Netzwerk und Registry-Konfiguration prüfen. Kein Token nötig. |
| HTTPS-Adresse bei LoxBerry abgewiesen | 0.1.0 erkennt HTTPS am Frontend mit internem HTTP nicht. Direktes LoxBerry-HTTPS verwenden, Schutz nicht abschalten. [Bekannte Grenze](../INSTALL.de.md#loxberry-plugin). |
| Nach Neustart erneut anmelden | Die PLX-Webanmeldung ist getrennt von der gespeicherten Porsche-Sitzung. |

Runtime-Status einschließlich nicht abgenommenem Podman/Rootless: [Installationsmatrix](../INSTALL.de.md#runtime-status). Keine Stable-Abnahme behauptet; siehe [Fehleraufarbeitung und Gate](INSTALLATION-LESSONS.de.md).

## Sicherung und Hilfe

[Update-/Sicherungsanleitung](../INSTALL.de.md#updates-sicherung-und-rückweg) beachten. Datenvolume beziehungsweise Plugin-Daten und Zugangsdaten geschützt sichern: Sie können Tokens, Standort-/Fahrtdaten und TLS-Schlüssel enthalten. Für [GitHub-Feedback](https://github.com/square-com-de/plx/issues/new?template=feedback_question.md) nur bereinigte Bilder/Logs verwenden. Schwachstellen siehe [Sicherheit](../SECURITY.md).
