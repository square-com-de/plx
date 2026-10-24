"""Validated configuration, atomic private storage and measurement parsing."""
from __future__ import annotations

import json
import copy
import math
import os
import re
import tempfile
from datetime import datetime, timezone
from pathlib import Path

DEFAULTS = {
    "enabled": False, "interval_s": 900, "max_age_s": 3600, "mqtt_format": "simple",
    "vehicles": [],
    "mqtt": {"enabled": False, "host": "127.0.0.1", "port": 1883,
             "username": "", "password": "", "tls": False,
             "prefix": "porsche2lox"},
}
FIELDS = ("soc", "range_km", "target_soc", "direct_charge_enabled")


class DataError(Exception):
    pass


def write_private(path: Path, value):
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    fd, temporary = tempfile.mkstemp(prefix=".p2l-", dir=path.parent)
    try:
        with os.fdopen(fd, "w") as file:
            json.dump(value, file, ensure_ascii=False, allow_nan=False)
            file.flush()
            os.fsync(file.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def read_json(path: Path, default=None):
    if not path.exists():
        return json.loads(json.dumps(default))
    return json.loads(path.read_text())


def boolean(value):
    if type(value) is not bool:
        raise ValueError("Bitte einen gültigen Schalterwert angeben.")
    return value


def validate_config(config):
    if not isinstance(config, dict):
        raise ValueError("Ungültige Konfiguration.")
    result = copy.deepcopy(DEFAULTS)
    # Existing installations without an explicit format keep their old topics.
    result['mqtt_format'] = config.get('mqtt_format', 'detailed')
    if result['mqtt_format'] not in ('simple', 'detailed'):
        raise ValueError('Ungültiges MQTT-Ausgabeformat.')
    result["enabled"] = boolean(config.get("enabled", False))
    for key, low, high in (("interval_s", 300, 86400), ("max_age_s", 300, 604800)):
        value = config.get(key, DEFAULTS[key])
        if type(value) is not int or not low <= value <= high:
            raise ValueError(f"{key}: Wert zwischen {low} und {high} Sekunden erforderlich.")
        result[key] = value
    from .parameters import READ_MEASUREMENTS
    for key, allowed in (("publish_parameters", READ_MEASUREMENTS), ("publish_fields", FIELDS)):
        chosen = config.get(key, list(allowed))
        if not isinstance(chosen, list) or any(not isinstance(k, str) or k not in allowed for k in chosen):
            raise ValueError("Ungültige MQTT-Datenauswahl.")
        result[key] = list(dict.fromkeys(chosen))
    names, vins = set(), set()
    vehicles = config.get("vehicles", [])
    if not isinstance(vehicles, list) or len(vehicles) > 20:
        raise ValueError("Ungültige Fahrzeugauswahl.")
    for item in vehicles:
        if not isinstance(item, dict):
            raise ValueError("Ungültige Fahrzeugauswahl.")
        vin, alias = item.get("vin", ""), item.get("alias", "")
        if not isinstance(vin, str) or not re.fullmatch(r"[A-HJ-NPR-Z0-9]{17}", vin):
            raise ValueError("Ungültige Fahrzeugnummer.")
        if not isinstance(alias, str) or not re.fullmatch(r"[a-z][a-z0-9_-]{0,31}", alias):
            raise ValueError("Fahrzeugname: Kleinbuchstaben, Ziffern, _ und -; maximal 32 Zeichen.")
        if alias in names or vin in vins:
            raise ValueError("Fahrzeug und Topic-Name müssen eindeutig sein.")
        names.add(alias)
        vins.add(vin)
        result["vehicles"].append({"vin": vin, "alias": alias})
    mqtt = config.get("mqtt", {})
    if not isinstance(mqtt, dict):
        raise ValueError("Ungültige MQTT-Einstellung.")
    for key in ("enabled", "tls"):
        result["mqtt"][key] = boolean(mqtt.get(key, DEFAULTS["mqtt"][key]))
    for key, limit in (("host", 253), ("username", 256), ("password", 2048), ("prefix", 80)):
        value = mqtt.get(key, DEFAULTS["mqtt"][key])
        if not isinstance(value, str) or len(value) > limit or any(ord(c) < 32 for c in value):
            raise ValueError("Ungültige MQTT-Einstellung.")
        result["mqtt"][key] = value
    if not re.fullmatch(r"[A-Za-z0-9._-]+", result["mqtt"]["host"]):
        raise ValueError("MQTT-Hostname oder IPv4-Adresse erforderlich.")
    if not re.fullmatch(r"[a-z][a-z0-9_-]{0,79}", result["mqtt"]["prefix"]):
        raise ValueError("Ungültiges MQTT-Präfix.")
    port = mqtt.get("port", 1883)
    if type(port) is not int or not 1 <= port <= 65535:
        raise ValueError("Ungültiger MQTT-Port.")
    result["mqtt"]["port"] = port
    return result


def epoch(value):
    if isinstance(value, str):
        try:
            parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
            if parsed.tzinfo is not None:
                return int(parsed.timestamp())
        except ValueError:
            pass
    return None


def number(value, low, high):
    if type(value) not in (int, float) or not math.isfinite(value) or not low <= value <= high:
        return None
    return value


def parse_overview(payload, vin, now, max_age):
    """Never use library properties: missing battery is not a real 0% reading."""
    if not isinstance(payload, dict) or payload.get("vin") != vin:
        raise DataError("Fahrzeugantwort fehlt oder passt nicht zur Auswahl.")
    measurements = payload.get("measurements")
    if not isinstance(measurements, list):
        raise DataError("Porsche hat keine Messwerte geliefert.")
    enabled = {}
    for item in measurements:
        if isinstance(item, dict) and isinstance(item.get("status"), dict) and item["status"].get("isEnabled") is True:
            if isinstance(item.get("value"), dict):
                enabled[item.get("key")] = item["value"]
    battery = enabled.get("BATTERY_LEVEL", {})
    soc = number(battery.get("percent"), 0, 100)
    if not enabled:
        raise DataError("Porsche hat keine verwendbaren Fahrzeugdaten geliefert.")
    charging = enabled.get("CHARGING_SUMMARY", {})
    target = number(charging.get("targetSoC"), 0, 100)
    # Only publish an explicit target. Profile minimum SoC is NOT a target.
    if target is None:
        target = number(enabled.get("CHARGING_SETTINGS", {}).get("targetSoc"), 0, 100)
    mode = charging.get("mode")
    direct = int(mode == "DIRECT") if mode in ("DIRECT", "PROFILE", "TIMER") else None
    measured = epoch(battery.get("lastModified"))
    age = now - measured if measured is not None else None
    fresh = soc is not None and age is not None and -300 <= age <= max_age
    from .parameters import parse_parameters
    return {
        "parameters": parse_parameters(measurements, now, max_age),
        "soc": soc,
        "range_km": number(enabled.get("E_RANGE", {}).get("kilometers"), 0, 3000),
        "target_soc": target, "direct_charge_enabled": direct,
        "measurement_epoch": measured, "data_age_s": max(0, age) if age is not None else None,
        "data_valid": int(fresh), "age_known": int(age is not None),
        "api_ok": 1, "auth_required": 0, "error_code": 0,
        "last_fetch_epoch": now,
    }


def refresh_age(snapshot, now, max_age):
    result = dict(snapshot)
    if "parameters" in result:
        from .parameters import refresh_parameters
        result["parameters"] = refresh_parameters(result["parameters"], now, max_age, result.get("api_ok"))
    measured = result.get("measurement_epoch")
    age = now - measured if measured is not None else None
    result["data_age_s"] = max(0, age) if age is not None else None
    result["age_known"] = int(age is not None)
    result["data_valid"] = int(bool(result.get("api_ok")) and result.get("soc") is not None and age is not None and -300 <= age <= max_age)
    return result
