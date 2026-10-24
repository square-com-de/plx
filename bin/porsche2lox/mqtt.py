"""Bounded MQTT publishing with acknowledgement and explicit unknown values."""
import threading
import json
import ssl

import paho.mqtt.client as mqtt

from .core import FIELDS
from .loxone import flat_topics, mqtt_scalar, HEALTH_FIELDS
from .compact import compact_rows


def messages(prefix, alias, snapshot, selected_parameters=None, selected_fields=None):
    selected_fields = set(FIELDS if selected_fields is None else selected_fields)
    base = f"{prefix}/{alias}"
    # data_valid=0 brackets each update. Individual field flags prevent a missing
    # retained value from being mistaken for a new measurement by consumers.
    result = [(f"{base}/data_valid", "0")]
    for key, value in snapshot.items():
        if key == "parameters":
            for name, parameter in value.items():
                if selected_parameters is not None and name not in selected_parameters:
                    continue
                for field_route, field in flat_topics(prefix, alias, name, parameter):
                    result.extend([(field_route+'/value', mqtt_scalar(field['value']) if field['available'] else ''),
                                   (field_route+'/available', str(field['available']))])
                route = f"{base}/parameters/{name.lower()}"
                result.extend([(f"{route}/value", json.dumps(parameter.get("value"), ensure_ascii=False, allow_nan=False) if parameter.get("available") else ""),
                               (f"{route}/available", str(parameter.get("available", 0))),
                               (f"{route}/data_valid", str(parameter.get("data_valid", 0))),
                               (f"{route}/measurement_epoch", str(parameter.get("measurement_epoch") or ""))])
            continue
        if key == "data_valid":
            continue
        if key in FIELDS and key not in selected_fields:
            continue
        result.append((f"{base}/{key}", "" if value is None else str(value)))
    for key in FIELDS:
        if key not in selected_fields:
            continue
        result.append((f"{base}/{key}_available", str(int(snapshot.get(key) is not None))))
    result.append((f"{base}/data_valid", str(snapshot.get("data_valid", 0))))
    return result


def selection_routes(config, snapshots=None):
    from .parameters import READ_MEASUREMENTS
    if config.get('mqtt_format', 'detailed') == 'simple':
        return {row['topic'] for row in compact_rows(config, snapshots or {})}
    routes = {config['mqtt']['prefix']+'/heartbeat'}
    for vehicle in config['vehicles']:
        base = f"{config['mqtt']['prefix']}/{vehicle['alias']}"
        routes.update(base+'/'+key for key in HEALTH_FIELDS)
        for key in config.get('publish_fields', FIELDS):
            routes.update((f'{base}/{key}', f'{base}/{key}_available'))
        for key in config.get('publish_parameters', READ_MEASUREMENTS):
            parameter = (snapshots or {}).get(vehicle['alias'], {}).get('parameters', {}).get(key, {})
            for route, field in flat_topics(config['mqtt']['prefix'], vehicle['alias'], key, parameter):
                routes.update((route+'/value',route+'/available'))
            for field in ('value','available','data_valid','measurement_epoch'):
                routes.add(f'{base}/parameters/{key.lower()}/{field}')
    return routes


def selection_deletions(old, new, snapshots=None):
    return [(topic, '') for topic in sorted(selection_routes(old, snapshots) - selection_routes(new, snapshots))]


def publish(config, payloads):
    """Connect/publish/disconnect within a fixed deadline; never log secrets."""
    ready = threading.Event()
    accepted = []
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)

    def on_connect(_client, _userdata, _flags, reason, _properties):
        accepted.append(not reason.is_failure)
        ready.set()

    client.on_connect = on_connect
    if config["username"]:
        client.username_pw_set(config["username"], config["password"])
    if config["tls"]:
        client.tls_set_context(ssl.create_default_context())
    client.connect_timeout = 5
    try:
        client.connect(config["host"], config["port"], keepalive=30)
        client.loop_start()
        if not ready.wait(7) or not accepted or not accepted[0]:
            raise ConnectionError("MQTT-Anmeldung fehlgeschlagen.")
        import time
        deadline = time.monotonic() + 10
        for topic, payload in payloads:
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                raise TimeoutError("MQTT-Zeitlimit erreicht.")
            message = client.publish(topic, payload, qos=1, retain=True)
            message.wait_for_publish(timeout=remaining)
            if not message.is_published():
                raise TimeoutError("MQTT hat die Übertragung nicht bestätigt.")
    finally:
        client.disconnect()
        client.loop_stop()
