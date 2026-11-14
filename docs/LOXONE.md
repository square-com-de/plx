# Loxone-Anbindung

## Einfache MQTT-Ausgabe

Für neue Installationen gilt „Nur ausgewählte Werte“. Jede gespeicherte Auswahl erzeugt genau ein Topic. Zwei ausgewählte Reifendrücke ergeben beispielsweise:

- `porsche2lox/taycan/tire_pressure_front_left` → Druckzahl in **bar**
- `porsche2lox/taycan/tire_pressure_front_right` → Druckzahl in **bar**

Es gibt dabei keine zusätzlichen Verfügbarkeits-/Diagnose-/Heartbeat-Themen, keine parallelen JSON-Kopien und keine Katalog-Löschserie beim Start. Bei fehlenden oder unbrauchbaren Druckdaten wird `null` gesendet, niemals eine erfundene Null als Druckwert. Die einfache Ausgabe überträgt die zuletzt vom Fahrzeug gemeldeten Werte auch bei unbekanntem oder hohem Messalter; sie behauptet keine neue Fahrzeugmessung. Die normale Anzeige in PLX zeigt weiterhin Datenalter und Status. Weitere strukturierte Parameter werden jeweils als eine JSON-Nachricht am eigenen Parameter-Topic gesendet. MQTT-Abonnement: `<Präfix>/#`.

„Erweiterte Ausgabeoptionen“ enthält bei Bedarf das bisherige ausführliche Format. Vorhandene Installationen ohne Formatangabe behalten ihre bisherigen Topics. Eine bewusste Formatumstellung entfernt einmal die tatsächlich bekannten alten Themen der gespeicherten Auswahl einschließlich alter Überwachungsthemen. Beim Abwählen wird nur das betroffene vorher gewählte einfache Topic entfernt; andere Katalogparameter werden nicht angefasst. Die folgende ausführliche Themenbeschreibung gilt nur für das ausführliche Format.

Im einfachen Format enthält die XML-/CSV-Vorlage nur die ausgewählten Werte. Die alte Auswahl „Hauptwerte + Überwachung“ ist dann ausgeblendet. Empfänger sehen bei fehlenden Daten `null`; Alter und Verbindungszustand sind ohne zusätzliche Themen ausschließlich in PLX ersichtlich.

PLX → MQTT-Broker → LoxBerry MQTT Gateway → virtuelle Eingänge im Miniserver.

Das Plugin verändert keine Gateway-Einstellungen oder Miniserver-Programme automatisch. Unter **Loxone** lassen sich eine XML-Vorlage für virtuelle UDP-Eingänge und eine CSV-Zuordnung herunterladen. Im einfachen Format enthält die Vorlage ausschließlich die ausgewählten Werte. Nur im ausführlichen Format ist „Hauptwerte + Überwachung“ der voreingestellte Exportumfang (bei vier Hauptwerten 17 Eingänge); dort kann optional die gesamte gespeicherte Parameterauswahl exportiert werden. Der XML-Import in der tatsächlichen Loxone-Config-Version und die Miniserver-Verknüpfung müssen vor Ort geprüft werden.

## Empfohlener Einstieg: zwei Reifendrücke

