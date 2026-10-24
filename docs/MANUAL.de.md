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

Broker in der Einrichtung konfigurieren, unter Loxone die Werte auswählen und speichern. Ein Abonnement, `<Präfix>/#`, empfängt alle unter diesem Präfix gesendeten PLX-Nachrichten.

**Einfache Ausgabe (Standard bei Neuinstallation):** ein Topic pro gewähltem Wert. Reifendruck wird als tatsächlicher Druck in bar gesendet, nicht als Druckabweichung. Fehlende Werte sind JSON `null`; eine echte numerische Null bleibt Null. Strukturierte andere Parameter bleiben jeweils ein JSON-Topic. Zwei ausgewählte Reifendrücke ergeben genau zwei Topics.

Einfaches MQTT sendet den zuletzt gemeldeten Wert auch bei unbekanntem oder hohem Messalter. Es gibt keine zusätzlichen Heartbeat-, Verfügbarkeits- oder Altersthemen. Retained-Werte können nach Verbindungsabbruch oder Dienstende bestehen bleiben. Für Automationen, die aktuelle Daten voraussetzen, das ausführliche Format mit Freigabe-/Verfügbarkeitssignalen verwenden.

**Ausführliche Ausgabe:** unter „Erweiterte Ausgabeoptionen“ wählbar. Ergänzt Diagnose, Verfügbarkeit, Zeitstempel und einzelne Detailfelder. Bestehende Installationen ohne Formatangabe behalten dieses Verhalten. Beim Formatwechsel oder Abwählen werden bekannte alte Topics einmal bereinigt; das ist keine regelmäßige Löschserie.

XML/CSV ist optional. XML dient numerischen virtuellen UDP-Eingängen über ein MQTT Gateway; CSV beschreibt auch nichtnumerische Felder. UDP-Port des Gateways und optional dessen Absender-IP einstellen. Ein XML-Import bestätigt noch nicht den gesamten Weg bis zum Miniserver; diesen vor Ort testen. Siehe [Loxone-Zuordnung](LOXONE.md).

## Häufige Fragen

| Beobachtung | Prüfen |
| --- | --- |
| Angemeldet, aber keine Übersichtswerte | Fahrzeug in der Einrichtung auswählen, speichern und Status abrufen. |
| Broker nicht erreichbar | Netzwerkadresse, Port, Zugangsdaten und TLS-Einstellung prüfen. `127.0.0.1` ist in Docker PLX selbst. |
| Unerwartet viele Topics | Format und gespeicherte Datenauswahl prüfen. Alte Monitorzeilen sind nicht zwingend aktuell gespeicherte Broker-Topics. |
| Trotz Abruf alte Daten | Messalter und Cloud-Abruf unterscheiden. PLX weckt das Auto nicht auf. |
| Anderes Auto liefert andere Parameter | Ausstattung, Vertrag und Porsche-Antwort unterscheiden sich. Fehlend nicht als Null behandeln. |
| Image lässt sich nicht laden | Öffentliches Release `ghcr.io/square-com-de/plx:0.1.0` oder dessen Digest verwenden; Schreibweise, Netzwerk und Registry-Konfiguration prüfen. Kein Token nötig. |
| Nach Neustart erneut anmelden | Die PLX-Webanmeldung ist getrennt von der gespeicherten Porsche-Sitzung. |

## Sicherung und Hilfe

[Update-/Sicherungsanleitung](../INSTALL.de.md#updates-und-sicherung) beachten. Datenvolume beziehungsweise Plugin-Daten und Zugangsdaten geschützt sichern: Sie können Tokens, Standort-/Fahrtdaten und TLS-Schlüssel enthalten. Für [GitHub-Feedback](https://github.com/square-com-de/plx/issues/new?template=feedback_question.md) nur bereinigte Bilder/Logs verwenden. Schwachstellen siehe [Sicherheit](../SECURITY.md).
