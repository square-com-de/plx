(() => {
  'use strict';
  // Presentation-only translations: MQTT keys, saved values and API payloads stay unchanged.
  const messages = {
  "Bitte PLX über HTTPS öffnen. Anmeldung und Speichern sind über HTTP gesperrt.": "Please open PLX over HTTPS. Sign-in and saving are blocked over HTTP.",
  "Einfaches MQTT sendet den zuletzt gemeldeten Wert ohne Altersfreigabe; fehlende Werte sind null. Das Messalter siehst du in PLX.": "Simple MQTT sends the last reported value without a freshness signal; missing values are null. Check measurement age in PLX.",
  "Im ausführlichen MQTT-Format melden data_valid und available die Freigabe. Auch ein neuer Cloud-Abruf kann alte Fahrzeugdaten liefern.": "Detailed MQTT provides data_valid and available signals. A new cloud fetch can still return old vehicle data.",
  "Übersicht": "Overview",
  "Fahrzeugdaten": "Vehicle data",
  "Porsche-Konto": "Porsche account",
  "Einrichtung": "Setup",
  "Dein Porsche x Loxone in Deinem intelligenten Zuhause.": "Your Porsche x Loxone in your smart home.",
  "Fahrzeugstatus": "Vehicle status",
  "Gespeicherte Porsche-Daten. Messalter und Abrufzeit werden getrennt angezeigt.": "Saved Porsche data. Measurement age and fetch time are shown separately.",
  "Status abrufen": "Refresh status",
  "Noch nicht eingerichtet": "Not set up",
  "MQTT-Ausgabe": "MQTT output",
  "Statusabruf": "Status polling",
  "Deaktiviert": "Disabled",
  "Nicht angemeldet": "Signed out",
  "Sitzung gespeichert": "Session saved",
  "Angemeldet": "Signed in",
  "CAPTCHA erforderlich": "CAPTCHA required",
  "Anmeldung abgelaufen": "Session expired",
  "Anmeldung fehlgeschlagen": "Sign-in failed",
  "Anmeldung erforderlich": "Sign-in required",
  "Zugriff gesperrt": "Access blocked",
  "Unbekannt": "Unknown",
  "Verbunden": "Connected",
  "Porsche Connect verbunden": "Porsche Connect connected",
  "Porsche Connect · Sitzung gespeichert": "Porsche Connect · session saved",
  "Porsche Connect · wird geprüft": "Porsche Connect · checking",
  "Mit Porsche Connect verbunden": "Connected to Porsche Connect",
  "Porsche-Sitzung gespeichert": "Porsche session saved",
  "Mit Porsche verbinden": "Connect to Porsche",
  "Du bist angemeldet. Keine erneute Anmeldung nötig – die Sitzung wird automatisch erneuert.": "You are signed in. No need to sign in again — your session renews automatically.",
  "Keine erneute Anmeldung nötig. Mit „Fahrzeuge laden“ kannst du die gespeicherte Sitzung prüfen.": "No need to sign in again. Use “Load vehicles” to check your saved session.",
  "Melde dich mit deiner Porsche-ID an. Das Passwort wird nicht dauerhaft gespeichert.": "Sign in with your Porsche ID. Your password is not stored permanently.",
  "Verbindung zum Plugin wird hergestellt …": "Connecting to PLX …",
  "Verbindungsstatus wird geprüft.": "Checking connection status.",
  "Verbunden · Übertragung bestätigt": "Connected · delivery confirmed",
  "Verbindung fehlgeschlagen": "Connection failed",
  "Wartet auf Übertragung": "Waiting to send",
  "Automatik aus · manueller Abruf möglich": "Automatic polling off · manual refresh available",
  "Wartet auf Anmeldung": "Waiting for sign-in",
  "Bereit": "Ready",
  "Noch kein Abruf": "Not fetched yet",
  "Messalter unbekannt": "Measurement age unknown",
  "Vor weniger als 1 Minute gemessen": "Measured less than 1 minute ago",
  "Daten gültig": "Data valid",
  "Daten nicht freigegeben": "Data not approved",
  "Reichweite": "Range",
  "Ladeziel": "Charge target",
  "Batterie": "Battery",
  "unbekannt": "unknown",
  "aktiviert": "enabled",
  "deaktiviert": "disabled",
  "Bitte zuerst ein Fahrzeug in der Einrichtung auswählen und speichern.": "Select a vehicle in Setup and save it first.",
  "Porsche ist verbunden. Bitte die Fahrzeugauswahl noch speichern.": "Porsche is connected. Please save your vehicle selection.",
  "Bitte im Porsche-Konto Fahrzeuge laden und auswählen.": "Load and select vehicles in Porsche account.",
  "Fahrzeug auswählen und speichern": "Select and save vehicle",
  "Melde dich bei Porsche an und wähle dein Fahrzeug in der Einrichtung aus.": "Sign in to Porsche and select your vehicle in Setup.",
  "Bestehende Taycan-App: PLX nutzt eine eigene Sitzung und eigene Topics. Aktiviere die neue Integration erst nach der Einrichtung.": "Existing Taycan app: PLX uses its own session and topics. Enable the new integration after setup.",
  "Alle Statusparameter mit Verfügbarkeit und eigenem Messalter. Für Details einen Bereich aufklappen.": "All status parameters with availability and measurement age. Expand a category for details.",
  "Fahrzeugdaten durchsuchen": "Search vehicle data",
  "z. B. Reifendruck, Laden, Kilometer …": "e.g. tire pressure, charging, mileage …",
  "Anzeigen": "Show",
  "Alle Parameter": "All parameters",
  "Nur verfügbar": "Available only",
  "Aktuelle Werte": "Current values",
  "Veraltete Werte": "Stale values",
  "Nicht verfügbar": "Unavailable",
  "Für MQTT ausgewählt": "Selected for MQTT",
  "Zurücksetzen": "Reset",
  "Suche in Namen, technischen Kennungen und Werten": "Search names, technical identifiers and values",
  "Keine passenden Parameter. Suchbegriff oder Filter ändern.": "No matching parameters. Change your search or filter.",
  "Weiter zur Einrichtung →": "Continue to setup →",
  "Im nächsten Schritt Fahrzeuge auswählen und Einstellungen speichern.": "Next, select vehicles and save your settings.",
  "Porsche-ID (E-Mail)": "Porsche ID (email)",
  "Passwort": "Password",
  "Bei Porsche anmelden": "Sign in to Porsche",
  "Die Anmeldung erfordert HTTPS. Porsche kann zur Bestätigung ein CAPTCHA anzeigen.": "Sign-in requires HTTPS. Porsche may ask you to complete a CAPTCHA.",
  "Sitzung & Verbindung": "Session & connection",
  "Andere Porsche-ID anmelden": "Use another Porsche ID",
  "Nur die Sitzungstokens werden geschützt auf deinem LoxBerry gespeichert. Sie werden automatisch erneuert.": "Only session tokens are securely stored on your LoxBerry. They renew automatically.",
  "Nur die Sitzungstokens werden geschützt in deinem eigenen PLX-Datenspeicher gespeichert. Sie werden automatisch erneuert.": "Only session tokens are securely stored in your PLX data store. They renew automatically.",
  "Passwort und CAPTCHA-Kontext werden spätestens nach fünf Minuten aus dem Anmeldevorgang entfernt.": "Password and CAPTCHA context are removed from the sign-in process within five minutes.",
  "Fahrzeuge laden": "Load vehicles",
  "Abmelden & Sitzung löschen": "Sign out & delete session",
  "Porsche möchte eine Bestätigung": "Porsche needs verification",
  "Übertrage die Zeichen aus dem Bild. Der ursprüngliche Anmeldevorgang wird fortgesetzt.": "Enter the characters in the image to continue signing in.",
  "Zeichen aus dem Bild": "Characters in the image",
  "Bestätigen": "Confirm",
  "Abbrechen": "Cancel",
  "Wähle Fahrzeuge aus und lege fest, wann Daten abgerufen und weitergegeben werden.": "Choose vehicles and configure when data is fetched and shared.",
  "SCHRITT 1 · FAHRZEUGE": "STEP 1 · VEHICLES",
  "Welche Fahrzeuge möchtest du verwenden?": "Which vehicles would you like to use?",
  "Gewünschte Fahrzeuge anhaken. Danach die Einstellungen speichern.": "Select the vehicles you want, then save your settings.",
  "Bitte zuerst anmelden und Fahrzeuge laden.": "Sign in and load vehicles first.",
  "Fahrzeugauswahl und Einstellungen speichern": "Save vehicle selection and settings",
  "2. Statusabruf": "2. Status polling",
  "Automatischen Statusabruf aktivieren": "Enable automatic status polling",
  "Abfrageintervall": "Polling interval",
  "5 Minuten": "5 minutes",
  "15 Minuten · empfohlen": "15 minutes · recommended",
  "15 Minuten": "15 minutes",
  "30 Minuten": "30 minutes",
  "60 Minuten": "60 minutes",
  "1 Stunde": "1 hour",
  "6 Stunden": "6 hours",
  "24 Stunden": "24 hours",
  "Maximales Alter der Fahrzeugdaten": "Maximum vehicle data age",
  "Ältere Fahrzeugdaten werden weiter angezeigt, aber als ungültig an Loxone gemeldet. Auch ein neuer Abruf kann alte Daten liefern, wenn das Fahrzeug schläft.": "Older data remains visible but is marked invalid in detailed output. A fresh cloud request can still return old data while the vehicle is asleep.",
  "3. MQTT zu Loxone": "3. MQTT to Loxone",
  "MQTT-Ausgabe aktivieren": "Enable MQTT output",
  "Benutzername": "Username",
  "MQTT-Passwort": "MQTT password",
  "Leer lassen: gespeichertes Passwort behalten": "Leave empty to keep the saved password",
  "Gespeichert · leer lassen zum Beibehalten": "Saved · leave empty to keep",
  "Gespeichertes MQTT-Passwort löschen": "Delete saved MQTT password",
  "TLS mit Zertifikatsprüfung": "TLS with certificate verification",
  "Topic-Präfix": "Topic prefix",
  "Die bestehende App verwendet porsche/taycan. PLX veröffentlicht in einem eigenen Namensraum.": "The existing app uses porsche/taycan. PLX publishes in its own namespace.",
  "Docker: Broker-Adresse im Netzwerk verwenden; 127.0.0.1 bezeichnet diesen Container. PLX nutzt eigene Topics.": "Docker: use the broker’s network address; 127.0.0.1 refers to this container. PLX uses its own topics.",
  "Einstellungen speichern": "Save settings",
  "Technischer Name für Loxone/MQTT (z. B. taycan)": "Technical name for Loxone/MQTT (e.g. taycan)",
  "In Loxone verwenden": "Use in Loxone",
  "MQTT-Abonnement im LoxBerry MQTT Gateway einrichten und den virtuellen Eingängen zuordnen.": "Set up the MQTT subscription in the LoxBerry MQTT Gateway and assign virtual inputs.",
  "Welche Daten per MQTT senden?": "Which data should MQTT send?",
  "Erweiterte Ausgabeoptionen": "Advanced output options",
  "MQTT-Format": "MQTT format",
  "Nur ausgewählte Werte · einfach": "Selected values only · simple",
  "Ausführliche Daten + Diagnose": "Detailed data + diagnostics",
  "Alle auswählen": "Select all",
  "Keine auswählen": "Select none",
  "Datenauswahl speichern": "Save data selection",
  "Noch nicht gespeichert": "Not saved yet",
  "Datenauswahl gespeichert.": "Data selection saved.",
  "Hauptwerte": "Main values",
  "Akkustand (%)": "Battery level (%)",
  "Reichweite (km)": "Range (km)",
  "Ladeziel (%)": "Charge target (%)",
  "Direktlademodus": "Direct charging mode",
  "MQTT-Abonnement": "MQTT subscription",
  "Dieses eine Abonnement empfängt alle PLX-Nachrichten. Welche Fahrzeugwerte gesendet werden, bestimmst du oben mit den Häkchen. Überwachungssignale bleiben dabei.": "This subscription receives all PLX messages. Select the vehicle values to send using the checkboxes above.",
  "Exportumfang": "Export scope",
  "Hauptwerte + Überwachung · empfohlen": "Main values + monitoring · recommended",
  "Alle gespeicherten ausgewählten Parameter": "All saved selected parameters",
  "UDP-Port des MQTT Gateways": "MQTT Gateway UDP port",
  "Absender-IP des MQTT-Gateways (optional)": "MQTT Gateway source IP (optional)",
  "Leer: kein Absenderfilter": "Empty: no source filter",
  "Loxone-XML herunterladen": "Download Loxone XML",
  "Zuordnung als CSV herunterladen": "Download mapping as CSV",
  "Messwert": "Measurement",
  "Verwendung": "Purpose",
  "Einheit": "Unit",
  "Akkustand": "Battery level",
  "Elektrische Reichweite": "Electric range",
  "Aktuell": "Current",
  "Veraltet": "Stale",
  "Nicht freigegeben": "Not approved",
  "Derzeit keine Fahrzeugdaten": "No vehicle data available",
  "Keine Einträge": "No entries",
  "Kein verlässlicher Messzeitpunkt vorhanden.": "No reliable measurement timestamp available.",
  "Dieses Fahrzeug liefert diesen Parameter derzeit nicht.": "This vehicle does not currently report this parameter.",
  "Noch keine Detaildaten abgerufen. In der Übersicht „Status abrufen“ wählen.": "No detailed data yet. Choose “Refresh status” in Overview.",
  "Porsche hat kein darstellbares CAPTCHA geliefert. Anmeldung bitte neu starten.": "Porsche returned no displayable CAPTCHA. Please restart sign-in.",
  "Gespeichert. Die Fahrzeugauswahl wurde übernommen.": "Saved. Your vehicle selection has been applied.",
  "Bitte zuerst die Datenauswahl speichern.": "Please save your data selection first.",
  "Exportumfang geändert. Das MQTT-Abonnement bleibt gleich.": "Export scope changed. The MQTT subscription stays the same.",
  "Optional für Loxone: Die XML-Vorlage enthält genau die ausgewählten numerischen Werte. Für reines MQTT ist kein Export nötig.": "Optional for Loxone: the XML template contains exactly the selected numeric values. MQTT alone does not require an export.",
  "Pro Auswahl ein Topic. Reifendruck wird als Zahl in bar gesendet, ohne zusätzliche Diagnose- oder Verfügbarkeitsthemen. Gesendet wird der zuletzt gemeldete Wert; das Messalter siehst du in PLX. Fehlende Werte: null.": "One topic per selection. Tire pressure is sent as a number in bar, without extra diagnostic or availability topics. The last reported value is sent; check measurement age in PLX. Missing values: null.",
  "Nur angehakte Werte werden per MQTT verschickt. Heartbeat, Fehler- und Gültigkeitssignale bleiben zur Überwachung aktiv.": "Only checked values are sent over MQTT. Heartbeat, error and validity signals remain enabled for monitoring.",
  "PLX · Statusintegration · Unabhängiges Projekt, nicht von Porsche unterstützt.": "PLX · Status integration · Independent project, not supported by Porsche.",
  "PLX abmelden": "Sign out of PLX",
  "Ja": "Yes",
  "Nein": "No",
  "Kilometer": "Kilometers",
  "Messzeitpunkt": "Measurement time",
  "Ladeleistung": "Charging power",
  "Maximale Ladeleistung": "Maximum charging power",
  "Ladegeschwindigkeit": "Charging speed",
  "Modus": "Mode",
  "Zustand": "State",
  "Breitengrad": "Latitude",
  "Längengrad": "Longitude",
  "Reifendruck": "Tire pressure",
  "Abweichung": "Difference",
  "Druck": "Pressure",
  "Temperatur": "Temperature",
  "Zieltemperatur": "Target temperature",
  "Geöffnet": "Open",
  "Verriegelt": "Locked",
  "Eingeschaltet": "On",
  "Aktiviert": "Enabled",
  "Wert": "Value",
  "Lädt": "Charging",
  "Direktladen": "Direct charging",
  "Aus": "Off",
  "An": "On",
  "Verriegeln": "Lock",
  "Nicht eingeblendet": "Hidden",
  "Fahrzeug & Sicherheit": "Vehicle & security",
  "Batterie & Laden": "Battery & charging",
  "Weitere Fahrzeugdaten": "Other vehicle data",
  "Standort & Fahrten": "Location & trips",
  "Klima & Timer": "Climate & timers",
  "Wartung & Meldungen": "Maintenance & alerts",
  "Batteriezustand": "Battery condition",
  "Batteriemanagement": "Battery management",
  "Gesamtreichweite": "Total range",
  "Ladeleistung und Ladegeschwindigkeit": "Charging power and speed",
  "Ladevorgang": "Charging session",
  "Ladeübersicht": "Charging summary",
  "Ladeeinstellungen": "Charging settings",
  "Ladeprofile": "Charging profiles",
  "Abfahrtszeiten": "Departure times",
  "Klimatisierung": "Climate control",
  "Kilometerstand": "Odometer",
  "Standort": "Location",
  "Verriegelung": "Lock state",
  "Parkbremse": "Parking brake",
  "Parklicht": "Parking lights",
  "Fahrzeug-Zeitstempel": "Vehicle timestamp",
  "Privatsphäre": "Privacy",
  "Connect-Vertrag": "Connect contract",
  "Alarmanlage": "Alarm system",
  "Diebstahlstatus": "Theft status",
  "Zeitzone": "Time zone",
  "Tankfüllstand": "Fuel level",
  "Kraftstoffreserve": "Fuel reserve",
  "Fahrzeugmeldungen": "Vehicle alerts",
  "Wartungsprognose": "Service forecast",
  "Navigationsziele": "Navigation destinations",
  "Fronthaube": "Front lid",
  "Heckklappe": "Rear lid",
  "Serviceklappe": "Service flap",
  "Schiebedach": "Sunroof",
  "Schiebedach hinten": "Rear sunroof",
  "Verdeck": "Convertible top",
  "Hauptservice": "Main service",
  "Zwischenservice": "Intermediate service",
  "Ölservice": "Oil service",
  "Zeit": "Time",
  "Fahrtstatistik": "Trip statistics",
  "Fahrthistorie": "Trip history",
  "Kurzzeit": "Short term",
  "Langzeit": "Long term",
  "Zyklus": "Cyclic",
  "Monatsbericht": "Monthly report",
  "Dienst nicht erreichbar.": "Service unavailable.",
  "Fahrzeugliste aktualisiert.": "Vehicle list updated.",
  "Angemeldet. Bitte Fahrzeuge auswählen und Einstellungen speichern.": "Signed in. Please select vehicles and save your settings.",
  "MQTT ist nicht erreichbar oder hat die Übertragung abgelehnt.": "MQTT is unreachable or rejected the transmission.",
  "Alte MQTT-Topics konnten nicht als ungültig markiert werden. Bitte Brokerverbindung wiederherstellen und erneut speichern.": "Old MQTT topics could not be invalidated. Restore the broker connection and save again.",
  "Reifendruck vorne links": "Tire pressure front left",
  "Tür vorne links": "Door front left",
  "Fenster vorne links": "Window front left",
  "Reifendruck vorne rechts": "Tire pressure front right",
  "Tür vorne rechts": "Door front right",
  "Fenster vorne rechts": "Window front right",
  "Reifendruck hinten links": "Tire pressure rear left",
  "Tür hinten links": "Door rear left",
  "Fenster hinten links": "Window rear left",
  "Reifendruck hinten rechts": "Tire pressure rear right",
  "Tür hinten rechts": "Door rear right",
  "Fenster hinten rechts": "Window rear right",
  "Pluginbereiche": "PLX sections",
  "Fahrzeug": "Vehicle",
  "Bereit zur Einrichtung.": "Ready for setup.",
  "Anmeldung läuft …": "Signing in …",
  "Status wird geprüft …": "Checking status …",
  "Bitte das CAPTCHA lösen. Der Vorgang läuft nach fünf Minuten ab.": "Please complete the CAPTCHA. This sign-in attempt expires after five minutes.",
  "Abgemeldet. Die gespeicherte Sitzung wurde gelöscht.": "Signed out. The saved session has been deleted.",
  "Anmeldung abgebrochen.": "Sign-in cancelled.",
  "Status abgerufen. Unbekanntes oder zu hohes Messalter bleibt als ungültig markiert.": "Status fetched. Data with unknown or excessive age stays marked invalid.",
  "Einstellungen gespeichert.": "Settings saved.",
  "Anmeldung abgelaufen. Bitte erneut starten.": "Sign-in expired. Please start again.",
  "Bitte erneut bei PLX anmelden und die Seite neu laden.": "Please sign in to PLX again and reload this page.",
  "Nur angehakte Werte werden per MQTT verschickt. Die Auswahl gilt für alle eingerichteten Fahrzeuge. Die Anzeige im Plugin bleibt vollständig. Heartbeat, Fehler- und Gültigkeitssignale bleiben zur Überwachung aktiv.": "Only checked values are sent over MQTT. Your selection applies to all configured vehicles. PLX still displays all data. Heartbeat, error and validity signals remain enabled for monitoring.",
  "Für die XML-Vorlage im MQTT Gateway UDP zum Miniserver aktivieren und denselben Port einstellen. Der Export berücksichtigt gespeicherte Datenauswahl und bereits gelesene Felder. „Hauptwerte“ begrenzt nur die Vorlage, nicht den MQTT-Versand. Das MQTT-Abonnement bleibt unabhängig vom Exportumfang gleich. Große Fahrt-/Historiengruppen können sehr viele Eingänge erzeugen. Reine Texte bleiben per MQTT verfügbar und werden in der numerischen UDP-Vorlage ausgelassen. Bestehende JSON-Topics bleiben zusätzlich erhalten.": "For the XML template, enable UDP to the Miniserver in your MQTT Gateway and use the same port. The export includes your saved selection and fields already fetched. “Main values” limits only the template, not MQTT output. The subscription stays the same for either scope. Trip histories can create many inputs. Text values remain available via MQTT and are omitted from the numeric UDP template. Existing JSON topics are retained.",
  "In Loxone jeden Wert mit data_valid UND dem jeweiligen …_available absichern. Den Heartbeat zusätzlich überwachen: Nach 180 Sekunden ohne neue Nachricht gilt die Integration als ausgefallen. Nicht verfügbare retained-Werte werden gelöscht; der Miniserver muss trotzdem die Freigabesignale auswerten.": "In Loxone, guard each value with data_valid AND its corresponding …_available signal. Also monitor the heartbeat: after 180 seconds without a new message, treat the integration as offline. Unavailable retained values are deleted; the Miniserver must still evaluate validity signals.",
  "Explizites Ladeziel, sofern gemeldet": "Explicit charge target, when reported",
  "Direktlademodus, kein Ladestatus": "Direct charging mode, not charging status",
  "Freigabe: Abruf erfolgreich und Messalter bekannt und zulässig": "Valid when fetch succeeds and measurement age is known and within the limit",
  "Einzelwert vorhanden": "Individual value available",
  "Cloud-Abruf / erneute Anmeldung nötig": "Cloud fetch / sign-in required",
  "Messalter / Messalter bekannt": "Measurement age / age known",
  "Plugin-Überwachung, am Präfix ohne Fahrzeugname": "Integration monitoring, at the prefix without a vehicle name",
  "Abgewählte MQTT-Werte konnten nicht gelöscht werden. Auswahl wurde nicht gespeichert.": "Deselected MQTT values could not be deleted. Your selection was not saved.",
  "Anfrage konnte nicht verarbeitet werden.": "The request could not be processed.",
  "Bitte den laufenden Vorgang abwarten.": "Please wait for the current operation to finish.",
  "Bitte erneut bei Porsche anmelden.": "Please sign in to Porsche again.",
  "Bitte vor einer neuen Anmeldung 30 Sekunden warten.": "Please wait 30 seconds before signing in again.",
  "Bitte vor einer neuen Fahrzeugabfrage 30 Sekunden warten.": "Please wait 30 seconds before loading vehicles again.",
  "Bitte zuerst anmelden und ein Fahrzeug aus der Liste auswählen.": "Please sign in and select a vehicle from the list first.",
  "Bitte zuerst erneut anmelden.": "Please sign in again first.",
  "Bitte zuerst mindestens ein Fahrzeug auswählen und speichern.": "Please select and save at least one vehicle first.",
  "Das Porsche-Konto ist gesperrt oder der Zugriff ist nicht freigegeben.": "The Porsche account is locked or access has not been granted.",
  "Die letzte Abfrage liegt weniger als fünf Minuten zurück.": "The last request was less than five minutes ago.",
  "Diese Aktion wird nicht unterstützt.": "This action is not supported.",
  "Ein Vorgang läuft bereits. Bitte kurz warten.": "An operation is already running. Please wait.",
  "Porsche hat keine verwendbaren Fahrzeugdaten geliefert.": "Porsche returned no usable vehicle data.",
  "Porsche ist momentan nicht erreichbar. Der nächste Versuch erfolgt automatisch.": "Porsche is currently unreachable. PLX will retry automatically.",
  "Ungültige Anfrage.": "Invalid request.",
  "Ungültige Exportanfrage.": "Invalid export request.",
  "Zu viele Anfragen. PLX wartet vor dem nächsten Versuch.": "Too many requests. PLX will wait before retrying.",
  "Bitte einen gültigen Schalterwert angeben.": "Please provide a valid switch value.",
  "Fahrzeug und Topic-Name müssen eindeutig sein.": "Vehicle and topic names must be unique.",
  "Fahrzeugantwort fehlt oder passt nicht zur Auswahl.": "The vehicle response is missing or does not match the selection.",
  "Fahrzeugname: Kleinbuchstaben, Ziffern, _ und -; maximal 32 Zeichen.": "Vehicle name: lowercase letters, digits, _ and -; maximum 32 characters.",
  "MQTT-Hostname oder IPv4-Adresse erforderlich.": "MQTT hostname or IPv4 address required.",
  "Porsche hat keine Messwerte geliefert.": "Porsche returned no measurements.",
  "Ungültige Fahrzeugauswahl.": "Invalid vehicle selection.",
  "Ungültige Fahrzeugnummer.": "Invalid vehicle identification number.",
  "Ungültige Konfiguration.": "Invalid configuration.",
  "Ungültige MQTT-Datenauswahl.": "Invalid MQTT data selection.",
  "Ungültige MQTT-Einstellung.": "Invalid MQTT setting.",
  "Ungültiger MQTT-Port.": "Invalid MQTT port.",
  "Ungültiges MQTT-Ausgabeformat.": "Invalid MQTT output format.",
  "Ungültiges MQTT-Präfix.": "Invalid MQTT prefix.",
  "Antwort zu umfangreich für die Statusansicht.": "Response too large for the status view."
};
  let language = 'de';
  try { language = localStorage.getItem('plx.language') === 'en' ? 'en' : 'de'; } catch (_) {}
  const originals = new WeakMap();
  function english(text) {
    if (messages[text]) return messages[text];
    const patterns = [
      [/^(.+): Wert zwischen (\d+) und (\d+) Sekunden erforderlich\.$/, '$1: a value between $2 and $3 seconds is required.'],
      [/^Vor (\d+) Minuten gemessen$/, 'Measured $1 minutes ago'],
      [/^(\d+) Fahrzeug\(e\) geladen · (\d+) gespeichert$/, '$1 vehicle(s) loaded · $2 saved'],
      [/^(\d+) Fahrzeug gefunden$/, '$1 vehicle found'],
      [/^(\d+) Fahrzeuge gefunden$/, '$1 vehicles found'],
      [/^(\d+) von (\d+) Parametern verfügbar$/, '$1 of $2 parameters available'],
      [/^(\d+) von (\d+) Parametern$/, '$1 of $2 parameters'],
      [/^(\d+) von (\d+) verfügbar$/, '$1 of $2 available'],
      [/^(\d+) Treffer · (\d+) Parameter$/, '$1 matches · $2 parameters'],
      [/^(\d+) von (\d+) Werten ausgewählt$/, '$1 of $2 values selected'],
    ];
    for (const [pattern, replacement] of patterns) if (pattern.test(text)) return text.replace(pattern, replacement);
    for (const [de,en] of [['Nächster Abruf: ','Next fetch: '],['Cloud-Abruf: ','Cloud fetch: '],['Direktlademodus: ','Direct charging mode: '],['Porsche Connect · ','Porsche Connect · ']]) {
      if (text.startsWith(de)) return en + english(text.slice(de.length));
    }
    text=text.replace(/(\d+) numerische Eingänge für UDP/g,'$1 numeric UDP inputs').replace(' (inkl. Überwachung)', ' (including monitoring)').replace(/(\d+) Text-\/unbekannte Felder nur in CSV\/MQTT/g,'$1 text/unknown fields in CSV/MQTT only').replace(/(\d+) Topics für UDP zu lang/g,'$1 topics too long for UDP').replace('Import in Loxone Config und Verbindung zum Miniserver anschließend prüfen.','Import into Loxone Config, then check the Miniserver connection.');
    // Composite labels are separated explicitly; never alter input values or technical keys.
    if (text.includes(' · ')) return text.split(' · ').map(english).join(' · ');
    if (text.includes(': ')) return text.split(': ').map(english).join(': ');
    return text;
  }
  function translate() {
    document.documentElement.lang = language;
    const root = document.querySelector('#p2l'); if (!root) return;
    const walker = document.createTreeWalker(root, NodeFilter.SHOW_TEXT);
    let n;
    while ((n = walker.nextNode())) {
      if (n.parentElement.closest('script,style,code,textarea,#language-switch,[data-vin],.vehicle-title h3,.parameter-vehicle-title h3,#found-list')) continue;
      const last=originals.get(n), current=n.nodeValue;
      const source=last && current===last.output ? last.source : current;
      const trimmed=source.trim(), output=language==='en'?source.replace(trimmed,english(trimmed)):source;
      originals.set(n,{source,output}); if(current!==output)n.nodeValue=output;
    }
    root.querySelectorAll('[placeholder],[aria-label]').forEach(el=>{
      for(const attr of ['placeholder','aria-label']) {
        if(!el.hasAttribute(attr))continue;
        const current=el.getAttribute(attr);
        const saved=originals.get(el)||{},last=saved[attr];
        const source=last&&current===last.output?last.source:current;
        const output=language==='en'?english(source):source;saved[attr]={source,output};originals.set(el,saved);
        if(current!==output)el.setAttribute(attr,output);
      }
    });
    document.querySelectorAll('.plx-logout button').forEach(b=>b.textContent=language==='en'?'Sign out of PLX':'PLX abmelden');
    document.querySelectorAll('#language-switch button').forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.language===language)));
  }
  const switcher=document.createElement('div');switcher.id='language-switch';switcher.setAttribute('role','group');switcher.setAttribute('aria-label','Language / Sprache');
  ['de','en'].forEach(lang=>{const b=document.createElement('button');b.type='button';b.textContent=lang.toUpperCase();b.dataset.language=lang;b.addEventListener('click',()=>{
    language=lang;try{localStorage.setItem('plx.language',lang);}catch(_){} translate();window.dispatchEvent(new Event('plx-language'));
  });switcher.append(b);});
  const headerControls=document.createElement('div');headerControls.className='header-controls';
  headerControls.append(switcher,document.querySelector('#connect-status'));
  document.querySelector('.hero').append(headerControls);
  window.PLXLanguage={get locale(){return language==='en'?'en-GB':'de-DE';},english,translate};
  let scheduled=false;
  const observer=new MutationObserver(()=>{if(!scheduled){scheduled=true;queueMicrotask(()=>{scheduled=false;observer.disconnect();translate();observe();});}});
  function observe(){observer.observe(document.querySelector('#p2l'),{subtree:true,childList:true,characterData:true});}
  translate();observe();
})();

