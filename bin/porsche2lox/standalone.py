"""Standalone HTTPS shell for the shared PLX UI and private control service."""
from __future__ import annotations

import argparse
import base64
import hashlib
import hmac
import html
import json
import os
from pathlib import Path
import secrets
import signal
import socket
import ssl
import subprocess
import sys
import threading
import time
from collections import defaultdict, deque
from http.cookies import SimpleCookie
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlsplit

ACTIONS = {'status', 'save', 'login', 'captcha', 'vehicles', 'poll', 'logout', 'cancel', 'loxone_export'}
MAX_BODY = 30000
MAX_REPLY = 4194304


class Application:
    def __init__(self, root, data, username, password):
        if not username or len(username) > 100 or len(password) < 16:
            raise ValueError('PLX-Benutzername und ein Passwort mit mindestens 16 Zeichen erforderlich.')
        self.root, self.data = Path(root), Path(data)
        self.username = username
        self.salt = secrets.token_bytes(32)
        self.digest = self.password_hash(password)
        self.sessions = {}
        self.attempts = defaultdict(deque)
        self.lock = threading.Lock()
        self.worker = None

    def password_hash(self, password):
        return hashlib.pbkdf2_hmac('sha256', password.encode(), self.salt, 600000)

    def authenticate(self, address, username, password):
        now = time.monotonic()
        with self.lock:
            # Bound memory even when many different source addresses connect.
            self.attempts = defaultdict(deque, {k: v for k, v in self.attempts.items() if v and v[-1] > now - 60})
            attempts = self.attempts[address]
            if len(attempts) >= 5 or len(self.attempts) > 1000:
                return None
            attempts.append(now)
        valid = hmac.compare_digest(self.password_hash(password), self.digest)
        valid = hmac.compare_digest(username.encode(), self.username.encode()) and valid
        if not valid:
            return None
        token, csrf = secrets.token_urlsafe(32), secrets.token_hex(32)
        with self.lock:
            self.sessions = {k: v for k, v in self.sessions.items() if v[0] > time.monotonic()}
            if len(self.sessions) >= 32:
                self.sessions.pop(next(iter(self.sessions)))
            self.sessions[token] = (now + 8 * 3600, csrf)
        return token

    def session(self, token):
        with self.lock:
            result = self.sessions.get(token)
            if result and result[0] > time.monotonic():
                return result[1]
            self.sessions.pop(token, None)
        return None

    def command(self, request):
        with socket.socket(socket.AF_UNIX) as connection:
            connection.settimeout(25)
            connection.connect(str(self.data / 'runtime/control.sock'))
            connection.sendall(json.dumps(request, ensure_ascii=False).encode() + b'\n')
            with connection.makefile('rb') as stream:
                reply = stream.readline(MAX_REPLY + 1)
        if len(reply) > MAX_REPLY or not reply.endswith(b'\n'):
            raise ValueError('Ungültige Dienstantwort.')
        json.loads(reply)
        return reply

    def ready(self):
        return (self.worker is None or self.worker.poll() is None) and (self.data / 'runtime/control.sock').exists()


class Server(ThreadingHTTPServer):
    daemon_threads = True
    request_queue_size = 16

    def __init__(self, address, app, tls_context=None):
        self.app = app
        self.tls_context = tls_context
        self.slots = threading.BoundedSemaphore(16)
        super().__init__(address, Handler)

    def process_request(self, request, client_address):
        if not self.slots.acquire(blocking=False):
            self.shutdown_request(request)
            return
        try:
            super().process_request(request, client_address)
        except Exception:
            self.slots.release()
            raise

    def process_request_thread(self, request, client_address):
        try:
            if self.tls_context is not None:
                request.settimeout(10)
                try:
                    request = self.tls_context.wrap_socket(request, server_side=True)
                except (OSError, ssl.SSLError):
                    self.shutdown_request(request)
                    return
            super().process_request_thread(request, client_address)
        finally:
            self.slots.release()


