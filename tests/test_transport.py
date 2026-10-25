"""Run the same PHP transport policy as the LoxBerry frontend."""
from pathlib import Path
import shutil
import subprocess
import pytest

ROOT = Path(__file__).resolve().parents[1]

def test_proxy_transport_policy():
    php = shutil.which('php')
    if not php:
        pytest.skip('PHP required; also exercised on the LoxBerry acceptance VM')
    subprocess.run([php, str(ROOT/'tests/test_transport.php'), str(ROOT/'webfrontend/htmlauth/transport.php')], check=True)


def test_frontend_script_syntax():
    node = shutil.which('node')
    if not node:
        pytest.skip('Node required for frontend syntax check')
    subprocess.run([node, '--check', str(ROOT/'webfrontend/htmlauth/app.js')], check=True)
