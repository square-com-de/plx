"""Read-only adapter. No vehicle command methods are exposed or imported."""
from __future__ import annotations

import asyncio
import logging
import os
from urllib.parse import urlsplit
import time
from pathlib import Path

import httpx
from pyporscheconnectapi.connection import Connection
from pyporscheconnectapi.exceptions import PorscheCaptchaRequiredError
from pyporscheconnectapi.oauth2 import Captcha, Credentials

from .core import read_json, write_private
from .parameters import READ_MEASUREMENTS

# Upstream logs include tokens, raw responses and authorization codes.
for name in ("pyporscheconnectapi", "httpx", "httpcore"):
    logging.getLogger(name).disabled = True
    logging.getLogger(name).setLevel(logging.CRITICAL + 1)
    logging.getLogger(name).addHandler(logging.NullHandler())
    logging.getLogger(name).propagate = False


class SessionExpired(Exception):
    pass


class StatusConnection(Connection):
    def __init__(self, session_path, **kwargs):
        self.session_path = session_path
        super().__init__(**kwargs)

    async def request(self, method, url, **kwargs):
        if method != "GET":
            raise PermissionError("PLX unterstützt ausschließlich Statusabfragen.")
        # Persist refreshed tokens BEFORE an API request or data validation can fail.
        async with self.token_lock:
            try:
                await self.oauth2_client.ensure_valid_token(self.token)
            finally:
                if self.token.get("access_token"):
                    write_private(self.session_path, dict(self.token))
        return await super().request(method, url, **kwargs)


class Porsche:
    def __init__(self, session_path: Path):
        self.session_path = session_path
        self.pending = None
        self.deadline = 0
        self.captcha = None

    def _connection(self, **kwargs):
        return StatusConnection(self.session_path, async_client=httpx.AsyncClient(), **kwargs)

    async def cancel_login(self):
        if self.pending:
            self.pending.oauth2_client.credentials = Credentials(None, None)
            self.pending.oauth2_client.captcha = Captcha(None, None)
            self.pending.oauth2_client.code_verifier = None
            await self.pending.close()
        self.pending = None
        self.captcha = None
        self.deadline = 0

    async def expire_login(self):
        if self.pending and time.monotonic() >= self.deadline:
            await self.cancel_login()

    async def login(self, email=None, password=None, code=None):
        await self.expire_login()
        if code is None:
            await self.cancel_login()
            if not isinstance(email, str) or "@" not in email or len(email) > 254:
                raise ValueError("Bitte eine gültige Porsche-ID eingeben.")
            if not isinstance(password, str) or not password or len(password) > 2048:
                raise ValueError("Bitte das Porsche-Passwort eingeben.")
            self.pending = self._connection(email=email, password=password)
            self.deadline = time.monotonic() + 300
        elif not self.pending or not self.captcha:
            raise ValueError("Anmeldung abgelaufen. Bitte erneut anmelden.")
        else:
            if not isinstance(code, str) or not 1 <= len(code) <= 128:
                raise ValueError("Bitte den CAPTCHA-Code eingeben.")
            oauth = self.pending.oauth2_client
            oauth.captcha = Captcha(code, self.captcha.state)
            oauth.code_verifier = self.captcha.code_verifier
        try:
            async with asyncio.timeout(110):
                token = await self.pending.get_token()
            write_private(self.session_path, dict(token))
            await self.cancel_login()
            return {"state": "authenticated"}
        except PorscheCaptchaRequiredError as exc:
            self.captcha = exc
            return {"state": "captcha", "image": exc.captcha}
        except BaseException:
            await self.cancel_login()
            raise

    async def connection(self):
        try:
            token = read_json(self.session_path, {})
        except (ValueError, OSError) as exc:
            raise SessionExpired() from exc
        if not isinstance(token, dict):
            raise SessionExpired()
        if not token.get("access_token") or not token.get("refresh_token"):
            raise SessionExpired()
        return self._connection(token=token)

    async def vehicles(self):
        connection = await self.connection()
        try:
            async with asyncio.timeout(110):
                result = await connection.get("/connect/v1/vehicles")
            if not isinstance(result, list):
                raise ValueError("Ungültige Fahrzeugliste von Porsche.")
            return [{"vin": v["vin"], "name": str(v.get("customName") or v.get("modelName") or "Porsche")[:80]}
                    for v in result if isinstance(v, dict) and isinstance(v.get("vin"), str)]
        finally:
            await connection.close()

    async def cache_picture(self, vin, destination):
        """Cache an optional model picture; never send OAuth tokens to the CDN."""
        if destination.exists() and time.time() - destination.stat().st_mtime < 86400:
            return
        connection = await self.connection()
        try:
            async with asyncio.timeout(30):
                pictures = await connection.get(f"/connect/v1/vehicles/{vin}/pictures")
        finally:
            await connection.close()
        if not isinstance(pictures, list):
            return
        picture = next((p for p in pictures if isinstance(p, dict) and p.get('view') == 'frontView'), None)
        if not picture:
            return
        url = picture.get('url', '')
        parsed = urlsplit(url)
        if parsed.scheme != 'https' or parsed.hostname != 'cdn.pdg-viz-picserv2.pdcp.porsche.digital' or parsed.username or parsed.password or parsed.port not in (None, 443):
            return
        async with httpx.AsyncClient(timeout=30, follow_redirects=False) as client:
            async with client.stream('GET', url) as response:
                response.raise_for_status()
                content = bytearray()
                async for chunk in response.aiter_bytes():
                    content.extend(chunk)
                    if len(content) > 2_000_000:
                        return
        if not (content.startswith(b'\x89PNG\r\n\x1a\n') or content.startswith(b'\xff\xd8\xff') or (content[:4] == b'RIFF' and content[8:12] == b'WEBP')):
            return
        temporary = destination.with_suffix('.tmp')
        try:
            with temporary.open('wb') as output:
                os.chmod(temporary, 0o600)
                output.write(content)
            os.replace(temporary, destination)
        finally:
            temporary.unlink(missing_ok=True)

    async def overview(self, vin):
        connection = await self.connection()
        try:
            async with asyncio.timeout(110):
                return await connection.get(
                    f"/connect/v1/vehicles/{vin}",
                    params=[("mf", key) for key in READ_MEASUREMENTS],
                )
        finally:
            await connection.close()

    async def close(self):
        await self.cancel_login()
