"""Integration tests against real PHP, a Unix socket and a local Mosquitto.

The PHP SDK stubs are deliberately test-only; no real LoxBerry instance is used.
"""
import asyncio
import json
import os
import re
import shutil
import socket
import subprocess
import sys
import time
from pathlib import Path

import httpx
import pytest

from porsche2lox.mqtt import publish
from test_core import VIN, payload

ROOT = Path(__file__).resolve().parents[1]
pytestmark = pytest.mark.skipif(not shutil.which('php') or not shutil.which('mosquitto'), reason='Linux integration image required')


def port():
    with socket.socket() as s:
        s.bind(('127.0.0.1', 0))
        return s.getsockname()[1]


def test_real_mqtt_retained_and_deletion(tmp_path):
    broker_port = port()
    config = tmp_path/'mosquitto.conf'
    config.write_text(f'listener {broker_port} 127.0.0.1\nallow_anonymous true\n')
    proc = subprocess.Popen(['mosquitto','-c',str(config)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    try:
        for _ in range(100):
            with socket.socket() as s:
                if s.connect_ex(('127.0.0.1',broker_port)) == 0: break
            time.sleep(.02)
        mqtt = {'host':'127.0.0.1','port':broker_port,'username':'','password':'','tls':False}
        publish(mqtt, [('porsche2lox/test/soc','42')])
        result = subprocess.run(['mosquitto_sub','-h','127.0.0.1','-p',str(broker_port),'-t','porsche2lox/test/soc','-C','1','-W','2'],capture_output=True,text=True,check=True)
        assert result.stdout.strip() == '42'
        publish(mqtt, [('porsche2lox/test/soc','')])
        result = subprocess.run(['mosquitto_sub','-h','127.0.0.1','-p',str(broker_port),'-t','porsche2lox/test/soc','-C','1','-W','1'],capture_output=True,text=True)
        assert result.returncode != 0 and not result.stdout
    finally:
        proc.terminate()
        proc.wait(timeout=5)


def test_php_csrf_https_and_real_unix_socket(tmp_path):
    async def run():
        data, config = tmp_path/'data', tmp_path/'config'
        sdk = tmp_path/'sdk'
        sdk.mkdir()
        (sdk/'loxberry_system.php').write_text('<?php $lbpdatadir = getenv("P2L_DATA"); $lbptemplatedir = getenv("P2L_TEMPLATE");')
        (sdk/'loxberry_web.php').write_text('<?php class LBWeb {static function lbheader(...$args) {echo "<!doctype html><html><head><meta charset=\\\"utf-8\\\"></head><body>";} static function lbfooter(){echo "</body></html>";}}')
        router = tmp_path/'router.php'
        router.write_text('<?php if (!isset($_GET["unauthorized"])) {$_SERVER["REMOTE_USER"]="test-user";} $_SERVER["HTTPS"] = ($_SERVER["HTTP_X_TEST_HTTPS"] ?? "") === "1" ? "on" : "off"; return false;')
        env = dict(os.environ, P2L_DATA=str(data), P2L_TEMPLATE=str(ROOT/'templates'), PYTHONPATH=str(ROOT/'bin'))
        service = subprocess.Popen([sys.executable,'-m','porsche2lox.service','--data-dir',str(data),'--config-dir',str(config)], env=env, stdout=subprocess.DEVNULL,stderr=subprocess.PIPE)
        web_port = port()
        php = subprocess.Popen(['php','-d',f'include_path={sdk}','-S',f'127.0.0.1:{web_port}','-t',str(ROOT/'webfrontend/htmlauth'),str(router)],env=env,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
        try:
            async with httpx.AsyncClient(base_url=f'http://127.0.0.1:{web_port}') as client:
                for _ in range(150):
                    try:
                        response = await client.get('/index.php')
                        if response.status_code == 200 and (data/'control.sock').exists(): break
                    except httpx.ConnectError: pass
                    await asyncio.sleep(.02)
                assert response.status_code == 200
                csrf = re.search(r'data-csrf="([a-f0-9]+)"',response.text).group(1)
                assert 'PLX' in response.text
                assert (await client.get('/index.php?unauthorized=1')).status_code == 403
                assert (await client.post('/index.php?api=1',json={'action':'status'})).status_code == 403
                headers = {'X-CSRF-Token':csrf}
                reply = await client.post('/index.php?api=1',headers=headers,json={'action':'status'})
                state = reply.json()['data']
                assert state['config']['enabled'] is False
                assert 'password' not in state['config']['mqtt']
                denied = await client.post('/index.php?api=1',headers=headers,json={'action':'login','params':{'email':'test@example.com','password':'test'}})
                assert 'HTTPS' in denied.json()['error']
                status = await client.post('/index.php?api=1',headers=headers,json={'action':'honk'})
                assert not status.json()['ok']
                # No login reaches Porsche; the entire test is local.
                old_cookie='; '.join(k+'='+v for k,v in client.cookies.items())
                saved = await client.post('/index.php?api=1',headers={**headers,'X-Test-HTTPS':'1'},json={'action':'save','params':state['config']})
                assert saved.json()['ok']
                assert 'secure' in saved.headers['set-cookie'].lower() and 'httponly' in saved.headers['set-cookie'].lower()
                https_cookie='; '.join(k+'='+v for k,v in client.cookies.items())
                assert https_cookie != old_cookie
                stale = await client.post('/index.php?api=1',headers={**headers,'Cookie':old_cookie},json={'action':'status','params':{}})
                assert stale.status_code == 403
                # PHP must preserve {} as an object when forwarding to Python.
                cancelled = await client.post('/index.php?api=1',headers={**headers,'Cookie':https_cookie},json={'action':'cancel','params':{}})
                assert cancelled.json()['ok'], cancelled.text
                assert (config/'settings.json').stat().st_mode & 0o777 == 0o600
                assert (data/'control.sock').stat().st_mode & 0o777 == 0o600
        finally:
            php.terminate()
            service.terminate()
            php.wait(timeout=5)
            service.wait(timeout=30)
            assert service.returncode == 0, service.stderr.read().decode()
    asyncio.run(run())


def test_php_syntax():
    subprocess.run(['php','-l',str(ROOT/'webfrontend/htmlauth/index.php')],check=True)