(() => {
  'use strict';
  const root = document.querySelector('#p2l');
  document.body.classList.add('porsche2lox-page');
  // The classic LoxBerry theme gives its desktop margin precedence over plugin
  // styles. Override that one shell property on small screens and restore it
  // when returning to desktop; all other pages keep their original layout.
  const shell = root.closest('.lb-main');
  const smallScreen = window.matchMedia('(max-width:700px)');
  function fitShell() {
    if (!shell) return;
    if (smallScreen.matches) shell.style.setProperty('margin-left', '0px', 'important');
    else shell.style.removeProperty('margin-left');
  }
  smallScreen.addEventListener('change', fitShell);
  fitShell();
  const $ = (selector) => root.querySelector(selector);
  let state, dirty = false, pending = false, selecting = '', actionError = '', showSelection = false, firstView = true, loginExpanded = false, publishDirty = false;
  const labels = {signed_out:'Nicht angemeldet', session_saved:'Sitzung gespeichert', authenticated:'Angemeldet', captcha:'CAPTCHA erforderlich', expired:'Anmeldung abgelaufen', failed:'Anmeldung fehlgeschlagen', auth_required:'Anmeldung erforderlich', access_blocked:'Zugriff gesperrt'};
  const node = (tag, text, cls) => {const n = document.createElement(tag); if (text !== undefined) n.textContent = text; if (cls) n.className = cls; return n;};
  const stamp = (value) => value ? new Date(value * 1000).toLocaleString(window.PLXLanguage.locale) : 'Noch kein Abruf';
  const age = (seconds) => seconds == null ? 'Messalter unbekannt' : seconds < 60 ? 'Vor weniger als 1 Minute gemessen' : `Vor ${Math.floor(seconds / 60)} Minuten gemessen`;
  function notice(message, kind = '') {$('#notice').textContent = message; $('#notice').className = kind;}
  const transportWarning = 'Bitte PLX über HTTPS öffnen. Anmeldung und Speichern sind über HTTP gesperrt.';
  if (location.protocol !== 'https:') {
    const warning = document.createElement('p');
    warning.className = 'transport-warning'; warning.setAttribute('role', 'alert');
    warning.textContent = transportWarning;
    root.querySelector('nav').after(warning);
    root.querySelectorAll('#login-form input, #captcha-form input, input[type=password]').forEach(input => {input.disabled = true;});
  }
  ['login-form', 'captcha-form', 'settings-form'].forEach(id => {
    $('#' + id).addEventListener('submit', event => {
      if (location.protocol === 'https:') return;
      event.preventDefault(); event.stopImmediatePropagation();
      notice(transportWarning, 'error');
    }, true);
  });
  async function api(action, params = {}) {
    if (location.protocol !== 'https:' && ['login', 'captcha', 'save'].includes(action)) throw new Error(transportWarning);
    const response = await fetch('index.php?api=1', {method:'POST', credentials:'same-origin', cache:'no-store', headers:{'Content-Type':'application/json', 'X-CSRF-Token':root.dataset.csrf}, body:JSON.stringify({action, params})});
    const reply = await response.json();
    if (!reply.ok) throw new Error(reply.error || 'Dienst nicht erreichbar.');
    return reply.data;
  }
  async function act(action, params = {}) {
    if (pending) return;
    if (action === 'login' || action === 'captcha') loginExpanded = false;
    pending = true;
    try {actionError = ''; showSelection = ['vehicles','login','captcha'].includes(action); state = await api(action, params); render(); $('#notice').scrollIntoView({block:'nearest', behavior:'smooth'});}
    catch (error) {actionError = error.message; notice(actionError, 'error'); $('#notice').scrollIntoView({block:'nearest', behavior:'smooth'});}
    finally {pending = false;}
  }
  let parameterIndex = [], parameterGroups = [], filterActive = false, filterExpansion = new Set();
  function render() {
    if (!state) return;
    $('#data-age-help').textContent = (state.config.mqtt_format || 'detailed') === 'simple' ? 'Einfaches MQTT sendet den zuletzt gemeldeten Wert ohne Altersfreigabe; fehlende Werte sind null. Das Messalter siehst du in PLX.' : 'Im ausführlichen MQTT-Format melden data_valid und available die Freigabe. Auch ein neuer Cloud-Abruf kann alte Fahrzeugdaten liefern.';
    if (actionError) notice(actionError, 'error');
    else notice(state.job.message, state.job.state === 'error' ? 'error' : state.job.state === 'ok' ? 'ok' : '');
    const account = labels[state.login.state] || 'Unbekannt';
    $('#account-health').textContent = account;
    $('#login-state').textContent = account;
    const connected = state.login.state === 'authenticated' && !state.auth_blocked;
    const saved = state.login.state === 'session_saved' && !state.auth_blocked;
    const hasSession = connected || saved;
    const connectionText = connected ? 'Porsche Connect verbunden' : saved ? 'Porsche Connect · Sitzung gespeichert' : `Porsche Connect · ${account}`;
    $('#connect-status').textContent = connectionText;
    $('#connect-status').classList.toggle('connected', connected);
    $('#login-state').textContent = connected ? 'Verbunden' : account;
    $('#login-state').classList.toggle('valid', connected);
    $('#account-title').textContent = connected ? 'Mit Porsche Connect verbunden' : saved ? 'Porsche-Sitzung gespeichert' : 'Mit Porsche verbinden';
    $('#account-description').textContent = connected ? 'Du bist angemeldet. Keine erneute Anmeldung nötig – die Sitzung wird automatisch erneuert.' : saved ? 'Keine erneute Anmeldung nötig. Mit „Fahrzeuge laden“ kannst du die gespeicherte Sitzung prüfen.' : 'Melde dich mit deiner Porsche-ID an. Das Passwort wird nicht dauerhaft gespeichert.';
    $('#login-form').hidden = hasSession && !loginExpanded;
    $('#show-login').hidden = !hasSession;
    $('.account-layout').classList.toggle('session-active', hasSession && !loginExpanded);

    $('#vehicle-count').textContent = `${state.vehicles.length} Fahrzeug(e) geladen · ${state.config.vehicles.length} gespeichert`;
    const found = state.vehicles;
    $('#found-vehicles').hidden = !found.length;
    $('#found-title').textContent = `${found.length} ${found.length === 1 ? 'Fahrzeug gefunden' : 'Fahrzeuge gefunden'}`;
    $('#found-list').replaceChildren(...found.map(v => node('li', `${v.name} · …${v.vin.slice(-6)}`)));
    if (firstView) {
      firstView = false;
      if (!state.config.vehicles.length) openTab('account');
    }
    if (showSelection && !state.busy && state.login.state !== 'captcha') {
      showSelection = false;
      if (state.vehicles.length) {openTab('account'); $('#found-vehicles').scrollIntoView({block:'nearest', behavior:'smooth'});}
    }
    $('#mqtt-health').textContent = !state.config.mqtt.enabled ? 'Deaktiviert' : state.mqtt_ok === true ? 'Verbunden · Übertragung bestätigt' : state.mqtt_ok === false ? 'Verbindung fehlgeschlagen' : 'Wartet auf Übertragung';
    $('#poll-health').textContent = !state.config.enabled ? 'Automatik aus · manueller Abruf möglich' : state.auth_blocked ? 'Wartet auf Anmeldung' : state.next_poll_epoch ? `Nächster Abruf: ${stamp(state.next_poll_epoch)}` : 'Bereit';
    root.querySelectorAll('[data-action], #login-form button, #captcha-form button').forEach(b => {b.disabled = state.busy;});
    $('#publish-form button[type=submit]').disabled = state.busy;
    $('#refresh').disabled = state.busy || state.auth_blocked || !state.config.vehicles.length;
    const cards = $('#vehicles');
    const parameterCards = $('#parameter-vehicles');
    const expanded = new Set([...parameterCards.querySelectorAll('details[open][data-section]')].map(n => n.dataset.section));
    parameterCards.replaceChildren();
    parameterIndex = []; parameterGroups = [];
    if (!state.config.vehicles.length) parameterCards.append(node('div', 'Bitte zuerst ein Fahrzeug in der Einrichtung auswählen und speichern.', 'empty'));
    cards.replaceChildren();
    if (!state.config.vehicles.length) {
      const empty = node('div', undefined, 'empty');
      empty.append(node('p', state.vehicles.length ? 'Porsche ist verbunden. Bitte die Fahrzeugauswahl noch speichern.' : 'Bitte im Porsche-Konto Fahrzeuge laden und auswählen.'));
      const setup = node('button', 'Fahrzeug auswählen und speichern', 'secondary');
      setup.addEventListener('click', () => openTab('settings')); empty.append(setup); cards.append(empty);
    }
    state.config.vehicles.forEach(v => {
      const s = state.snapshots[v.alias] || {}, card = node('article', undefined, 'vehicle-card');
      const title = node('div', undefined, 'vehicle-title'); title.append(node('h3', state.vehicles.find(vehicle => vehicle.vin === v.vin)?.name || v.alias), node('span', s.data_valid ? 'Daten gültig' : 'Daten nicht freigegeben', `badge ${s.data_valid ? 'valid' : ''}`));
      const soc = node('div', s.soc == null ? '—' : String(s.soc), 'soc'); soc.append(node('span', ' %'));
      const track = node('div', undefined, 'battery-track'), fill = node('div', undefined, 'battery-fill'); fill.style.width = `${Math.min(100, Math.max(0, s.soc || 0))}%`; track.append(fill);
      const metrics = node('div', undefined, 'metrics');
      [[s.range_km == null ? '—' : `${s.range_km} km`, 'Reichweite'], [s.target_soc == null ? '—' : `${s.target_soc} %`, 'Ladeziel']].forEach(([value, label]) => {const m = node('div'); m.append(node('strong', value), node('span', label)); metrics.append(m);});
      const time = node('div', undefined, 'time'); time.append(node('div', age(s.data_age_s)), node('div', `Cloud-Abruf: ${stamp(s.last_fetch_epoch)}`), node('div', `Direktlademodus: ${s.direct_charge_enabled == null ? 'unbekannt' : s.direct_charge_enabled ? 'aktiviert' : 'deaktiviert'}`));
      card.append(title);
      const summary = node('div', undefined, 'vehicle-summary');
      if (state.images?.[v.alias]) {
        const picture = node('img', undefined, 'vehicle-picture');
        picture.alt = 'Modellansicht des Fahrzeugs';
        picture.src = `index.php?image=${encodeURIComponent(v.alias)}&v=${state.images[v.alias]}`;
        picture.addEventListener('error', () => picture.hidden = true);
        const visual = node('div', undefined, 'vehicle-visual');
        visual.append(picture); summary.append(visual); summary.classList.add('with-image');
      }
      const stats = node('div', undefined, 'vehicle-stats');
      stats.append(node('span', 'Batterie', 'metric-caption'), soc, track, metrics);
      summary.append(stats); card.append(summary, time);
      const dataCard = node('article', undefined, 'card parameter-vehicle');
      const dataTitle = node('div', undefined, 'parameter-vehicle-title');
      dataTitle.append(node('h3', state.vehicles.find(vehicle => vehicle.vin === v.vin)?.name || v.alias));
      if (s.parameters) {
        const parameters = Object.values(s.parameters);
        dataTitle.append(node('span', `${parameters.filter(p => p.available).length} von ${parameters.length} Parametern verfügbar`, 'badge'));
        dataCard.append(dataTitle, parameterDetails(s.parameters, v.alias, expanded));
      } else dataCard.append(dataTitle, node('p', 'Noch keine Detaildaten abgerufen. In der Übersicht „Status abrufen“ wählen.', 'hint'));
      parameterCards.append(dataCard);
      cards.append(card);
    });
    const captcha = state.login.state === 'captcha'; $('#captcha-form').hidden = !captcha;
    const image = state.login.image || '';
    if (captcha && image.length < 160000 && /^data:image\/(svg\+xml|png|jpeg)[;,]/i.test(image)) $('#captcha-image').src = image;
    else {$('#captcha-image').removeAttribute('src'); if (captcha) notice('Porsche hat kein darstellbares CAPTCHA geliefert. Anmeldung bitte neu starten.', 'error');}
    if (!dirty) renderSettings();
    renderVehicleChoices();
    applyParameterFilters();
    renderPublishSelection();
    $('#subscription').value = exportSubscriptions().join('\n');
  }
  const parameterNames = {percent:'Akkustand',kilometers:'Kilometer',lastModified:'Messzeitpunkt',chargingPower:'Ladeleistung',chargingPowerkW:'Ladeleistung',maxChargingPowerkW:'Maximale Ladeleistung',chargingRate:'Ladegeschwindigkeit',chargingRatekmPerMin:'Ladegeschwindigkeit',targetSoC:'Ladeziel',targetSoc:'Ladeziel',mode:'Modus',state:'Zustand',status:'Status',latitude:'Breitengrad',longitude:'Längengrad',actualPressureBar:'Reifendruck',differenceBar:'Abweichung',pressure:'Druck',temperature:'Temperatur',targetTemperature:'Zieltemperatur',isOpen:'Geöffnet',isLocked:'Verriegelt',isOn:'Eingeschaltet',isEnabled:'Aktiviert',value:'Wert',unit:'Einheit'};
  const parameterStates = {CHARGING:'Lädt',DIRECT:'Direktladen',NORMAL:'Normal',OFF:'Aus',ON:'An',LOCK:'Verriegeln',HIDDEN:'Nicht eingeblendet',NOT_AVAILABLE:'Nicht verfügbar',AC:'AC',DC:'DC'};
  function parameterValue(value,key='') {
    if(value==null)return 'Nicht verfügbar';
    if(typeof value==='boolean')return value?'Ja':'Nein';
    if(typeof value==='number'){
      if(key==='targetTemperature')return `${(value-273.15).toLocaleString(window.PLXLanguage.locale,{maximumFractionDigits:1})} °C`;
      const unit=key==='percent'||['targetSoC','targetSoc'].includes(key)?' %':key==='kilometers'?' km':key.endsWith('Bar')?' bar':key.endsWith('kW')?' kW':key.endsWith('kmPerMin')?' km/min':'';
      return value.toLocaleString(window.PLXLanguage.locale,{maximumFractionDigits:6})+unit;
    }
    if(/^\d{4}-\d{2}-\d{2}T/.test(value)&&!Number.isNaN(Date.parse(value)))return new Date(value).toLocaleString(window.PLXLanguage.locale);
    return parameterStates[value]||String(value);
  }
  function parameterRows(value,path=[],output=[]) {
    if(value!==null&&typeof value==='object')Object.entries(value).forEach(([k,v])=>parameterRows(v,[...path,k],output));
    else output.push({label:path.map(k=>parameterNames[k]||k).join(' · ')||'Wert',value:parameterValue(value,path.at(-1)),key:path.at(-1)||'',preview:!path.some(k=>['lastModified','timestamp','lastModifiedTime','supportedStatuses','actions','id','uuid','snapshotId','createTime','lastUsedTime'].includes(k))});
    return output;
  }
  function parameterStatus(p) {
    if(!p.available)return 'Nicht verfügbar';
    if(p.data_valid)return 'Aktuell';
    if(!p.age_known)return 'Messalter unbekannt';
    return p.data_age_s>state.config.max_age_s?'Veraltet':'Nicht freigegeben';
  }
  function searchText(value){return String(value).toLowerCase().replaceAll('ß','ss').normalize('NFKD').replace(/[\u0300-\u036f]/g,'');}
  function parameterDetails(parameters, alias, expanded) {
    const root = node('div', undefined, 'parameter-groups');
    const groups = new Map();
    Object.entries(parameters).forEach(([key,p])=>{if(!groups.has(p.group))groups.set(p.group,[]);groups.get(p.group).push([key,p]);});
    groups.forEach((items,group,index)=>{
      const section=node('details',undefined,'parameter-group');section.dataset.section=`${alias}/${group}`;section.open=expanded.has(section.dataset.section);
      const heading=node('summary');
      const icon=node('span',String(parameterGroups.length%6+1).padStart(2,'0'),'group-symbol');icon.setAttribute('aria-hidden','true');
      const copy=node('span',undefined,'group-heading');copy.append(node('strong',group));
      const count=node('small',`${items.filter(([,p])=>p.available).length} von ${items.length} verfügbar`);copy.append(count);heading.append(icon,copy);section.append(heading);
      const entry={section,count,items:[],total:items.length};parameterGroups.push(entry);
      items.forEach(([key,p])=>{
        const item=node('details',undefined,'parameter-item');item.dataset.section=`${alias}/${key}`;item.open=expanded.has(item.dataset.section);
        const status=parameterStatus(p),values=p.available?parameterRows(p.value):[];
        const summary=node('summary');
        const top=node('span',undefined,'parameter-heading');top.append(node('strong',p.label),node('span',status,'parameter-status'));summary.append(top);
        const preview=values.filter(v=>v.preview).slice(0,2).map(v=>`${v.label}: ${v.value}`).join(' · ');
        summary.append(node('span',p.available?(preview||'Keine Einträge'):'Derzeit keine Fahrzeugdaten','parameter-preview'));item.append(summary);
        if(p.available){const list=node('dl',undefined,'parameter-values');values.forEach(v=>list.append(node('dt',v.label),node('dd',v.value)));item.append(list,node('p',p.age_known?age(p.data_age_s):'Kein verlässlicher Messzeitpunkt vorhanden.','hint'));}
        else item.append(node('p',p.reason||'Dieses Fahrzeug liefert diesen Parameter derzeit nicht.','hint'));
        item.append(node('code',key,'parameter-key'));section.append(item);
        const corpus=[alias,key,p.label,p.group,status,p.reason,JSON.stringify(p.value),...values.map(v=>`${v.label} ${v.value}`)].join(' ');
        const englishCorpus=window.PLXLanguage.english(p.label)+' '+window.PLXLanguage.english(p.group)+' '+values.map(v=>window.PLXLanguage.english(v.label)+' '+window.PLXLanguage.english(String(v.value))).join(' ');
        const german=corpus.replace(/[äöüÄÖÜ]/g,c=>({ä:'ae',ö:'oe',ü:'ue',Ä:'Ae',Ö:'Oe',Ü:'Ue'}[c]));
        const record={item,key,p,alias,corpus:searchText(corpus+' '+german+' '+englishCorpus)};entry.items.push(record);parameterIndex.push(record);
      });root.append(section);
    });return root;
  }
  function applyParameterFilters(){
    const words=searchText($('#parameter-search').value.trim()).split(/\s+/).filter(Boolean),mode=$('#parameter-filter').value,active=words.length>0||mode!=='all';
    if(active&&!filterActive)filterExpansion=new Set(parameterGroups.filter(g=>g.section.open).map(g=>g.section.dataset.section));
    let visible=0;
    parameterGroups.forEach(group=>{
      let matches=0;
      group.items.forEach(record=>{
        const p=record.p;
        const status=mode==='all'||mode==='available'&&p.available||mode==='current'&&p.available&&p.data_valid||mode==='stale'&&p.available&&p.age_known&&p.data_age_s>state.config.max_age_s||mode==='unavailable'&&!p.available||mode==='unknown'&&p.available&&!p.age_known||mode==='published'&&(state.config.publish_parameters==null||state.config.publish_parameters.includes(record.key));
        const shown=Boolean(status)&&words.every(w=>record.corpus.includes(w));record.item.hidden=!shown;if(shown){matches++;visible++;}
      });
      group.section.hidden=matches===0;
      group.count.textContent=active?`${matches} Treffer · ${group.total} Parameter`:`${group.items.filter(r=>r.p.available).length} von ${group.total} verfügbar`;
      if(active)group.section.open=matches>0;
      else if(filterActive)group.section.open=filterExpansion.has(group.section.dataset.section);
    });
    $('#parameter-vehicles').querySelectorAll('.parameter-vehicle').forEach(card=>{card.hidden=active&&![...card.querySelectorAll('.parameter-group')].some(g=>!g.hidden);});
    $('#parameter-results').textContent=`${visible} von ${parameterIndex.length} Parametern`;
    $('#parameter-no-results').hidden=!parameterIndex.length||visible>0;filterActive=active;
  }
  let searchTimer;
  $('#parameter-search').addEventListener('input',()=>{clearTimeout(searchTimer);searchTimer=setTimeout(applyParameterFilters,120);});
  $('#parameter-filter').addEventListener('change',applyParameterFilters);
  $('#parameter-reset').addEventListener('click',()=>{$('#parameter-search').value='';$('#parameter-filter').value='all';applyParameterFilters();$('#parameter-search').focus();});
  const basePublishFields = [['soc','Akkustand (%)'],['range_km','Reichweite (km)'],['target_soc','Ladeziel (%)'],['direct_charge_enabled','Direktlademodus']];
  function updatePublishCount() {
    const all = [...$('#publish-options').querySelectorAll('input[type=checkbox]')];
    $('#publish-count').textContent = `${all.filter(n=>n.checked).length} von ${all.length} Werten ausgewählt`;
  }
  function applyOutputFormat(mode) {
    const simple=mode==='simple';
    $('#publish-help').textContent=simple?'Pro Auswahl ein Topic. Reifendruck wird als Zahl in bar gesendet, ohne zusätzliche Diagnose- oder Verfügbarkeitsthemen. Gesendet wird der zuletzt gemeldete Wert; das Messalter siehst du in PLX. Fehlende Werte: null.':'Nur angehakte Werte werden per MQTT verschickt. Heartbeat, Fehler- und Gültigkeitssignale bleiben zur Überwachung aktiv.';
    $('#loxone-scope-label').hidden=simple;
    $('#legacy-mqtt-reference').hidden=simple;
    const hint=$('#loxone-export-hint');
    if(!hint.dataset.detailedText)hint.dataset.detailedText=hint.textContent;
    hint.textContent=simple?'Optional für Loxone: Die XML-Vorlage enthält genau die ausgewählten numerischen Werte. Für reines MQTT ist kein Export nötig.':hint.dataset.detailedText;
  }
  $('#publish-format').addEventListener('change',event=>{publishDirty=true;applyOutputFormat(event.target.value);$('#publish-feedback').textContent='Noch nicht gespeichert';});
  function renderPublishSelection() {
    if (publishDirty) return;
    const target = $('#publish-options');
    const signature = JSON.stringify([state.parameter_catalog,state.config.publish_parameters,state.config.publish_fields,state.config.mqtt_format]);
    if (target.dataset.signature === signature) return;
    target.dataset.signature = signature; target.replaceChildren();
    $('#publish-format').value=state.config.mqtt_format||'detailed';applyOutputFormat($('#publish-format').value);
    const groups = new Map([['Hauptwerte',basePublishFields.map(([key,label])=>({key,label,kind:'field'}))]]);
    (state.parameter_catalog || []).forEach(p=>{if(!groups.has(p.group))groups.set(p.group,[]);groups.get(p.group).push({...p,kind:'parameter'});});
    groups.forEach((items,group)=>{
      const section = node('details'); section.open = group === 'Hauptwerte';section.append(node('summary',`${group} · ${items.length}`));
      items.forEach(p=>{
        const label=node('label',undefined,'switch'); const check=node('input');check.type='checkbox';check.dataset.publishKind=p.kind;check.value=p.key;
        const selected=p.kind==='field'?state.config.publish_fields:state.config.publish_parameters;
        check.checked=selected == null || selected.includes(p.key);
        label.append(check,document.createTextNode(p.label));section.append(label);
      });target.append(section);
    });updatePublishCount();
  }
  $('#publish-options').addEventListener('change',()=>{publishDirty=true;$('#publish-feedback').textContent='Noch nicht gespeichert';updatePublishCount();});
  for (const [id,checked] of [['publish-all',true],['publish-none',false]]) $(id.startsWith('#')?id:`#${id}`).addEventListener('click',()=>{
    $('#publish-options').querySelectorAll('input[type=checkbox]').forEach(n=>n.checked=checked);publishDirty=true;$('#publish-feedback').textContent='Noch nicht gespeichert';updatePublishCount();
  });
  $('#publish-form').addEventListener('submit',async event=>{
    event.preventDefault();
    const config=structuredClone(state.config);config.mqtt.password=null;config.mqtt_format=$('#publish-format').value;
    config.publish_fields=[...$('#publish-options').querySelectorAll('[data-publish-kind="field"]:checked')].map(n=>n.value);
    config.publish_parameters=[...$('#publish-options').querySelectorAll('[data-publish-kind="parameter"]:checked')].map(n=>n.value);
    try {state=await api('save',config);publishDirty=false;actionError='';$('#publish-feedback').textContent='Datenauswahl gespeichert.';render();}
    catch(error){$('#publish-feedback').textContent=error.message;actionError=error.message;notice(actionError,'error');}
  });
  function renderSettings() {
    const form = $('#settings-form'), c = state.config;
    for (const key of ['enabled', 'interval_s', 'max_age_s']) {const field = form.elements[key]; if (field.type === 'checkbox') field.checked = c[key]; else field.value = c[key];}
    for (const key of ['host','port','username','prefix']) form.elements[key].value = c.mqtt[key];
    form.elements.mqtt_enabled.checked = c.mqtt.enabled; form.elements.tls.checked = c.mqtt.tls;
    form.elements.mqtt_password.placeholder = c.mqtt.password_set ? 'Gespeichert · leer lassen zum Beibehalten' : 'MQTT-Passwort';
  }
  function renderVehicleChoices() {
    const c = state.config;
    const signature = JSON.stringify([state.vehicles, c.vehicles]);
    if (signature === selecting) return;
    selecting = signature;
    const select = $('#vehicle-select');
    const drafts = new Map([...select.querySelectorAll('[data-vin]')].map(check => [check.dataset.vin, {checked:check.checked, alias:[...select.querySelectorAll('[data-alias]')].find(n => n.dataset.alias === check.dataset.vin)?.value}]));
    select.replaceChildren();
    const all = new Map(c.vehicles.map(v => [v.vin, {vin:v.vin, name:v.alias}]));
    state.vehicles.forEach(v => all.set(v.vin, v));
    if (!all.size) select.textContent = 'Bitte zuerst anmelden und Fahrzeuge laden.';
    [...all.values()].forEach((vehicle, i) => {
      const selected = c.vehicles.find(v => v.vin === vehicle.vin);
      const div = node('div', undefined, 'vehicle-choice'), check = node('input'); check.type = 'checkbox'; check.dataset.vin = vehicle.vin; check.checked = dirty && drafts.has(vehicle.vin) ? drafts.get(vehicle.vin).checked : Boolean(selected);
      const label = node('label', undefined, 'switch'); label.append(check, document.createTextNode(`${vehicle.name} · …${vehicle.vin.slice(-6)}`));
      const alias = node('input'); alias.value = (dirty && drafts.get(vehicle.vin)?.alias) || selected?.alias || `porsche${i+1}`; alias.pattern = '[a-z][a-z0-9_-]{0,31}'; alias.maxLength = 32; alias.addEventListener('change', () => {alias.value = alias.value.toLowerCase().normalize('NFKD').replace(/[\u0300-\u036f]/g, '').replace(/[^a-z0-9_-]+/g, '_').replace(/^[^a-z]+/, '').slice(0,32) || `porsche${i+1}`;}); alias.dataset.alias = vehicle.vin;
      const aliasLabel = node('label', 'Technischer Name für Loxone/MQTT (z. B. taycan)'); aliasLabel.append(alias); div.append(label, aliasLabel); select.append(div);
    });
  }
  function openTab(id) {
    root.querySelectorAll('.tab,.panel').forEach(n => n.classList.remove('active'));
    root.querySelector(`.tab[data-tab="${id}"]`).classList.add('active');
    $(`#${id}`).classList.add('active');
  }
  root.querySelectorAll('.tab').forEach(button => button.addEventListener('click', () => openTab(button.dataset.tab)));
  $('#show-login').addEventListener('click', () => {loginExpanded = !loginExpanded; render();});
  $('#choose-vehicles').addEventListener('click', () => {openTab('settings'); $('.vehicle-setup').scrollIntoView({block:'start', behavior:'smooth'});});
  root.querySelectorAll('[data-action]').forEach(button => button.addEventListener('click', () => act(button.dataset.action)));
  $('#login-form').addEventListener('submit', event => {event.preventDefault(); const form = event.target; const params = {email:form.elements.email.value.trim(), password:form.elements.password.value}; form.elements.password.value = ''; act('login', params);});
  $('#captcha-form').addEventListener('submit', event => {event.preventDefault(); const code = event.target.elements.code.value; event.target.reset(); act('captcha', {code});});
  $('#settings-form').addEventListener('input', () => {dirty = true;});
  $('#settings-form').addEventListener('submit', async event => {
    event.preventDefault(); const f = event.target.elements;
    const vehicles = [...root.querySelectorAll('[data-vin]:checked')].map(check => ({vin:check.dataset.vin, alias:[...root.querySelectorAll('[data-alias]')].find(n => n.dataset.alias === check.dataset.vin).value}));
    const config = {mqtt_format:state.config.mqtt_format||'detailed',publish_fields:state.config.publish_fields,publish_parameters:state.config.publish_parameters,enabled:f.enabled.checked, interval_s:Number(f.interval_s.value), max_age_s:Number(f.max_age_s.value), vehicles,
      mqtt:{enabled:f.mqtt_enabled.checked, host:f.host.value.trim(), port:Number(f.port.value), username:f.username.value, password:f.clear_password.checked ? '' : f.mqtt_password.value || null, prefix:f.prefix.value, tls:f.tls.checked}};
    try {state = await api('save', config); actionError = ''; $('#save-feedback').textContent = 'Gespeichert. Die Fahrzeugauswahl wurde übernommen.'; dirty = false; f.mqtt_password.value = ''; f.clear_password.checked = false; selecting = ''; render();}
    catch(error) {$('#save-feedback').textContent = error.message; actionError = error.message; notice(actionError, 'error'); $('#notice').scrollIntoView({block:'nearest'});}
  });
  function exportSubscriptions() {
    const prefix=state.config.mqtt.prefix;
    return [`${prefix}/#`];
  }
  $('#loxone-scope').addEventListener('change',()=>{$('#subscription').value=exportSubscriptions().join('\n');$('#export-feedback').textContent='Exportumfang geändert. Das MQTT-Abonnement bleibt gleich.';});
  async function downloadLoxone(kind) {
    if (!state) return;
    if (publishDirty) {$('#export-feedback').textContent='Bitte zuerst die Datenauswahl speichern.'; return;}
    try {
      const result=await api('loxone_export',{port:Number($('#loxone-port').value),source:$('#loxone-source').value.trim(),scope:$('#loxone-scope').value});
      const url=URL.createObjectURL(new Blob([result[kind]],{type:kind==='xml'?'application/xml;charset=utf-8':'text/csv;charset=utf-8'}));
      const a=node('a');a.href=url;a.download=kind==='xml'?'VIU_PLX.xml':'PLX-Loxone.csv';a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);
      $('#export-feedback').textContent=`${result.numeric_count} numerische Eingänge für UDP${state.config.mqtt_format==='simple'?'':' (inkl. Überwachung)'} · ${result.text_count} Text-/unbekannte Felder nur in CSV/MQTT`+(result.too_long_count?` · ${result.too_long_count} Topics für UDP zu lang`:'')+'. Import in Loxone Config und Verbindung zum Miniserver anschließend prüfen.';
    } catch(error) {$('#export-feedback').textContent=error.message;}
  }
  $('#export').addEventListener('click',()=>downloadLoxone('csv'));
  $('#export-xml').addEventListener('click',()=>downloadLoxone('xml'));
  async function update() {try {if (!pending) {state = await api('status'); render();}} catch(error) {notice(error.message, 'error');} finally {setTimeout(update, 3000);}}
  window.addEventListener('plx-language',()=>{render();window.PLXLanguage.translate();});
  update();
})();
