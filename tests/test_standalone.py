import hashlib
import http.client
import json
from pathlib import Path
import threading
from urllib.parse import urlencode

import pytest

from porsche2lox.standalone import Application, Server

PASSWORD = 'independent-test-password-123'


@pytest.fixture
def site(tmp_path):
    root = Path(__file__).resolve().parents[1]
    app = Application(root, tmp_path, 'admin', PASSWORD)
    calls = []
    def command(request):
        calls.append(request)
        return b'{"ok":true,"data":{"sentinel":"own-service"}}\n'
    app.command = command
    server = Server(('127.0.0.1', 0), app)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    def request(method, path, body=None, headers=None):
        connection = http.client.HTTPConnection(*server.server_address, timeout=5)
        connection.request(method, path, body=body, headers=headers or {})
        reply = connection.getresponse()
        result = reply.status, dict(reply.getheaders()), reply.read()
        connection.close()
        return result
    yield app, calls, request
    server.shutdown()
    server.server_close()
    thread.join()


def login(request):
    status, headers, _ = request('POST', '/auth/login', urlencode({'username': 'admin', 'password': PASSWORD}), {'Content-Type': 'application/x-www-form-urlencoded'})
    assert status == 303
    assert all(x in headers['Set-Cookie'] for x in ['HttpOnly', 'Secure', 'SameSite=Strict'])
    cookie = headers['Set-Cookie'].split(';')[0]
    status, _, body = request('GET', '/', headers={'Cookie': cookie})
    assert status == 200
    csrf = body.decode().split('data-csrf="')[1].split('"')[0]
    return cookie, csrf


def test_authentication_and_no_private_static_access(site):
    app, calls, request = site
    for path in ['/', '/app.js', '/index.php?image=taycan', '/../../runtime/session.json']:
        status, _, body = request('GET', path)
        assert status == 401
        assert b'PLX-Passwort' in body
    cookie, csrf = login(request)
    status, headers, body = request('GET', '/', headers={'Cookie': cookie})
    assert b'Dein Porsche x Loxone in Deinem intelligenten Zuhause.' in body
    assert b'<?= $csrf ?>' not in body
    assert 'frame-ancestors' in headers['Content-Security-Policy']
    assert headers['Referrer-Policy'] == 'same-origin'
    assert request('GET', '/app.js', headers={'Cookie': cookie})[0] == 200
    assert request('GET', '/runtime/session.json', headers={'Cookie': cookie})[0] == 404
    assert not calls


def test_api_csrf_origin_allowlist_and_size(site):
    app, calls, request = site
    body = json.dumps({'action': 'status', 'params': {}})
    assert request('POST', '/index.php?api=1', body)[0] == 401
    cookie, csrf = login(request)
    headers = {'Cookie': cookie, 'Content-Type': 'application/json'}
    assert request('POST', '/index.php?api=1', body, headers)[0] == 403
    headers['X-CSRF-Token'] = csrf
    headers['Origin'] = 'https://evil.example'
    assert request('POST', '/index.php?api=1', body, headers)[0] == 403
    del headers['Origin']
    assert request('POST', '/index.php?api=1', body, headers)[0] == 200
    assert calls == [{'action': 'status', 'params': {}}]
    assert request('POST', '/index.php?api=1', '{"action":"unlock"}', headers)[0] == 400
    assert request('POST', '/index.php?api=1', '{"action":"save","params":[]}', headers)[0] == 400
    assert request('POST', '/index.php?api=1', 'x' * 30001, headers)[0] == 413
    assert len(calls) == 1


def test_web_logout_keeps_porsche_session(site):
    app, calls, request = site
    cookie, csrf = login(request)
    assert request('POST', '/auth/logout', 'csrf=invalid', {'Cookie': cookie})[0] == 403
    assert request('POST', '/auth/logout', urlencode({'csrf': csrf}), {'Cookie': cookie})[0] == 303
    assert request('GET', '/', headers={'Cookie': cookie})[0] == 401
    assert calls == []


def test_login_limit_and_session_expiry(site):
    app, calls, request = site
    for _ in range(5):
        assert request('POST', '/auth/login', 'username=admin&password=wrong')[0] == 401
    assert request('POST', '/auth/login', urlencode({'username': 'admin', 'password': PASSWORD}))[0] == 401
    with app.lock:
        app.sessions['expired'] = (0, 'csrf')
    assert app.session('expired') is None
    assert 'expired' not in app.sessions
    assert not calls


def test_images_only_configured_aliases_and_valid_images(site):
    app, calls, request = site
    cookie, _ = login(request)
    (app.data / 'config').mkdir()
    (app.data / 'runtime').mkdir()
    (app.data / 'config/settings.json').write_text(json.dumps({'vehicles': [{'vin': 'test-vin', 'alias': 'own'}]}))
    image = app.data / 'runtime' / ('vehicle-' + hashlib.sha256(b'test-vin').hexdigest() + '.image')
    image.write_bytes(b'\x89PNG\r\n\x1a\nprivate-picture')
    status, headers, body = request('GET', '/index.php?image=own', headers={'Cookie': cookie})
    assert status == 200 and headers['Content-Type'] == 'image/png'
    assert request('GET', '/index.php?image=other', headers={'Cookie': cookie})[0] == 404
    image.write_bytes(b'<script>unsafe</script>')
    assert request('GET', '/index.php?image=own', headers={'Cookie': cookie})[0] == 404


def test_no_default_password_and_separate_data(tmp_path):
    with pytest.raises(ValueError):
        Application(tmp_path, tmp_path, 'admin', 'short')
    app = Application(tmp_path, tmp_path, 'admin', PASSWORD)
    assert not app.ready()
