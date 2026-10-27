"""Icon routes must work before login without exposing private assets."""
from pathlib import Path
import struct

import pytest
from test_standalone import site, login


@pytest.mark.parametrize('name,mime', [('favicon.png','image/png'),('favicon.ico','image/vnd.microsoft.icon'),('apple-touch-icon.png','image/png')])
def test_public_icon_route_has_exact_content_and_mime(site, name, mime):
    app, calls, request = site
    status, headers, body = request('GET', '/'+name+'?v=plx-x1')
    assert status == 200
    assert headers['Content-Type'] == mime
    assert 'Location' not in headers and 'Set-Cookie' not in headers
    assert body == (app.root/'webfrontend/htmlauth'/name).read_bytes()
    assert not calls
    assert request('GET', '/index.php?image=private-car')[0] == 401


def test_icons_declared_on_both_login_and_app(site):
    app, calls, request = site
    status, _, body = request('GET', '/')
    assert status == 401
    cookie, _ = login(request)
    _, _, page = request('GET', '/', headers={'Cookie':cookie})
    for content in [body, page]:
        head = content.decode().split('<style>', 1)[0]
        for name in ('favicon.png','favicon.ico','apple-touch-icon.png'):
            assert name+'?v=plx-x1' in head


def test_transparent_png_and_multisize_ico_exports():
    root = Path(__file__).resolve().parents[1]/'webfrontend/htmlauth'
    for name, size in [('favicon.png',32),('apple-touch-icon.png',180)]:
        png=(root/name).read_bytes()
        assert png[:8] == b'\x89PNG\r\n\x1a\n'
        assert struct.unpack('>II',png[16:24]) == (size,size)
        assert png[25] == 6  # RGBA; transparent background retained.
    ico=(root/'favicon.ico').read_bytes()
    assert struct.unpack('<HHH',ico[:6]) == (0,1,3)
    for i,size in enumerate([16,32,48]):
        entry=ico[6+i*16:22+i*16]
        assert tuple(entry[:2]) == (size,size)
        length,offset=struct.unpack('<II',entry[8:16])
        assert ico[offset:offset+8] == b'\x89PNG\r\n\x1a\n'
        assert offset+length <= len(ico)
