import asyncio
import copy
import json
from unittest.mock import MagicMock

from porsche2lox.core import validate_config
from porsche2lox.mqtt import BrokerMonitor
from test_service import service, configured


def test_offline_deselection_persists_and_retry_survives_restart(tmp_path):
    async def run():
        def offline(*_):
            raise ConnectionRefusedError(111, 'secret must not reach view')
        app, _ = service(tmp_path, offline)
        app.config = validate_config(configured())
        app.config['mqtt']['enabled'] = True
        new = copy.deepcopy(app.config)
        new['publish_fields'] = []
        new['publish_parameters'] = []
        result = await app.command({'action': 'save', 'params': new})
        assert result['mqtt_cleanup_pending']
        assert json.loads(app.config_path.read_text())['publish_fields'] == []
        await app.retry_cleanup()
        assert app.mqtt_error == 'unreachable'
        assert 'secret must not' not in json.dumps(app.view())
        calls = []
        restarted, _ = service(tmp_path, lambda c, p: calls.append(p))
        await restarted.retry_cleanup()
        assert calls and not restarted.pending_cleanup
    asyncio.run(run())


def test_reselection_cancels_pending_deletion_and_preserves_current_value(tmp_path):
    async def run():
        calls=[]
        app,_=service(tmp_path, lambda c,p:calls.extend(p))
        app.config=validate_config(configured())
        app.config['mqtt']['enabled']=True
        old=copy.deepcopy(app.config)
        new=copy.deepcopy(old);new['publish_fields']=[]
        await app.command({'action':'save','params':new})
        await app.command({'action':'save','params':old})
        await app.retry_cleanup()
        assert not calls and not app.pending_cleanup
    asyncio.run(run())


def test_monitor_requires_connack_tracks_disconnect_and_ignores_old_callbacks(monkeypatch):
    clients=[]
    def make(*_):
        c=MagicMock();clients.append(c);return c
    monkeypatch.setattr('porsche2lox.mqtt.mqtt.Client',make)
    monitor=BrokerMonitor()
    c=validate_config(configured())['mqtt'];c['enabled']=True
    monitor.configure(c)
    first=clients[0]
    assert monitor.view()['state']=='connecting'
    ok=MagicMock(is_failure=False)
    first.on_connect(first,None,None,ok,None)
    assert monitor.view()['state']=='connected'
    first.on_disconnect(first,None,None,ok,None)
    assert monitor.view()['state']=='disconnected'
    denied=MagicMock(is_failure=True,value=135)
    first.on_connect(first,None,None,denied,None)
    assert monitor.view()=={'state':'error','error':'auth'}
    monitor.configure(dict(c,host='other.example'))
    first.on_connect(first,None,None,ok,None)
    assert monitor.view()['state']=='connecting'
    monitor.close()
    assert monitor.view()['state']=='disabled'
