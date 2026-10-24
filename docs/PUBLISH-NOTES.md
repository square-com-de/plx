PLX brings Porsche Connect into your smart home — as a standalone HTTPS Docker container and a LoxBerry 4 plugin, with the same German/English dashboard.

**Deutsch:** Porsche Connect für dein intelligentes Zuhause: Docker-Container oder LoxBerry-Plugin, mit kompakter Übersicht, Fahrzeugbild, Suchfunktion und gezielter MQTT-Auswahl. Zwei gewählte Reifendrücke ergeben zwei Topics mit Zahlen in bar. Einstellungen und Sitzung bleiben beim LoxBerry-Update erhalten.

**English:** Compact vehicle overview, account-provided model image, searchable parameters and selective MQTT output. Two selected tire pressures produce two numeric topics in bar. LoxBerry updates preserve settings and the Porsche session.

### Downloads

- **LoxBerry:** install `PLX-LoxBerry-0.1.0.zip` in the plugin manager. Do not use the automatic GitHub source ZIP as a plugin package.
- **Docker / Portainer:** extract `PLX-Docker-0.1.0.tar.gz`; its Compose file pins the release image digest. Public image: `ghcr.io/square-com-de/plx:0.1.0` (AMD64/ARM64), no registry login required. Create your own PLX web-password secret before starting.
- Verify downloads against `SHA256SUMS`. `manifest.json` identifies the source and container digest.

### Preview limits

This is a **pre-release**, not stable. Reads Porsche Connect status only; no vehicle commands or wake requests. Vehicle data requires the Porsche cloud and varies by model/contract. Simple MQTT sends the last reported value, missing data as `null`; it has no heartbeat/age topics. Use detailed mode when freshness signals are needed.

Separate Docker and LoxBerry tests cover HTTPS, account/vehicle fetch, DE/EN/mobile UI, installer updates with retained settings/session and exactly two pressure values at an isolated MQTT broker. Full MQTT Gateway → Loxone Miniserver acceptance remains open.

Original PLX code: MIT. Third-party libraries and Porsche trademarks/artwork retain their own terms. Independent project, not affiliated with or supported by Porsche or Loxone.

[English documentation](https://github.com/square-com-de/plx/blob/main/README.md) · [Deutsch](https://github.com/square-com-de/plx/blob/main/README.de.md) · Contact: plx@square-com.de
