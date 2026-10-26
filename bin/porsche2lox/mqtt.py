"""Bounded MQTT publishing with acknowledgement and explicit unknown values."""
import threading
import json
import ssl
import socket
import time

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
        accepted.append(None if not reason.is_failure else ('auth' if reason.value in (134, 135) else 'rejected'))
        ready.set()

    client.on_connect = on_connect
    denied = threading.Event()
    def on_publish(_client, _userdata, _mid, reason, _properties):
        if reason.is_failure:
            denied.set()
    client.on_publish = on_publish
    if config["username"]:
        client.username_pw_set(config["username"], config["password"])
    if config["tls"]:
        client.tls_set_context(ssl.create_default_context())
    client.connect_timeout = 5
    try:
        client.connect(config["host"], config["port"], keepalive=30)
        client.loop_start()
        if not ready.wait(7) or not accepted:
            raise MQTTError('timeout')
        if accepted[0]:
            raise MQTTError(accepted[0])
        import time
        deadline = time.monotonic() + 10
        for topic, payload in payloads:
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                raise TimeoutError("MQTT-Zeitlimit erreicht.")
            message = client.publish(topic, payload, qos=1, retain=True)
            message.wait_for_publish(timeout=remaining)
            if denied.is_set():
                raise MQTTError('rejected')
            if not message.is_published():
                raise TimeoutError("MQTT hat die Übertragung nicht bestätigt.")
    finally:
        client.disconnect()
        client.loop_stop()


class MQTTError(ConnectionError):
    """Stable, secret-free category exposed to the UI."""
    def __init__(self, code):
        self.code = code
        super().__init__(code)


def failure_code(exc):
    if isinstance(exc, MQTTError):
        return exc.code
    if isinstance(exc, ssl.SSLError):
        return 'tls'
    if isinstance(exc, (TimeoutError, socket.timeout)):
        return 'timeout'
    if isinstance(exc, OSError):
        return 'unreachable'
    return 'delivery'


class BrokerMonitor:
    """A separate, idle connection tracks broker login and disconnects.

    It never subscribes or publishes; delivery acknowledgement is kept separate.
    Callbacks only write the state of this client, so an old connection cannot
    overwrite the state after a configuration change.
    """
    def __init__(self):
        self.client = None
        self.config = None
        self.state = {'state': 'disabled', 'error': None}
        self.lock = threading.RLock()

    def view(self):
        with self.lock:
            return dict(self.state)

    def configure(self, config):
        if config == self.config:
            return
        self.close()
        self.config = dict(config)
        if not config['enabled']:
            return
        client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
        with self.lock:
            self.client = client
            self.state = {'state': 'connecting', 'error': None}

        def state(value, error=None):
            with self.lock:
                if self.client is client:
                    self.state = {'state': value, 'error': error}

        def connected(_client, _userdata, _flags, reason, _properties):
            state('error', 'auth' if reason.value in (134, 135) else 'rejected') if reason.is_failure else state('connected')

        def disconnected(_client, _userdata, _flags, reason, _properties):
            # Preserve a precise CONNACK failure until the next connect attempt.
            with self.lock:
                if self.client is client and self.state['state'] != 'error':
                    state('disconnected')

        client.on_connect = connected
        client.on_disconnect = disconnected
        client.on_connect_fail = lambda *_: state('error', 'unreachable')
        if config['username']:
            client.username_pw_set(config['username'], config['password'])
        client.connect_timeout = 5
        client.reconnect_delay_set(min_delay=3, max_delay=30)
        try:
            if config['tls']:
                client.tls_set_context(ssl.create_default_context())
            client.connect_async(config['host'], config['port'], keepalive=15)
            client.loop_start()
        except Exception as exc:
            state('error', failure_code(exc))

    def close(self):
        with self.lock:
            client, self.client = self.client, None
            self.state = {'state': 'disabled', 'error': None}
        if client:
            client.disconnect()
            client.loop_stop()
