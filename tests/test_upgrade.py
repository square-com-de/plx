"""Upgrade regression: LoxBerry purges both state trees between its hooks."""
import os
from pathlib import Path
import shutil
import stat
import subprocess

ROOT = Path(__file__).resolve().parents[1]


def test_preupgrade_survives_installer_purge_without_copying_runtime(tmp_path):
    config = tmp_path/'config';data = tmp_path/'data';stage = tmp_path/'stage'
    for directory in (config/'porsche2lox2', data/'porsche2lox2', stage):directory.mkdir(parents=True)
    (config/'porsche2lox2/settings.json').write_text('{"vehicles":["test"],"publish_parameters":["left","right"]}')
    (data/'porsche2lox2/session.json').write_text('{"test-session":"preserve"}')
    (data/'porsche2lox2/vehicle-test.image').write_bytes(b'image')
    (data/'porsche2lox2/venv').mkdir();(data/'porsche2lox2/venv/not-state').write_text('skip')
    (data/'porsche2lox2/service.lock').write_text('skip')
    outside=tmp_path/'outside';outside.write_text('must not package')
    (data/'porsche2lox2/unrelated-link').symlink_to(outside)
    env={**os.environ,'LBPCONFIG':str(config),'LBPDATA':str(data)}
    result=subprocess.run(['bash',str(ROOT/'preupgrade.sh'),'zip','porsche2lox','porsche2lox2','0.1.0',str(tmp_path),str(stage)],env=env,capture_output=True,text=True)
    assert result.returncode==0
    assert 'test-session' not in result.stdout
    shutil.rmtree(config);shutil.rmtree(data)
    shutil.copytree(stage/'config', config/'porsche2lox2');shutil.copytree(stage/'data',data/'porsche2lox2')
    assert 'left' in (config/'porsche2lox2/settings.json').read_text()
    assert 'preserve' in (data/'porsche2lox2/session.json').read_text()
    assert set(p.name for p in (data/'porsche2lox2').iterdir())=={'session.json','vehicle-test.image'}
    for path in (config/'porsche2lox2/settings.json',data/'porsche2lox2/session.json'):
        assert stat.S_IMODE(path.stat().st_mode)==0o600


def test_unknown_persistent_directory_stops_before_purge(tmp_path):
    config=tmp_path/'config';data=tmp_path/'data'
    (data/'porsche2lox/new-state-layout').mkdir(parents=True)
    env={**os.environ,'LBPCONFIG':str(config),'LBPDATA':str(data)}
    result=subprocess.run(['bash',str(ROOT/'preupgrade.sh'),'zip','porsche2lox','porsche2lox','0.1.0',str(tmp_path),str(tmp_path/'stage')],env=env,capture_output=True)
    assert result.returncode==2
    assert (data/'porsche2lox/new-state-layout').exists()


def test_preroot_stops_only_numbered_plugin_service(tmp_path):
    command=tmp_path/'systemctl'
    command.write_text('#!/bin/sh\nprintf "%s\\n" "$*" >> "$CALLS"\n')
    command.chmod(0o755)
    env={**os.environ,'PATH':str(tmp_path)+':'+os.environ['PATH'],'CALLS':str(tmp_path/'calls')}
    result=subprocess.run(['bash',str(ROOT/'preroot.sh'),'zip','porsche2lox','porsche2lox2'],env=env,capture_output=True)
    assert result.returncode==0
    assert (tmp_path/'calls').read_text().splitlines()==['cat porsche2lox-porsche2lox2.service','stop porsche2lox-porsche2lox2.service']
    (tmp_path/'calls').unlink()
    result=subprocess.run(['bash',str(ROOT/'preroot.sh'),'zip','porsche2lox','porsche-taycan'],env=env,capture_output=True)
    assert result.returncode==2
    assert not (tmp_path/'calls').exists()
