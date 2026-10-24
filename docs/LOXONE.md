# Loxone-Anbindung

## Einfache MQTT-Ausgabe

Für neue Installationen gilt „Nur ausgewählte Werte“. Jede gespeicherte Auswahl erzeugt genau ein Topic. Zwei ausgewählte Reifendrücke ergeben beispielsweise:

- `porsche2lox/taycan/tire_pressure_front_left` → Druckzahl in **bar**
- `porsche2lox/taycan/tire_pressure_front_right` → Druckzahl in **bar**

Es gibt dabei keine zusätzlichen Verfügbarkeits-/Diagnose-/Heartbeat-Themen, keine parallelen JSON-Kopien und keine Katalog-Löschserie beim Start. Bei fehlenden oder ungültigen Daten wird `null` gesendet, niemals eine erfundene Null als Druckwert. Die einfache Ausgabe überträgt die zuletzt vom Fahrzeug gemeldeten Werte auch bei unbekanntem oder hohem Messalter; sie behauptet keine neue Fahrzeugmessung. Die normale Anzeige in PLX zeigt weiterhin Datenalter und Status. Weitere strukturierte Parameter werden jeweils als eine JSON-Nachricht am eigenen Parameter-Topic gesendet. MQTT-Abonnement: `<Präfix>/#`.

„Erweiterte Ausgabeoptionen“ enthält bei Bedarf das bisherige ausführliche Format. Vorhandene Installationen ohne Formatangabe behalten ihre bisherigen Topics. Eine bewusste Formatumstellung entfernt einmal die tatsächlich bekannten alten Themen der gespeicherten Auswahl einschließlich alter Überwachungsthemen. Beim Abwählen wird nur das betroffene vorher gewählte einfache Topic entfernt; andere Katalogparameter werden nicht angefasst. Die folgende ausführliche Themenbeschreibung gilt nur für das ausführliche Format.

Im einfachen Format enthält die XML-/CSV-Vorlage nur die ausgewählten Werte. Die alte Auswahl „Hauptwerte + Überwachung“ ist dann ausgeblendet. Empfänger sehen bei fehlenden Daten `null`; Alter und Verbindungszustand sind ohne zusätzliche Themen ausschließlich in PLX ersichtlich.

PLX → MQTT-Broker → LoxBerry MQTT Gateway → virtuelle Eingänge im Miniserver.

Das Plugin verändert keine Gateway-Einstellungen oder Miniserver-Programme automatisch. Unter **Loxone** lassen sich eine XML-Vorlage für virtuelle UDP-Eingänge und eine CSV-Zuordnung herunterladen. Standardmäßig enthält die Vorlage nur ausgewählte Hauptwerte und Überwachung (bei vier Hauptwerten 17 Eingänge). Optional kann die gesamte gespeicherte Parameterauswahl exportiert werden. Der XML-Import in der tatsächlichen Loxone-Config-Version und die Miniserver-Verknüpfung müssen vor Ort geprüft werden.

## Empfohlener Einstieg

1. Fahrzeug auswählen, Status abrufen und die gewünschte MQTT-Datenauswahl speichern.
2. Im Plugin unter Loxone Exportumfang **Hauptwerte + Überwachung** wählen; UDP-Port an den Port des MQTT Gateways anpassen (Vorgabe 11883). Optional die Absender-IP des MQTT-Gateways als Filter angeben. Gemeint ist das Gateway, das UDP an den Miniserver sendet; dieses muss nicht auf LoxBerry laufen.
3. Im MQTT Gateway den gewünschten Miniserver sowie UDP-Übertragung auf denselben Port einrichten. Für das Standardpräfix genügt ein einziges Abonnement: `porsche2lox/#`. Es empfängt alle veröffentlichten PLX-Nachrichten. Welche Fahrzeugparameter veröffentlicht werden, steuert die gespeicherte Datenauswahl in PLX.
4. **Loxone-XML herunterladen**, als Vorlage für virtuelle UDP-Eingänge in Loxone Config importieren, Sender/Port prüfen und die gewünschten Eingänge verbinden. Falls bereits ein Gateway-UDP-Eingang auf diesem Port existiert, die benötigten Befehle dort übernehmen.
5. Datenfreigaben und Heartbeat mit den Automatiken verknüpfen; die Vorlage übernimmt diese Logik nicht automatisch.