class Handler(BaseHTTPRequestHandler):
    server_version = 'PLX'
    sys_version = ''

    def setup(self):
        super().setup()
        self.connection.settimeout(30)

    def log_message(self, *args):
        # Never log URLs, cookies, credentials or vehicle data.
        pass

    @property
    def app(self):
        return self.server.app

    def respond(self, status, body=b'', mime='text/html; charset=utf-8', headers=None, script_nonce=None):
        if isinstance(body, str):
            body = body.encode()
        self.send_response(status)
        self.send_header('Content-Type', mime)
        self.send_header('Content-Length', str(len(body)))
        self.send_header('Cache-Control', 'no-store')
        self.send_header('X-Content-Type-Options', 'nosniff')
        self.send_header('Referrer-Policy', 'same-origin')
        self.send_header('X-Frame-Options', 'DENY')
        script_policy = "'self'" + (" 'nonce-" + script_nonce + "'" if script_nonce else '')
        self.send_header('Content-Security-Policy', f"default-src 'self'; img-src 'self' data:; style-src 'self' 'unsafe-inline'; script-src {script_policy}; connect-src 'self'; frame-ancestors 'none'; base-uri 'none'; form-action 'self'")
        for key, value in (headers or {}).items():
            self.send_header(key, value)
        self.end_headers()
        self.wfile.write(body)

    def json_error(self, status, message):
        self.respond(status, json.dumps({'ok': False, 'error': message}), 'application/json; charset=utf-8')

    def token(self):
        try:
            cookie = SimpleCookie(self.headers.get('Cookie', ''))
            return cookie['plx_session'].value if 'plx_session' in cookie else ''
        except Exception:
            return ''

    def login_page(self, error=''):
        nonce = secrets.token_urlsafe(24)
        language_script = "<script>(()=>{let lang='de';try{lang=localStorage.getItem('plx.language')==='en'?'en':'de'}catch(_){}const texts={'Dein Porsche x Loxone in Deinem intelligenten Zuhause.':'Your Porsche x Loxone in your smart home.','Benutzername':'Username','PLX-Passwort':'PLX password','Anmelden':'Sign in','Die Anmeldung bei Porsche erfolgt anschließend in PLX.':'You can sign in to Porsche inside PLX.','Anmeldung nicht möglich. Zugangsdaten prüfen oder eine Minute warten.':'Unable to sign in. Check your credentials or wait one minute.'};const originals=new WeakMap();function apply(){document.documentElement.lang=lang;document.title=lang==='en'?'PLX · Sign in':'PLX · Anmelden';const w=document.createTreeWalker(document.querySelector('main'),NodeFilter.SHOW_TEXT);let n;while(n=w.nextNode()){if(n.parentElement.closest('#login-language'))continue;const source=originals.get(n)||n.nodeValue;originals.set(n,source);const t=source.trim();n.nodeValue=lang==='en'?source.replace(t,texts[t]||t):source}document.querySelectorAll('#login-language button').forEach(b=>{b.setAttribute('aria-pressed',String(b.dataset.lang===lang));b.style.background=b.dataset.lang===lang?'#101114':'white';b.style.color=b.dataset.lang===lang?'white':'#62656b'})}const switcher=document.createElement('div');switcher.id='login-language';switcher.setAttribute('role','group');switcher.setAttribute('aria-label','Language / Sprache');switcher.style.cssText='position:fixed;top:16px;right:20px;display:flex;gap:4px';for(const l of ['de','en']){const b=document.createElement('button');b.type='button';b.textContent=l.toUpperCase();b.dataset.lang=l;b.style.cssText='margin:0;width:auto;padding:7px 11px;cursor:pointer';b.onclick=()=>{lang=l;try{localStorage.setItem('plx.language',lang)}catch(_){}apply()};switcher.append(b)}document.body.append(switcher);apply()})();</script>"
        language_script = language_script.replace('<script>', '<script nonce="' + nonce + '">', 1)
        error = html.escape(error)
        self.respond(401, f'''<!doctype html><html lang="de"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>PLX · Anmelden</title><style>body{{margin:0;background:#f3f3f4;font:15px/1.5 -apple-system,BlinkMacSystemFont,Segoe UI,sans-serif;color:#101114}}main{{max-width:360px;margin:12vh auto;padding:30px;background:white;border-radius:18px}}h1{{margin:0}}p{{color:#62656b}}label{{display:block;margin-top:16px}}input,button{{box-sizing:border-box;width:100%;padding:12px;border:1px solid #c9cbd0;border-radius:6px;font:inherit}}button{{margin-top:24px;background:#101114;color:white}}.error{{color:#a71930}}</style><main><h1>PLX</h1><p>Dein Porsche x Loxone in Deinem intelligenten Zuhause.</p><form action="/auth/login" method="post"><label>Benutzername<input name="username" autocomplete="username" required maxlength="100"></label><label>PLX-Passwort<input name="password" type="password" autocomplete="current-password" required maxlength="1024"></label><button>Anmelden</button><p class="error" role="alert">{error}</p></form><p>Die Anmeldung bei Porsche erfolgt anschließend in PLX.</p></main>{language_script}</html>''', script_nonce=nonce)

    def same_origin(self):
        origin = self.headers.get('Origin')
        # Direct HTTPS only: forwarded headers are intentionally not trusted.
        return origin is None or origin == 'https://' + self.headers.get('Host', '')

    def read_body(self):
        if self.headers.get('Transfer-Encoding'):
            raise ValueError()
        size = int(self.headers.get('Content-Length', '-1'))
        if not 0 <= size <= MAX_BODY:
            raise ValueError()
        body = self.rfile.read(size)
        if len(body) != size:
            raise ValueError()
        return body

    def do_GET(self):
        path = urlsplit(self.path)
        if path.path == '/healthz':
            self.respond(200 if self.app.ready() else 503, b'ready' if self.app.ready() else b'starting', 'text/plain')
            return
        csrf = self.app.session(self.token())
        if not csrf:
            if 'api' in parse_qs(path.query):
                self.json_error(401, 'Bitte erneut bei PLX anmelden und die Seite neu laden.')
            else:
                self.login_page()
            return
        if path.path in ('/', '/index.php'):
            query = parse_qs(path.query)
            if 'image' in query:
                self.image(query['image'][0])
                return
            if 'api' in query:
                self.json_error(405, 'POST erforderlich.')
                return
            content = (self.app.root / 'templates/dashboard.html').read_text().replace('<?= $csrf ?>', csrf)
            content = content.replace('auf deinem LoxBerry gespeichert', 'in deinem eigenen PLX-Datenspeicher gespeichert')
            content = content.replace('Die bestehende App verwendet porsche/taycan. PLX veröffentlicht in einem eigenen Namensraum.', 'Docker: Broker-Adresse im Netzwerk verwenden; 127.0.0.1 bezeichnet diesen Container. PLX nutzt eigene Topics.')
            logout = f'<form action="/auth/logout" method="post" class="plx-logout"><input type="hidden" name="csrf" value="{csrf}"><button>PLX abmelden</button></form>'
            self.respond(200, '<!doctype html><html lang="de"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>PLX</title><style>body{margin:0;background:white}.plx-logout{max-width:1280px;margin:12px auto;padding:0 12px;text-align:right}.plx-logout button{border:1px solid #ddd;background:white;color:#62656b;border-radius:5px;padding:7px 12px;cursor:pointer}</style></head><body>' + content + logout + '</body></html>')
            return
        assets = {'/app.css': 'text/css; charset=utf-8', '/app.js': 'text/javascript; charset=utf-8', '/logo.svg': 'image/svg+xml'}
        if path.path in assets:
            self.respond(200, (self.app.root / 'webfrontend/htmlauth' / path.path[1:]).read_bytes(), assets[path.path])
            return
        self.respond(404, 'Nicht gefunden.')

    def image(self, alias):
        try:
            config = json.loads((self.app.data / 'config/settings.json').read_text())
            vehicle = next(v for v in config['vehicles'] if v['alias'] == alias)
            filename = 'vehicle-' + hashlib.sha256(vehicle['vin'].encode()).hexdigest() + '.image'
            path = self.app.data / 'runtime' / filename
            if path.stat().st_size > 2000000:
                raise ValueError()
            blob = path.read_bytes()
            mime = 'image/png' if blob.startswith(b'\x89PNG\r\n\x1a\n') else 'image/jpeg' if blob.startswith(b'\xff\xd8\xff') else 'image/webp' if blob[:4] == b'RIFF' and blob[8:12] == b'WEBP' else None
            if mime:
                self.respond(200, blob, mime)
                return
        except (OSError, ValueError, KeyError, StopIteration, TypeError):
            pass
        self.respond(404, 'Bild nicht verfügbar.')

    def do_POST(self):
        path = urlsplit(self.path)
        if not self.same_origin():
            self.json_error(403, 'Ungültiger Ursprung.')
            return
        try:
            body = self.read_body()
        except (ValueError, OSError):
            self.json_error(413, 'Ungültige Anfragegröße.')
            return
        if path.path == '/auth/login':
            try:
                form = parse_qs(body.decode(), max_num_fields=3)
                token = self.app.authenticate(self.client_address[0], form.get('username', [''])[0], form.get('password', [''])[0])
            except (ValueError, UnicodeError):
                token = None
            if not token:
                self.login_page('Anmeldung nicht möglich. Zugangsdaten prüfen oder eine Minute warten.')
                return
            self.respond(303, headers={'Location': '/', 'Set-Cookie': f'plx_session={token}; Path=/; HttpOnly; Secure; SameSite=Strict; Max-Age=28800'})
            return
        token = self.token()
        csrf = self.app.session(token)
        if not csrf:
            self.json_error(401, 'Bitte erneut bei PLX anmelden und die Seite neu laden.')
            return
        if path.path == '/auth/logout':
            try:
                submitted = parse_qs(body.decode(), max_num_fields=2).get('csrf', [''])[0]
            except (ValueError, UnicodeError):
                submitted = ''
            if not hmac.compare_digest(csrf, submitted):
                self.json_error(403, 'Ungültige Anfrage.')
                return
            with self.app.lock:
                self.app.sessions.pop(token, None)
            self.respond(303, headers={'Location': '/', 'Set-Cookie': 'plx_session=; Path=/; HttpOnly; Secure; SameSite=Strict; Max-Age=0'})
            return
        if path.path != '/index.php' or parse_qs(path.query).get('api') != ['1']:
            self.json_error(404, 'Nicht gefunden.')
            return
        if not hmac.compare_digest(csrf, self.headers.get('X-CSRF-Token', '')):
            self.json_error(403, 'Ungültige Anfrage. Bitte Seite neu laden.')
            return
        try:
            if self.headers.get_content_type() != 'application/json':
                raise ValueError()
            request = json.loads(body)
            if not isinstance(request, dict) or request.get('action') not in ACTIONS or not isinstance(request.get('params', {}), dict):
                raise ValueError()
        except (ValueError, TypeError):
            self.json_error(400, 'Diese Anfrage wird nicht unterstützt.')
            return
        try:
            self.respond(200, self.app.command(request), 'application/json; charset=utf-8')
        except (OSError, ValueError):
            self.json_error(503, 'PLX-Dienst momentan nicht erreichbar.')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--data-dir', type=Path, default=Path('/data'))
    parser.add_argument('--root', type=Path, default=Path('/app'))
    parser.add_argument('--host', default='0.0.0.0')
    parser.add_argument('--port', type=int, default=8443)
    args = parser.parse_args()
    os.umask(0o077)
    from .bootstrap import configured_host, web_password, prepare_tls
    try:
        host = configured_host()
        cert, key = prepare_tls(args.data_dir, host)
        password = web_password(args.data_dir)
        app = Application(args.root, args.data_dir, os.environ.get('PLX_USERNAME', 'admin'), password)
        del password
        context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        context.minimum_version = ssl.TLSVersion.TLSv1_2
        context.load_cert_chain(cert, key)
    except (ValueError, OSError, subprocess.SubprocessError):
        # Deliberate validation messages contain no entered value or secret.
        error = sys.exc_info()[1]
        message = str(error) if isinstance(error, ValueError) else 'PLX-Start fehlgeschlagen. Datenrechte sowie Zertifikat/Schlüssel prüfen.'
        parser.error(message)
    server = Server((args.host, args.port), app, context)
    app.worker = subprocess.Popen([sys.executable, '-m', 'porsche2lox.service', '--config-dir', str(args.data_dir / 'config'), '--data-dir', str(args.data_dir / 'runtime')])
    def shutdown(*_):
        threading.Thread(target=server.shutdown, daemon=True).start()
    for sig in (signal.SIGTERM, signal.SIGINT):
        signal.signal(sig, shutdown)
    def monitor():
        app.worker.wait()
        shutdown()
    threading.Thread(target=monitor, daemon=True).start()
    try:
        print('PLX HTTPS bereit auf Port ' + str(args.port), flush=True)
        server.serve_forever(poll_interval=0.25)
    finally:
        server.server_close()
        if app.worker.poll() is None:
            app.worker.terminate()
            try:
                app.worker.wait(timeout=30)
            except subprocess.TimeoutExpired:
                app.worker.kill()
                app.worker.wait()
    if app.worker.returncode not in (0, -signal.SIGTERM):
        raise SystemExit(1)


if __name__ == '__main__':
    main()
