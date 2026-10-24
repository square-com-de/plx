import asyncio
import copy
import json
import time
from unittest.mock import AsyncMock

import pytest
from pyporscheconnectapi.exceptions import PorscheExceptionError

from porsche2lox.core import DEFAULTS
from porsche2lox.service import Service
from test_core import VIN, payload


def service(tmp_path, publisher=lambda *_: None):
    adapter = AsyncMock()
    adapter.pending = None
    adapter.overview.return_value = payload(timestamp=None)
    app = Service(tmp_path/'config', tmp_path/'data', adapter=adapter, publisher=publisher)
    app.vehicles = [{'vin':VIN,'name':'Testwagen'}]
    return app, adapter


def configured():
    config = copy.deepcopy(DEFAULTS)
    config["mqtt_format"] = "detailed"  # Compatibility scenarios retain legacy format.
    config['enabled'] = True
    config['vehicles'] = [{'vin':VIN,'alias':'taycan'}]
    return config


def test_disabled_start_never_contacts_cloud(tmp_path):
    async def run():
        app, adapter = service(tmp_path)
        task = asyncio.create_task(app.tick())
        await asyncio.sleep(.02)
        app.stopping.set()
        await task
        adapter.overview.assert_not_awaited()
        adapter.vehicles.assert_not_awaited()
    asyncio.run(run())


def test_auth_failure_blocks_all_vehicles_and_preserves_last_value(tmp_path):
    async def run():
        app, adapter = service(tmp_path)
        app.config = configured()
        app.snapshots = {'taycan':{'soc':55,'api_ok':1,'data_valid':1}}
        adapter.overview.side_effect = PorscheExceptionError(401)
        await app.poll()
        assert app.auth_blocked
        assert app.snapshots['taycan']['soc'] == 55
        assert app.snapshots['taycan']['data_valid'] == 0
        assert app.snapshots['taycan']['auth_required'] == 1
        with pytest.raises(ValueError):
            await app.command({'action':'poll'})
    asyncio.run(run())


def test_unknown_timestamp_fetch_ok_but_invalid(tmp_path):
    async def run():
        app, _ = service(tmp_path)
        app.config = configured()
        await app.poll()
        value = app.view()['snapshots']['taycan']
        assert value['soc'] == 42
        assert value['api_ok'] == 1
        assert value['data_valid'] == 0
        assert value['age_known'] == 0
    asyncio.run(run())


def test_save_masks_password_preserves_session_and_never_uses_old_paths(tmp_path):
    async def run():
        app, _ = service(tmp_path)
        config = configured()
        config['mqtt']['password'] = 'a-test-secret'
        result = await app.command({'action':'save','params':config})
        assert 'a-test-secret' not in json.dumps(result)
        assert result['config']['mqtt']['password_set']
        config['mqtt']['password'] = None
        await app.command({'action':'save','params':config})
        assert app.config['mqtt']['password'] == 'a-test-secret'
        assert 'a-test-secret' in app.config_path.read_text()
    asyncio.run(run())


def test_mqtt_failure_does_not_poison_porsche_auth(tmp_path):
    async def run():
        def fail(*_): raise ConnectionError()
        app, _ = service(tmp_path, fail)
        app.config = configured()
        app.config['mqtt']['enabled'] = True
        await app.poll()
        assert app.mqtt_ok is False
        assert app.snapshots['taycan']['api_ok'] == 1
        assert not app.auth_blocked
        assert app.job['error_code'] == 5
    asyncio.run(run())


def test_rate_limit_backoff_and_manual_throttle(tmp_path):
    async def run():
        app, adapter = service(tmp_path)
        app.config = configured()
        adapter.overview.side_effect = PorscheExceptionError(429)
        await app.poll()
        assert app.next_poll - time.time() > 3590
        with pytest.raises(ValueError):
            app.launch('poll', {})
    asyncio.run(run())


def test_busy_rejects_config_change(tmp_path):
    async def run():
        app, _ = service(tmp_path)
        app.task = asyncio.create_task(asyncio.sleep(20))
        with pytest.raises(ValueError):
            await app.command({'action':'save','params':configured()})
        app.task.cancel()
        await asyncio.gather(app.task, return_exceptions=True)
    asyncio.run(run())


def test_logout_deletes_only_own_session_and_invalidates(tmp_path):
    async def run():
        app, _ = service(tmp_path)
        app.config = configured()
        path = app.data_dir/'session.json'
        path.write_text('{"test":true}')
        await app.command({'action':'logout'})
        await app.task
        assert not path.exists()
        assert app.snapshots['taycan']['auth_required'] == 1
        assert app.login['state'] == 'signed_out'
    asyncio.run(run())


def test_manual_poll_without_automatic_polling(tmp_path):
    async def run():
        app, adapter = service(tmp_path)
        app.config = configured()
        app.config['enabled'] = False
        await app.command({'action':'poll','params':{}})
        await app.task
        adapter.overview.assert_awaited_once_with(VIN)
        assert app.view()['snapshots']['taycan']['soc'] == 42
        assert app.config['enabled'] is False
    asyncio.run(run())