Die Befehlserkennungen entsprechen `MQTT:\i<topic>=\i\v`. Grundlage sind die geprüften Funktionen `build_udp_name` und `send_udp_bundled` des installierten LoxBerry-4-Gateways sowie `LoxBerry::IO::msudp_send`: Topicnamen mit Schrägstrichen und UDP-Pakete `MQTT: topic=wert ...`. Das Gateway bündelt selbst; kein zusätzlicher Sammelstring nötig. Die XML-Datei enthält `VirtualInUdp`, `Info templateType=1` und `VirtualInUdpCmd`, UTF-8 BOM und CRLF. Alle numerischen Eingänge bleiben analog konfiguriert, auch 0/1-Signale.

Die vollständige Auswahl einschließlich Fahrt-/Historiengruppen kann sehr viele Eingänge erzeugen (Testfahrzeug mit voller Auswahl: über 1500). Dafür vorher Parameter gezielt abwählen. Das Abonnement `<Präfix>/#` bleibt unabhängig vom Exportumfang gleich. Reine Texte sind in der CSV/MQTT verfügbar, aber nicht in der numerischen UDP-Vorlage; dafür sind gegebenenfalls HTTP-Texteingänge erforderlich. Der gewählte Exportumfang ändert nicht die gespeicherte Versand-Auswahl.

## Beispiel

Präfix `porsche2lox`, Fahrzeugname `taycan`: Abonnement `porsche2lox/#` im Gateway aktivieren und folgende Werte zuordnen:

| Topic-Endung unter `porsche2lox/taycan/` | Typ / Einheit | Bedeutung |
|---|---|---|
| soc | analog / % | Akkustand |
| range_km | analog / km | Elektrische Reichweite |
| target_soc | analog / % | Explizit gemeldetes Ladeziel |
| direct_charge_enabled | digital | Direktlademodus; kein Ladestatus |
| data_valid | digital | API erfolgreich und Batteriemessalter bekannt/zulässig |
| soc_available, range_km_available, target_soc_available, direct_charge_enabled_available | digital | Einzelwert vorhanden |
| api_ok | digital | Letzter Cloud-Abruf erfolgreich |
| auth_required | digital | Wiederanmeldung nötig |
| error_code | analog | 0=kein Abruffehler, 1=Verbindung, 2=Daten, 3=Anmeldung, 4=Rate Limit, 6=Zugriff gesperrt |
| data_age_s | analog / s | Alter des Batteriemesswerts |
| age_known | digital | Messalter bekannt |
| measurement_epoch | analog / Unixzeit | Batteriemesszeit |
| last_fetch_epoch | analog / Unixzeit | Letzter erfolgreicher Cloud-Abruf |

Der MQTT-Übertragungsfehler (Code 5 in der Weboberfläche) kann bei ausgefallenem Broker nicht zuverlässig über denselben Broker gemeldet werden.

## Freigabe in Loxone

1. `porsche2lox/heartbeat` als Unixzeit empfangen. Eine Wertänderung setzt einen 180-Sekunden-Watchdog zurück. Nach Ablauf gilt die gesamte Integration als ungültig. Nach Miniserver-Neustart zunächst ungültig, bis ein neuer Heartbeat eingetroffen ist.
2. Beispiel SoC-Freigabe: `Watchdog_OK UND data_valid UND soc_available`.
3. Für Reichweite entsprechend `range_km_available`, für Ladeziel `target_soc_available` ergänzen.
4. Ohne Freigabe letzten Wert allenfalls ausgegraut anzeigen; ihn nicht zur Automatikfreigabe verwenden. Unbekannte Werte niemals in 0 umdeuten.

