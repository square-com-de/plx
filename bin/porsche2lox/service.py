"""Private local control socket, short-lived login flow and status scheduler."""
from __future__ import annotations

import argparse
import asyncio
import fcntl
import hashlib
import json
import logging
import os
import signal
import time
from pathlib import Path

from .core import DEFAULTS, FIELDS, DataError, parse_overview, read_json, refresh_age, validate_config, write_private
from .mqtt import messages, publish, selection_deletions, selection_routes, BrokerMonitor, failure_code
from .loxone import enrich_schema, make_exports
from .parameters import READ_MEASUREMENTS, LABELS, category
from .compact import compact_rows
from .porsche import Porsche, SessionExpired

ERRORS = {
    1: "Porsche ist momentan nicht erreichbar. Der nächste Versuch erfolgt automatisch.",
    2: "Porsche hat keine verwendbaren Fahrzeugdaten geliefert.",
    3: "Bitte erneut bei Porsche anmelden.",
    4: "Zu viele Anfragen. PLX wartet vor dem nächsten Versuch.",
    5: "MQTT ist nicht erreichbar oder hat die Übertragung abgelehnt.",
    6: "Das Porsche-Konto ist gesperrt oder der Zugriff ist nicht freigegeben.",
}


def error_code(exc):
    if isinstance(exc, DataError):
        return 2
    status = getattr(exc, "code", None)
    name = type(exc).__name__
    body = str(getattr(exc, "response_body", "") or "").lower()
    if isinstance(exc, SessionExpired) or status == 401 or "WrongCredentials" in name or "invalid_grant" in body:
        return 3
    if status == 429:
        return 4
    if status in (405, 423):
        return 6
    return 1


