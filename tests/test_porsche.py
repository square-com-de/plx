import asyncio
import time
import base64
import hashlib
from urllib.parse import parse_qs
from pathlib import Path
from unittest.mock import AsyncMock

import httpx
import pytest
from pyporscheconnectapi.exceptions import PorscheCaptchaRequiredError, PorscheExceptionError
from pyporscheconnectapi.oauth2 import OAuth2Token

from porsche2lox.core import read_json
from porsche2lox.porsche import Porsche, StatusConnection
from porsche2lox.service import error_code


def test_refresh_persisted_even_when_read_fails(tmp_path):
    async def run():
        async def response(request):
            assert request.method == 'GET'
            assert 'wakeUpJob' not in str(request.url)
            return httpx.Response(401, text='unauthorized')
        async with httpx.AsyncClient(transport=httpx.MockTransport(response)) as client:
            connection = StatusConnection(tmp_path / 'session.json', async_client=client, token={'access_token':'old','refresh_token':'refresh','expires_at':1})
            async def refresh(token):
                token.update(access_token='new', refresh_token='rotated', expires_at=int(time.time())+3600)
            connection.oauth2_client.ensure_valid_token = refresh
            with pytest.raises(PorscheExceptionError):
                await connection.get('/connect/v1/vehicles')
            assert read_json(tmp_path / 'session.json')['refresh_token'] == 'rotated'
            with pytest.raises(PermissionError):
                await connection.post('/connect/v1/vehicles/fake/commands')
    asyncio.run(run())


def test_login_captcha_preserves_client_pkce_and_clears_password(tmp_path):
    async def run():
        adapter = Porsche(tmp_path / 'session.json')
        connection = adapter._connection(email='test@example.com', password='transient')
        connection.get_token = AsyncMock(side_effect=[PorscheCaptchaRequiredError('data:image/png;base64,AA==','state-123','verifier-123'), OAuth2Token({'access_token':'a','refresh_token':'r','expires_at':int(time.time())+3600})])
        connection.close = AsyncMock()
        adapter._connection = lambda **kwargs: connection
        result = await adapter.login('test@example.com','transient')
        assert result['state'] == 'captcha'
        assert adapter.pending is connection
        assert not (tmp_path/'session.json').exists()
        result = await adapter.login(code='1234')
        assert connection.oauth2_client.credentials.password is None
        assert connection.oauth2_client.code_verifier is None
        assert result['state'] == 'authenticated'
        assert adapter.pending is None
        connection.close.assert_awaited_once()
        assert read_json(tmp_path/'session.json')['access_token'] == 'a'
    asyncio.run(run())


def test_login_expiry_closes_client(tmp_path):
    async def run():
        adapter = Porsche(tmp_path/'session.json')
        adapter.pending = AsyncMock()
        connection = adapter.pending
        adapter.deadline = 1
        await adapter.expire_login()
        assert adapter.pending is None
        connection.close.assert_awaited_once()
        with pytest.raises(ValueError):
            await adapter.login(code='123')
    asyncio.run(run())


def test_real_oauth_flow_with_captcha_and_cookie_continuity(tmp_path):
    async def run():
        calls, verifier = [], {}
        async def respond(request):
            calls.append(request)
            data = parse_qs(request.content.decode())
            if request.url.path == '/authorize':
                verifier['challenge'] = request.url.params['code_challenge']
                return httpx.Response(302, headers={'Location':'https://identity.porsche.com/u/login/identifier?state=transaction', 'Set-Cookie':'flow=same-client; Path=/; Secure'})
            assert request.headers.get('cookie') == 'flow=same-client'
            if request.url.path == '/u/login/identifier':
                if 'captcha' not in data:
                    return httpx.Response(400, text='<img alt="captcha" src="data:image/png;base64,AA==">')
                assert data['captcha'] == ['1234']
                assert data['state'] == ['transaction']
                return httpx.Response(302, headers={'Location':'/u/login/password'})
            if request.url.path == '/u/login/password':
                assert data['password'] == ['test-password']
                return httpx.Response(302, headers={'Location':'/authorize/resume'})
            if request.url.path == '/authorize/resume':
                return httpx.Response(302, headers={'Location':'my-porsche-app://auth0/callback?code=test-code'})
            if request.url.path == '/oauth/token':
                digest = hashlib.sha256(data['code_verifier'][0].encode()).digest()
                assert base64.urlsafe_b64encode(digest).rstrip(b'=').decode() == verifier['challenge']
                return httpx.Response(200, json={'access_token':'local-test-access','refresh_token':'local-test-refresh','expires_in':3600})
            raise AssertionError(str(request.url))
        adapter = Porsche(tmp_path/'session.json')
        adapter._connection = lambda **kwargs: StatusConnection(adapter.session_path, async_client=httpx.AsyncClient(transport=httpx.MockTransport(respond)), **kwargs)
        assert (await adapter.login('test@example.com','test-password'))['state'] == 'captcha'
        assert (await adapter.login(code='1234'))['state'] == 'authenticated'
        assert adapter.pending is None
        assert read_json(adapter.session_path)['refresh_token'] == 'local-test-refresh'
        assert len(calls) == 6
    asyncio.run(run())


@pytest.mark.parametrize('status,body,expected', [(401,None,3), (400,'{"error":"invalid_grant"}',3), (429,None,4), (423,None,6), (503,None,1)])
def test_auth_error_uses_structured_exception(status, body, expected):
    assert error_code(PorscheExceptionError(status,response_body=body)) == expected


def test_picture_cache_is_optional_private_and_reuses_file(tmp_path, monkeypatch):
    async def run():
        client_type = httpx.AsyncClient
        png = b'\x89PNG\r\n\x1a\n' + b'test'
        requests = []
        def respond(request):
            requests.append(request)
            assert 'authorization' not in request.headers
            return httpx.Response(200, content=png)
        monkeypatch.setattr('porsche2lox.porsche.httpx.AsyncClient', lambda **kwargs: client_type(transport=httpx.MockTransport(respond), **kwargs))
        porsche = Porsche(tmp_path/'session.json')
        connection = AsyncMock()
        connection.get.return_value = [{'view':'frontView','url':'https://cdn.pdg-viz-picserv2.pdcp.porsche.digital/model.png'}]
        porsche.connection = AsyncMock(return_value=connection)
        target = tmp_path/'model.image'
        await porsche.cache_picture('test', target)
        assert target.read_bytes() == png
        assert target.stat().st_mode & 0o777 == 0o600
        await porsche.cache_picture('test', target)
        assert len(requests) == 1
    asyncio.run(run())


@pytest.mark.parametrize('url', ['http://cdn.pdg-viz-picserv2.pdcp.porsche.digital/a', 'https://127.0.0.1/a', 'https://cdn.pdg-viz-picserv2.pdcp.porsche.digital.evil.test/a'])
def test_picture_cache_rejects_untrusted_urls(tmp_path, url):
    async def run():
        porsche = Porsche(tmp_path/'session.json')
        connection = AsyncMock()
        connection.get.return_value = [{'view':'frontView','url':url}]
        porsche.connection = AsyncMock(return_value=connection)
        target = tmp_path/'model.image'
        await porsche.cache_picture('test', target)
        assert not target.exists()
    asyncio.run(run())