Wenn die Loxone-Eingangsverarbeitung einen Reset nur bei Wertänderung erlaubt, ist Unixzeit geeignet, da sie jede Minute wechselt. Bei Retained-Replay nach einem Neustart müssen alte Heartbeats anhand ihres Zeitstempels verworfen werden. Ein bloßer Empfangsimpuls auf eine alte retained-Nachricht beweist keine Betriebsbereitschaft.

Die MQTT-Nachrichten haben QoS 1 und retain=true. Ein Update ist kein atomarer MQTT-Datensatz. PLX sendet zunächst data_valid=0, dann Messwerte und Verfügbarkeitsflags, zuletzt die neue Freigabe. Bei Verwendung einer Automatik sollte die Freigabe im Miniserver kurz verzögert und mit dem Watchdog verknüpft werden.

Cloud-Daten dienen der Anzeige und langsamen Planung. Eine schnelle PV-Laderegelung gehört an die lokale Wallbox-/Energiemanagement-Anbindung.

## Erweiterte Statusparameter

Zusätzlich zu den bisherigen flachen Fahrzeugwerten gibt es 80 Katalogparameter unter `porsche2lox/<alias>/parameters/<parameter>/`. `value` enthält JSON (Objekt, Liste oder Einzelwert), `available` meldet die Verfügbarkeit, `data_valid` die eigene Alters-/Abrufprüfung und `measurement_epoch` den eigenen Messzeitpunkt. Fehlende Parameter löschen ihren retained-Wert. Für Automatikfreigaben dieser Parameter das jeweilige `available` UND `data_valid` sowie Heartbeat/API-Überwachung nutzen. Das globale `data_valid` bleibt die Freigabe für den Batteriemesswert und ersetzt keine Prüfung der anderen Messzeitpunkte. Zusätzlich werden Einzelwerte unter `porsche2lox/<alias>/fields/<parameter>/<feldpfad>/value` und `/available` veröffentlicht. Zahlen bleiben Zahlen, echte Booleans werden 0/1, Zeitstempel mit Zeitzone werden Unixzeit. Klar bekannte Zustände werden dokumentiert als 0/1 umgesetzt (open/locked/on/active/connected=1, Gegenwert=0); unbekannte Texte werden nicht als 0 geraten. Text bleibt per MQTT erhalten und wird von der numerischen XML ausgelassen. Bekannte Feldpfade bleiben gespeichert, damit verschwundene Werte mit leerem retained-Wert und available=0 entfernt werden können. Die bestehenden JSON-Themen bleiben kompatibel erhalten; auch diese sind im gemeinsamen Abonnement `porsche2lox/#` enthalten. Die XML-Eingänge werten nur ihre jeweilige Befehlserkennung aus. CSV enthält Topic, Beschreibung, Einheit, Typ und Befehlserkennung. Die Ende-zu-Ende-Prüfung mit einem Miniserver steht noch aus.

## Datenauswahl für MQTT

Im Tab „Loxone“ unter „Welche Daten an Loxone senden?“ Hauptwerte und einzelne Detailparameter anhaken und separat speichern. „Alle auswählen“/„Keine auswählen“ gelten für die vier Hauptwerte und 80 Detailparameter. Die Auswahl gilt für alle eingerichteten Fahrzeuge; in der Oberfläche bleiben sämtliche verfügbaren Daten sichtbar. Heartbeat, API-/Fehlerstatus und Freigabesignale bleiben zur Überwachung aktiv. Bestehende Installationen behalten zunächst ihren bisherigen Versandumfang. Abgewählte retained-Daten und zugehörige Parameterflags werden auf dem bisherigen Broker gelöscht; bei Brokerfehler wird die Speicherung abgebrochen. War MQTT beim Abwählen deaktiviert, werden ausgeschlossene Topics beim nächsten Einschalten bereinigt. CSV enthält nur ausgewählte Nutzwerte und notwendige Überwachungsthemen.
