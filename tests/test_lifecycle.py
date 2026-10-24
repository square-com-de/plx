import os
import shutil
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]


def test_package_allowlist_and_template_contract():
    import importlib.util
    spec = importlib.util.spec_from_file_location('builder', ROOT/'tools/build.py')
    builder = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(builder)
    assert not {'runtime','.venv','tests'} & set(builder.INCLUDE)
    assert (ROOT/'webfrontend/htmlauth/index.cgi').is_file()
    for path in ('postinstall.sh','postroot.sh','uninstall/uninstall.sh'):
        text = (ROOT/path).read_text()
        assert '${3:?' in text
        assert 'porsche-taycan' not in text
        assert '/opt/loxberry/data/porsche' not in text


@pytest.mark.skipif(os.geteuid() != 0 or not shutil.which('systemd-analyze'), reason='Isolated Linux integration container only')
def test_root_hook_suffix_generated_unit_and_uninstall(tmp_path):
    env = dict(os.environ)
    # Test namespace exclusively inside a disposable container.
    for key, sub in [('LBPBIN','bin'),('LBPDATA','data'),('LBPCONFIG','config')]:
        env[key] = str(tmp_path/sub)
        (tmp_path/sub/'porsche2lox01').mkdir(parents=True)
    fake = tmp_path/'fake'
    fake.mkdir()
    calls = tmp_path/'systemctl-calls'
    (fake/'systemctl').write_text('#!/bin/sh\nprintf "%s\\n" "$*" >> "$P2L_CALLS"\n')
    (fake/'systemctl').chmod(0o755)
    env.update(PATH=f'{fake}:{env["PATH"]}', P2L_CALLS=str(calls))
    unit = Path('/etc/systemd/system/porsche2lox-porsche2lox01.service')
    settings = tmp_path/'config/porsche2lox01/settings.json'
    settings.write_text('{"preserved":true}')
    session = tmp_path/'data/porsche2lox01/session.json'
    session.write_text('{"private":"test-only"}')
    try:
        subprocess.run(['bash',str(ROOT/'postroot.sh'),'temp','porsche2lox','porsche2lox01','0.1.0'],env=env,check=True,capture_output=True)
        text = unit.read_text()
        assert f'--data-dir {tmp_path}/data/porsche2lox01' in text
        assert 'User=loxberry' in text and 'ProtectSystem=strict' in text
        assert settings.read_text() == '{"preserved":true}'
        assert session.read_text() == '{"private":"test-only"}'
        assert 'restart porsche2lox-porsche2lox01.service' in calls.read_text()
        subprocess.run(['bash',str(ROOT/'uninstall/uninstall.sh'),'temp','porsche2lox','porsche2lox01','0.1.0'],env=env,check=True)
        assert not unit.exists()
        assert settings.exists() and session.exists()  # Removal belongs to LoxBerry.
        assert 'porsche-taycan' not in calls.read_text()
    finally:
        unit.unlink(missing_ok=True)