class Service:
    def __init__(self, config_dir, data_dir, adapter=None, publisher=publish):
        self.config_dir, self.data_dir = Path(config_dir), Path(data_dir)
        for directory in (self.config_dir, self.data_dir):
            directory.mkdir(parents=True, exist_ok=True, mode=0o700)
            directory.chmod(0o700)
        self.config_path = self.config_dir / "settings.json"
        self.config = validate_config(read_json(self.config_path, DEFAULTS))
        if not self.config_path.exists():
            write_private(self.config_path, self.config)
        self.porsche = adapter or Porsche(self.data_dir / "session.json")
        self.publisher = publisher
        self.monitor = BrokerMonitor() if publisher is publish else None
        self.cleanup_path = self.data_dir / 'mqtt-cleanup.json'
        self.pending_cleanup = read_json(self.cleanup_path, [])
        self.cleanup_attempt = 0
        self.mqtt_error = None
        self.snapshots = read_json(self.data_dir / "status.json", {})
        for snapshot in self.snapshots.values():
            enrich_schema(snapshot)
            snapshot.update(api_ok=0, data_valid=0)
        self.vehicles = []
        self.login = {"state": "session_saved" if (self.data_dir / "session.json").exists() else "signed_out"}
        self.job = {"state": "idle", "message": "Bereit zur Einrichtung."}
        self.task = None
        self.saving = False
        self.control_lock = asyncio.Lock()
        self.last_login = 0
        self.last_list = 0
        self.next_poll = 0
        self.last_poll = 0
        self.last_mqtt = 0
        self.mqtt_ok = None
        self.cleaned_selection = None
        self.auth_blocked = False
        self.failures = 0
        self.stopping = asyncio.Event()

    @property
    def busy(self):
        return self.saving or (self.task is not None and not self.task.done())

    def view(self):
        now = int(time.time())
        config = json.loads(json.dumps(self.config))
        config["mqtt"]["password_set"] = bool(config["mqtt"].pop("password"))
        return {
            "version": "0.1.5", "config": config, "login": self.login,
            "parameter_catalog": [{"key": key, "label": LABELS.get(key, key.replace("_", " ").capitalize()), "group": category(key)} for key in READ_MEASUREMENTS],
            "vehicles": self.vehicles, "job": self.job, "busy": self.busy,
            "images": {v["alias"]: int(self.image_path(v["vin"]).stat().st_mtime) for v in self.config["vehicles"] if self.image_path(v["vin"]).exists()},
            "snapshots": {v["alias"]: refresh_age(self.snapshots.get(v["alias"], {}), now, self.config["max_age_s"])
                          for v in self.config["vehicles"]},
            "mqtt_status": self.monitor.view() if self.monitor else {'state': 'disabled' if not self.config['mqtt']['enabled'] else 'unknown', 'error': None},
            "mqtt_cleanup_pending": bool(self.pending_cleanup), "mqtt_delivery_error": self.mqtt_error,
            "mqtt_ok": self.mqtt_ok, "next_poll_epoch": int(self.next_poll) if self.next_poll else None,
            "auth_blocked": self.auth_blocked,
        }

    def launch(self, action, params):
        if self.busy:
            raise ValueError("Ein Vorgang läuft bereits. Bitte kurz warten.")
        if action == "poll" and time.time() - self.last_poll < 300:
            raise ValueError("Die letzte Abfrage liegt weniger als fünf Minuten zurück.")
        if action == "login":
            if time.time() - self.last_login < 30:
                raise ValueError("Bitte vor einer neuen Anmeldung 30 Sekunden warten.")
            self.last_login = time.time()
        if action == "vehicles":
            if time.time() - self.last_list < 30:
                raise ValueError("Bitte vor einer neuen Fahrzeugabfrage 30 Sekunden warten.")
            self.last_list = time.time()
        self.job = {"state": "running", "message": "Anmeldung läuft …" if action in ("login", "captcha") else "Status wird geprüft …"}
        self.task = asyncio.create_task(self.run_job(action, params))

    async def run_job(self, action, params):
        try:
            if action in ("login", "captcha"):
                self.login = await self.porsche.login(
                    email=params.get("email"), password=params.get("password"),
                    code=params.get("code") if action == "captcha" else None,
                )
                params.clear()
                if self.login["state"] == "captcha":
                    self.job = {"state": "waiting", "message": "Bitte das CAPTCHA lösen. Der Vorgang läuft nach fünf Minuten ab."}
                    return
                self.auth_blocked = False
                self.next_poll = 0
                self.failures = 0
                self.vehicles = await self.porsche.vehicles()
                self.job = {"state": "ok", "message": "Angemeldet. Bitte Fahrzeuge auswählen und Einstellungen speichern."}
            elif action == "vehicles":
                self.vehicles = await self.porsche.vehicles()
                await self.cache_images()
                self.login = {"state": "authenticated"}
                self.job = {"state": "ok", "message": "Fahrzeugliste aktualisiert."}
            elif action == "logout":
                await self.porsche.cancel_login()
                (self.data_dir / "session.json").unlink(missing_ok=True)
                self.login = {"state": "signed_out"}
                self.vehicles = []
                self.auth_blocked = True
                self.invalidate(3)
                await self.publish_status()
                self.job = {"state": "ok", "message": "Abgemeldet. Die gespeicherte Sitzung wurde gelöscht."}
            elif action == "cancel":
                await self.porsche.cancel_login()
                self.login = {"state": "session_saved" if (self.data_dir / "session.json").exists() else "signed_out"}
                self.job = {"state": "idle", "message": "Anmeldung abgebrochen."}
            elif action == "poll":
                await self.poll()
        except asyncio.CancelledError:
            raise
        except Exception as exc:
            code = error_code(exc)
            if code == 3:
                self.auth_blocked = True
                self.login = {"state": "auth_required"}
            elif action in ("login", "captcha"):
                self.login = {"state": "failed"}
            self.job = {"state": "error", "message": ERRORS[code], "error_code": code}
        finally:
            params.clear()

    def invalidate(self, code):
        for vehicle in self.config["vehicles"]:
            alias = vehicle["alias"]
            snapshot = self.snapshots.setdefault(alias, {key: None for key in FIELDS})
            snapshot.update(api_ok=0, data_valid=0, error_code=code, auth_required=int(code == 3))

    def image_path(self, vin):
        return self.data_dir / ("vehicle-" + hashlib.sha256(vin.encode()).hexdigest() + ".image")

    async def cache_images(self):
        if not self.vehicles:
            try:
                self.vehicles = await self.porsche.vehicles()
            except Exception:
                pass
        for vehicle in self.config["vehicles"]:
            try:
                await self.porsche.cache_picture(vehicle["vin"], self.image_path(vehicle["vin"]))
            except Exception:
                pass  # Optional picture failure never invalidates vehicle data.

    async def poll(self):
        if not self.config["vehicles"]:
            raise ValueError("Bitte zuerst mindestens ein Fahrzeug auswählen und speichern.")
        self.last_poll = time.time()
        codes = []
        for vehicle in self.config["vehicles"]:
            alias = vehicle["alias"]
            try:
                payload = await self.porsche.overview(vehicle["vin"])
                self.snapshots[alias] = enrich_schema(parse_overview(payload, vehicle["vin"], int(time.time()), self.config["max_age_s"]), self.snapshots.get(alias))
                self.login = {"state": "authenticated"}
            except Exception as exc:
                code = error_code(exc)
                codes.append(code)
                snapshot = self.snapshots.setdefault(alias, {key: None for key in FIELDS})
                snapshot.update(api_ok=0, data_valid=0, auth_required=int(code == 3), error_code=code)
                if code in (3, 6):
                    self.auth_blocked = True
                    self.login = {"state": "auth_required" if code == 3 else "access_blocked"}
                    self.invalidate(code)
                    break
        await self.cache_images()
        write_private(self.data_dir / "status.json", self.snapshots)
        self.failures = min(5, self.failures + 1) if codes else 0
        delay = max(self.config["interval_s"], 3600 if 4 in codes else 0)
        self.next_poll = time.time() + min(86400, delay * (2 ** self.failures))
        await self.publish_status()
        if codes:
            self.job = {"state": "error", "message": ERRORS[codes[0]], "error_code": codes[0]}
        elif self.config["mqtt"]["enabled"] and self.mqtt_ok is False:
            self.job = {"state": "error", "message": ERRORS[5], "error_code": 5}
        else:
            self.job = {"state": "ok", "message": "Status abgerufen. Unbekanntes oder zu hohes Messalter bleibt als ungültig markiert."}

    @staticmethod
    def broker_identity(config):
        return tuple(config[key] for key in ('host', 'port', 'tls'))

    async def retry_cleanup(self):
        if not self.pending_cleanup:
            return
        # Remove reselected routes before retrying, including after a restart.
        current = selection_routes(self.config, self.snapshots)
        queue = []
        for entry in self.pending_cleanup:
            topics = set(entry['topics'])
            if self.broker_identity(entry['mqtt']) == self.broker_identity(self.config['mqtt']):
                topics -= current
                # Use updated credentials when the broker identity is unchanged.
                entry = dict(entry, mqtt=dict(self.config['mqtt']))
            if topics:
                queue.append(dict(entry, topics=sorted(topics)))
        self.pending_cleanup = queue
        write_private(self.cleanup_path, queue)
        if not queue:
            return
        entry = queue[0]
        try:
            await asyncio.to_thread(self.publisher, entry['mqtt'], [(topic, '') for topic in entry['topics']])
        except Exception as exc:
            self.mqtt_error = failure_code(exc)
            # A retired/unreachable broker must not starve later entries.
            self.pending_cleanup.append(self.pending_cleanup.pop(0))
            write_private(self.cleanup_path, self.pending_cleanup)
        else:
            self.pending_cleanup.pop(0)
            write_private(self.cleanup_path, self.pending_cleanup)
            self.mqtt_error = None
        self.cleanup_attempt = time.time()

    async def publish_status(self, config=None, force_invalid=False):
        config = config or self.config
        if not config["mqtt"]["enabled"]:
            self.mqtt_ok = None
            return
        if config.get('mqtt_format', 'detailed') == 'simple':
            # No shutdown invalidations, heartbeat, catalog sweep or metadata.
            if force_invalid:
                return
            now = int(time.time())
            snapshots = {v['alias']: refresh_age(self.snapshots.get(v['alias'], {}), now, config['max_age_s'])
                         for v in config['vehicles']}
            payloads = [(r['topic'], r['payload']) for r in compact_rows(config, snapshots)]
            if not payloads:
                self.mqtt_ok = None
                self.last_mqtt = time.time()
                return
            try:
                await asyncio.to_thread(self.publisher, config['mqtt'], payloads)
                self.mqtt_ok = True
                self.mqtt_error = None
            except Exception as exc:
                self.mqtt_error = failure_code(exc)
                self.mqtt_ok = False
            self.last_mqtt = time.time()
            return
        now = int(time.time())
        payloads = []
        payloads.append((f"{config['mqtt']['prefix']}/heartbeat", str(now)))
        for vehicle in config["vehicles"]:
            snapshot = refresh_age(self.snapshots.get(vehicle["alias"], {key: None for key in FIELDS}), now, config["max_age_s"])
            if force_invalid:
                snapshot.update(api_ok=0, data_valid=0)
                for parameter in snapshot.get('parameters', {}).values():
                    parameter['data_valid'] = 0
            payloads.extend(messages(config["mqtt"]["prefix"], vehicle["alias"], snapshot,
                                     config.get('publish_parameters'), config.get('publish_fields')))
        try:
            await asyncio.to_thread(self.publisher, config["mqtt"], payloads)
            self.mqtt_ok = True
            self.mqtt_error = None
        except Exception as exc:
            self.mqtt_error = failure_code(exc)
            self.mqtt_ok = False
        self.last_mqtt = time.time()

    async def command(self, request):
        if request.get('action') == 'loxone_export':
            params = request.get('params', {})
            if not isinstance(params, dict):
                raise ValueError('Ungültige Exportanfrage.')
            return make_exports(self.config, self.snapshots, params.get('port',11883), params.get('source',''),params.get('scope','selected'))
        if request.get("action", "status") == "status":
            return self.view()
        async with self.control_lock:
            return await self._command(request)

    async def _command(self, request):
        action = request.get("action", "status")
        params = request.get("params", {})
        if not isinstance(params, dict):
            raise ValueError("Ungültige Anfrage.")
        if action == "status":
            return self.view()
        if action == "save":
            if self.busy:
                raise ValueError("Bitte den laufenden Vorgang abwarten.")
            candidate = dict(params)
            candidate.setdefault('mqtt_format', self.config.get('mqtt_format', 'detailed'))
            mqtt = dict(candidate.get("mqtt", {}))
            if mqtt.get("password") is None:
                mqtt["password"] = self.config["mqtt"]["password"]
            candidate["mqtt"] = mqtt
            candidate = validate_config(candidate)
            known = {v["vin"] for v in self.vehicles} | {v["vin"] for v in self.config["vehicles"]}
            if any(v["vin"] not in known for v in candidate["vehicles"]):
                raise ValueError("Bitte zuerst anmelden und ein Fahrzeug aus der Liste auswählen.")
            # Persist cleanup intent first. A broker outage must not discard the
            # desired selection. Private outbox survives restarts and is retried.
            self.saving = True
            try:
                removed = selection_deletions(self.config, candidate, self.snapshots)
                queue = list(self.pending_cleanup)
                if removed and self.config['mqtt']['enabled']:
                    queue.append({'mqtt': dict(self.config['mqtt']), 'topics': [topic for topic, _ in removed]})
                write_private(self.cleanup_path, queue)
                previous = self.config
                write_private(self.config_path, candidate)
                self.config = candidate
                self.pending_cleanup = queue
                self.mqtt_ok = None
                self.mqtt_error = None
                self.cleanup_attempt = 0
                if self.monitor:
                    self.monitor.configure(candidate['mqtt'])
                self.snapshots = {v["alias"]: self.snapshots.get(v["alias"], {}) for v in candidate["vehicles"]}
                mqtt_only = candidate.get('mqtt_format') == 'simple' and candidate['vehicles'] == previous['vehicles']
                if not mqtt_only:
                    self.invalidate(0)
                if not mqtt_only or any(candidate[key] != previous[key] for key in ('enabled', 'interval_s')):
                    self.next_poll = max(time.time(), self.last_poll + 300)
                self.last_mqtt = 0
                self.job = {"state": "ok", "message": "Einstellungen gespeichert. Alte MQTT-Werte werden noch bereinigt." if self.pending_cleanup else "Einstellungen gespeichert."}
            finally:
                self.saving = False
        elif action in ("login", "captcha", "vehicles", "poll", "logout", "cancel"):
            if action == "poll" and self.auth_blocked:
                raise ValueError("Bitte zuerst erneut anmelden.")
            self.launch(action, params)
        else:
            raise ValueError("Diese Aktion wird nicht unterstützt.")
        return self.view()

    async def tick(self):
        while not self.stopping.is_set():
            if self.monitor:
                self.monitor.configure(self.config['mqtt'])
            if not self.busy:
                async with self.control_lock:
                    if self.pending_cleanup and time.time() - self.cleanup_attempt >= 30:
                        await self.retry_cleanup()
                await self.porsche.expire_login()
                if self.login.get("state") == "captcha" and not self.porsche.pending:
                    self.login = {"state": "expired"}
                    self.job = {"state": "error", "message": "Anmeldung abgelaufen. Bitte erneut starten."}
                if self.config["enabled"] and self.config["vehicles"] and not self.auth_blocked and not self.porsche.pending and time.time() >= self.next_poll:
                    self.launch("poll", {})
                elif self.config["enabled"] and time.time() - self.last_mqtt >= 60:
                    async with self.control_lock:
                        await self.publish_status()
            try:
                await asyncio.wait_for(self.stopping.wait(), timeout=2)
            except TimeoutError:
                pass

    async def handle(self, reader, writer):
        try:
            raw = await asyncio.wait_for(reader.readline(), timeout=5)
            request = json.loads(raw)
            if not isinstance(request, dict):
                raise ValueError()
            result = {"ok": True, "data": await self.command(request)}
        except ValueError as exc:
            result = {"ok": False, "error": str(exc)[:200] or "Ungültige Anfrage."}
        except Exception:
            result = {"ok": False, "error": "Anfrage konnte nicht verarbeitet werden."}
        writer.write(json.dumps(result, ensure_ascii=False).encode() + b"\n")
        try:
            await writer.drain()
        finally:
            writer.close()
            await writer.wait_closed()

    async def run(self):
        socket = self.data_dir / "control.sock"
        socket.unlink(missing_ok=True)
        server = await asyncio.start_unix_server(self.handle, path=socket, limit=32768)
        socket.chmod(0o600)
        loop = asyncio.get_running_loop()
        for sig in (signal.SIGINT, signal.SIGTERM):
            loop.add_signal_handler(sig, self.stopping.set)
        try:
            async with server:
                await self.tick()
        finally:
            if self.task and not self.task.done():
                self.task.cancel()
                await asyncio.gather(self.task, return_exceptions=True)
            await self.publish_status(force_invalid=True)
            if self.monitor:
                await asyncio.to_thread(self.monitor.close)
            await self.porsche.close()
            socket.unlink(missing_ok=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--config-dir", required=True, type=Path)
    parser.add_argument("--data-dir", required=True, type=Path)
    args = parser.parse_args()
    os.umask(0o077)
    args.data_dir.mkdir(parents=True, exist_ok=True, mode=0o700)
    with (args.data_dir / "service.lock").open("w") as lock:
        try:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            raise SystemExit("PLX läuft bereits.")
        logging.basicConfig(level=logging.CRITICAL)
        asyncio.run(Service(args.config_dir, args.data_dir).run())


if __name__ == "__main__":
    main()