1. Fahrzeug auswählen, Status abrufen. Unter Loxone nur die zwei gewünschten Reifendrücke wählen und speichern. **Einfaches Format** verwenden; die gesamte Parameterliste in der Oberfläche darf weiter sichtbar bleiben.
2. MQTT auf den tatsächlichen **Broker** richten, nicht einen reinen HTTPS-Webproxy. Broker-Port/TLS prüfen. Der Broker muss vom Container aus erreichbar sein; siehe [Netzwerkprüfung](MANUAL.de.md#mqtt-und-loxone).
3. Im MQTT Gateway genau ein Abonnement `porsche2lox/#` anlegen (bei eigenem Präfix entsprechend ändern). Die Datenauswahl in PLX bestimmt den Versand, nicht das Abonnement. Zwei Druckwerte ergeben zwei numerische Topics in bar, keine Heartbeats oder Freigabethemen im einfachen Format.
4. Optional XML für diese Auswahl herunterladen. Im einfachen Format gibt es keinen zusätzlichen Exportumfang „Hauptwerte + Überwachung“. Gateway-UDP-Port und virtuellen UDP-Eingang im Miniserver gleich einstellen (Exportvorgabe 11883). Das ist **kein** MQTT-Broker-TCP-Port.
5. Der optionale IP-Filter meint den **UDP-Sender: MQTT-Gateway-Host aus Sicht des Miniservers**. Er ist nicht automatisch PLX, Broker, LoxBerry oder Miniserver. Im Zweifel leer lassen; falscher Filter kann Empfang verhindern.
6. XML in Loxone Config als virtuelle UDP-Eingangsvorlage importieren und die zwei Werte zuordnen. Bei vorhandenem Gateway-Eingang auf demselben Port Befehle dort übernehmen. `null` bedeutet kein Druckwert; ein alter Retained-Wert beweist keine neue Messung. Zahlen und Aktualität bis zum Miniserver prüfen; XML-Export allein ist keine Ende-zu-Ende-Abnahme.

**Optionales ausführliches Format:** Nur bei Bedarf unter erweiterten Ausgabeoptionen aktivieren. Dann beeinflusst „Hauptwerte + Überwachung“ beziehungsweise „alle gespeicherten Parameter“ nur die XML-Vorlage, nicht MQTT-Versand oder Abonnement. Die folgenden Überwachungs-/Detailbeschreibungen gelten ausschließlich dafür. Für einen frischeabhängigen Ablauf Heartbeat, jeweiliges `available` und `data_valid` tatsächlich auswerten; im einfachen Format existieren diese Topics nicht.

Die Befehlserkennungen entsprechen `MQTT:\i<topic>=\i\v`. Grundlage sind die geprüften Funktionen `build_udp_name` und `send_udp_bundled` des installierten LoxBerry-4-Gateways sowie `LoxBerry::IO::msudp_send`: Topicnamen mit Schrägstrichen und UDP-Pakete `MQTT: topic=wert ...`. Das Gateway bündelt selbst; kein zusätzlicher Sammelstring nötig. Die XML-Datei enthält `VirtualInUdp`, `Info templateType=1` und `VirtualInUdpCmd`, UTF-8 BOM und CRLF. Alle numerischen Eingänge bleiben analog konfiguriert, auch 0/1-Signale.

Die vollständige Auswahl einschließlich Fahrt-/Historiengruppen kann sehr viele Eingänge erzeugen (Testfahrzeug mit voller Auswahl: über 1500). Dafür vorher Parameter gezielt abwählen. Das Abonnement `<Präfix>/#` bleibt unabhängig vom Exportumfang gleich. Reine Texte sind in der CSV/MQTT verfügbar, aber nicht in der numerischen UDP-Vorlage; dafür sind gegebenenfalls HTTP-Texteingänge erforderlich. Der gewählte Exportumfang ändert nicht die gespeicherte Versand-Auswahl.

## Beispiel im ausführlichen Format

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


## MQTT2LOX direkt: Dienst und Datenaktualität überwachen

Diese Anleitung gilt für **Ausführliche Daten + Diagnose / Detailed data + diagnostics**. Im einfachen Format fehlen diese Überwachungsthemen. Die Ausgabeoption bewusst in PLX speichern; das Abonnieren eines Topics erzeugt keine Nachrichten. Präfix `porsche2lox` und Fahrzeugalias `taycan` in allen Beispielen durch die eigene gespeicherte Konfiguration ersetzen. Alte `porsche/taycan/...`-Topics nicht mit PLX mischen.

### Direkter MQTT-Empfang oder UDP-Gateway?

- **MQTT2LOX direkt:** Als Subscribe-Topic ausschließlich beispielsweise `porsche2lox/taycan/error_code` eintragen. Den Nachrichteninhalt numerisch auswerten. Keine UDP-Befehlserkennung erforderlich. Die konkrete Einstellung der numerischen Auswertung hängt von der verwendeten MQTT2LOX-Version ab.
- **LoxBerry MQTT Gateway → UDP:** Hier gehört `MQTT:\i<topic>=\i\v` in die **Befehlserkennung eines virtuellen UDP-Eingangsbefehls**. Die exportierte XML kann diese Zuordnung vorbereiten. Diese Zeichenfolge gehört nicht ins MQTT-Abonnement.

### Anschlüsse am Statusbaustein

| Topic / Signal | Anschluss | Bedeutung |
|---|---|---|
| `porsche2lox/taycan/api_ok` | I1 | 1 = letzter Porsche-Abruf erfolgreich |
| `porsche2lox/taycan/error_code` | I2 | 0 = kein Abruffehler |
| `porsche2lox/taycan/auth_required` | I3 | 1 = erneute Anmeldung erforderlich |
| Berechnetes Heartbeat-Alter, siehe unten | I4 | Sekunden seit Heartbeat |
| `porsche2lox/taycan/data_valid` | I5 | Batterie-Messzeit bekannt, zulässiges Alter und Abruf erfolgreich |

Alle Nachrichten als Zahlen empfangen; insbesondere den Heartbeat nicht auf 0/1 begrenzen. Fehlende oder unlesbare Nachrichten nicht als Erfolg behandeln.

### Heartbeat anhand des Zeitstempels prüfen

Einen **Formelbaustein** „PLX Heartbeat-Alter“ anlegen:

- I1: Loxone-Zeitfunktion **Unix Timestamp** (UTC).
- I2: numerischer Inhalt von `porsche2lox/heartbeat` — global, ohne Fahrzeugalias.
- Formel: `I1-I2`.
- Ausgang R: an I4 des Statusbausteins.

Die aktuelle Zeit muss fortlaufend aktualisiert werden, auch wenn keine MQTT-Nachricht mehr eintrifft. PLX veröffentlicht im ausführlichen Modus ungefähr jede Minute; als Ausfallgrenze **180 Sekunden** verwenden. Mehr als 30 Sekunden Zukunftsabweichung (`I4 < -30`) als Zeitfehler behandeln. Beide Systemuhren synchronisieren.

Ein bloßer Empfangsimpuls mit Nachlaufzeit reicht nicht: Der Broker kann alte retained-Nachrichten nach einem Neustart erneut liefern. Die Zeitdifferenz lässt einen alten Zeitstempel alt bleiben. Ohne empfangenen Heartbeat keine Freigabe; Grundzustand „Status wird geprüft“, Statuswert 0. Für eine strengere Neustartfreigabe zusätzlich einen nach Programmstart wechselnden Heartbeat verlangen.

### Statusbedingungen

Im Statusbaustein folgende Priorität abbilden. Bei mehreren zutreffenden Bedingungen muss die höher stehende Meldung gewinnen; falls die verwendete Config-Version anders priorisiert, nachrangige Bedingungen entsprechend verriegeln.

| Priorität | Bedingung | Text | Statuswert |
|---|---|---|---|
| 1 | Heartbeat fehlt oder I4 > 180 | ❌ PLX nicht erreichbar | 0 |
| 2 | I4 < -30 | ⚠️ Zeitabweichung prüfen | 0 |
| 3 | I3 = 1 | 🔑 Porsche-Anmeldung erforderlich | 0 |
| 4 | I1 = 0 | ⚠️ Porsche-Abruf fehlgeschlagen | 0 |
| 5 | I2 ≠ 0 | ⚠️ Porsche-Fehler: `<v2>` | 0 |
| 6 | I5 = 0 | ⚠️ Fahrzeugdaten veraltet oder Messzeit unbekannt | 0 |
| 7 | Alle benötigten Signale bekannt; -30 ≤ I4 ≤ 180; I1 = 1; I2 = 0; I3 = 0; I5 = 1 | ✅ Porsche Connect OK · Batteriedaten aktuell | 1 |

Die letzte Zeile ausdrücklich als vollständige UND-Bedingung umsetzen, nicht als pauschalen Standardtext. Unbekannte Zustände bleiben gesperrt. Für einzelne Werte zusätzlich deren `*_available` verlangen. Bei automatischen Schaltungen die Freigabe kurz verzögern, weil MQTT-Nachrichten nicht atomar eintreffen.

**Geltungsbereich:** Das fahrzeugweite `data_valid` bezieht sich auf die Batterie. Es bescheinigt weder frischen Reifendruck noch das Alter aller übrigen Werte. Für Detailparameter zusätzlich `parameters/<parameter>/available`, `parameters/<parameter>/data_valid` und die Verfügbarkeit des betreffenden Feldes prüfen. Ein frischer Cloud-Abruf ist keine neue Fahrzeugmessung. „Dienst erreichbar“ bestätigt den laufenden Veröffentlichungsweg, nicht die aktuelle Erreichbarkeit der Porsche-API; dafür dienen I1–I3.

### Abnahme vor Verwendung

1. Normalbetrieb: Heartbeat-Alter typischerweise 0–60 Sekunden; Status nur bei gültigen Daten OK.
2. Auf einem separaten Testsystem PLX stoppen: nach mehr als 180 Sekunden kein OK mehr, auch wenn Messwerte retained bleiben.
3. Alten retained-Heartbeat nach Miniserver-/MQTT-Neustart einspielen: keine falsche Freigabe.
4. Mit synthetischen Testdaten `auth_required=1`, Abruffehler und `data_valid=0` prüfen: jeweils passende Meldung, Statuswert 0.
5. Fehlende Messwerte und unbekannte Messzeiten prüfen; niemals in gültige Nullwerte umdeuten.

Dies ist eine Konfigurationsanleitung, kein Nachweis einer bereits erfolgten Ende-zu-Ende-Abnahme am eigenen Miniserver. Fehlerfälle nur im separaten Testsystem beziehungsweise isolierten Testpräfix erzeugen.

Offizielle Bausteinreferenzen: [Zeitfunktionen](https://www.loxone.com/dede/kb/zeitfunktionen/), [Formel](https://www.loxone.com/dede/kb/formel/), [Status](https://www.loxone.com/dede/kb/status-baustein/).

### English: direct MQTT2LOX monitoring

Use **Detailed data + diagnostics**; simple output does not publish these signals. Replace prefix and alias with your saved configuration. With direct MQTT2LOX, subscribe to the plain topic and decode the payload as a number. The recognition string `MQTT:\i<topic>=\i\v` is only for a virtual UDP input command behind an MQTT-to-UDP gateway.

Connect `api_ok` to status I1, `error_code` to I2, `auth_required` to I3 and vehicle `data_valid` to I5, all below `porsche2lox/taycan/`. For I4, use a Formula block: I1 = continuously updated Loxone **Unix Timestamp**, I2 = numeric global `porsche2lox/heartbeat`, formula `I1-I2`, output R = heartbeat age in seconds.

Give faults priority: missing heartbeat or age >180 s → offline; age <−30 s → clock error; auth_required=1 → sign in again; api_ok=0 → fetch failed; error_code≠0 → report error; data_valid=0 → battery data stale or measurement time unknown. OK requires all inputs known, age within −30…180 s, api_ok=1, error_code=0, auth_required=0 and data_valid=1. Default/unknown state must remain invalid (status value 0); only OK uses 1. Add each measurement's availability before enabling automation.

Vehicle data_valid covers the battery measurement, not tire pressure or every other parameter. For detail parameters also check their own availability/validity and field availability. A retained message is not evidence of a live service; compare its timestamp. For stricter startup behaviour require a changing heartbeat after program start. Synchronize both clocks. Test outage, stale retained replay, authentication failure and stale/missing data on an isolated test system before relying on this logic. This guide does not claim completed Miniserver acceptance.

## Freigabe in Loxone (nur ausführliches Format)

1. `porsche2lox/heartbeat` als Unixzeit empfangen. Eine Wertänderung setzt einen 180-Sekunden-Watchdog zurück. Nach Ablauf gilt die gesamte Integration als ungültig. Nach Miniserver-Neustart zunächst ungültig, bis ein neuer Heartbeat eingetroffen ist.
2. Beispiel SoC-Freigabe: `Watchdog_OK UND data_valid UND soc_available`.
3. Für Reichweite entsprechend `range_km_available`, für Ladeziel `target_soc_available` ergänzen.
4. Ohne Freigabe letzten Wert allenfalls ausgegraut anzeigen; ihn nicht zur Automatikfreigabe verwenden. Unbekannte Werte niemals in 0 umdeuten.

Wenn die Loxone-Eingangsverarbeitung einen Reset nur bei Wertänderung erlaubt, ist Unixzeit geeignet, da sie jede Minute wechselt. Bei Retained-Replay nach einem Neustart müssen alte Heartbeats anhand ihres Zeitstempels verworfen werden. Ein bloßer Empfangsimpuls auf eine alte retained-Nachricht beweist keine Betriebsbereitschaft.

Die MQTT-Nachrichten haben QoS 1 und retain=true. Ein Update ist kein atomarer MQTT-Datensatz. PLX sendet zunächst data_valid=0, dann Messwerte und Verfügbarkeitsflags, zuletzt die neue Freigabe. Bei Verwendung einer Automatik sollte die Freigabe im Miniserver kurz verzögert und mit dem Watchdog verknüpft werden.

Cloud-Daten dienen der Anzeige und langsamen Planung. Eine schnelle PV-Laderegelung gehört an die lokale Wallbox-/Energiemanagement-Anbindung.

## Erweiterte Statusparameter (nur ausführliches Format)

Zusätzlich zu den bisherigen flachen Fahrzeugwerten gibt es 80 Katalogparameter unter `porsche2lox/<alias>/parameters/<parameter>/`. `value` enthält JSON (Objekt, Liste oder Einzelwert), `available` meldet die Verfügbarkeit, `data_valid` die eigene Alters-/Abrufprüfung und `measurement_epoch` den eigenen Messzeitpunkt. Fehlende Parameter löschen ihren retained-Wert. Für Automatikfreigaben dieser Parameter das jeweilige `available` UND `data_valid` sowie Heartbeat/API-Überwachung nutzen. Das globale `data_valid` bleibt die Freigabe für den Batteriemesswert und ersetzt keine Prüfung der anderen Messzeitpunkte. Zusätzlich werden Einzelwerte unter `porsche2lox/<alias>/fields/<parameter>/<feldpfad>/value` und `/available` veröffentlicht. Zahlen bleiben Zahlen, echte Booleans werden 0/1, Zeitstempel mit Zeitzone werden Unixzeit. Klar bekannte Zustände werden dokumentiert als 0/1 umgesetzt (open/locked/on/active/connected=1, Gegenwert=0); unbekannte Texte werden nicht als 0 geraten. Text bleibt per MQTT erhalten und wird von der numerischen XML ausgelassen. Bekannte Feldpfade bleiben gespeichert, damit verschwundene Werte mit leerem retained-Wert und available=0 entfernt werden können. Die bestehenden JSON-Themen bleiben kompatibel erhalten; auch diese sind im gemeinsamen Abonnement `porsche2lox/#` enthalten. Die XML-Eingänge werten nur ihre jeweilige Befehlserkennung aus. CSV enthält Topic, Beschreibung, Einheit, Typ und Befehlserkennung. Die Ende-zu-Ende-Prüfung mit einem Miniserver steht noch aus.

## Datenauswahl für MQTT

Im Tab „Loxone“ unter „Welche Daten an Loxone senden?“ Hauptwerte und einzelne Detailparameter anhaken und separat speichern. „Alle auswählen“/„Keine auswählen“ gelten für die vier Hauptwerte und 80 Detailparameter. Die Auswahl gilt für alle eingerichteten Fahrzeuge; in der Oberfläche bleiben sämtliche verfügbaren Daten sichtbar. Nur im ausführlichen Format bleiben Heartbeat, API-/Fehlerstatus und Freigabesignale zur Überwachung aktiv. Bestehende Installationen behalten zunächst ihren bisherigen Versandumfang. Abgewählte retained-Daten und zugehörige Parameterflags werden auf dem bisherigen Broker gelöscht; bei Brokerfehler wird die Speicherung abgebrochen. War MQTT beim Abwählen deaktiviert, werden ausgeschlossene Topics beim nächsten Einschalten bereinigt. CSV enthält im einfachen Format nur ausgewählte Nutzwerte; notwendige Überwachungsthemen kommen ausschließlich im ausführlichen Format hinzu.

Runtime-/Supportgrenzen und offene unabhängige Abnahme: [Installation](../INSTALL.de.md), [Fehleraufarbeitung](INSTALLATION-LESSONS.de.md) und [Gate #1](https://github.com/square-com-de/plx/issues/1).
