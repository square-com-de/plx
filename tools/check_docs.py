#!/usr/bin/env python3
"""Check the end-user guide links, shell syntax and release/support contract."""
import json
import configparser
from pathlib import Path
import re
import subprocess
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
GUIDES = ['README.md','README.de.md','INSTALL.md','INSTALL.de.md','docs/MANUAL.md','docs/MANUAL.de.md','docs/DOCKER.md','docs/LOXONE.md','docs/INSTALLATION-LESSONS.md','docs/INSTALLATION-LESSONS.de.md','docs/PROXMOX-CONTAINER.md','docs/PROXMOX-CONTAINER.de.md','docs/QUICKSTART-0.1.1.md']

def slug(text):
    return re.sub(r'[^\w\- ]', '', text.lower().replace('`','')).replace(' ','-')

def blocks(text, language):
    return re.findall(r'^```'+language+r'\n(.*?)^```', text, re.M | re.S)

def main():
    checked = 0
    for name in GUIDES:
        path=ROOT/name; text=path.read_text()
        for line in text.splitlines():
            if '```' in line:
                assert re.fullmatch(r'\s*```[A-Za-z0-9_-]*\s*',line), (name,'malformed code fence')
        for raw in re.findall(r'\]\(([^\s)]+)\)',text):
            u=urlsplit(raw)
            if u.scheme or raw.startswith('//'):continue
            target=(path.parent/unquote(u.path)).resolve() if u.path else path
            assert target.is_relative_to(ROOT), (name,raw,'outside repository')
            assert target.exists(), (name,raw,'missing target')
            if u.fragment and target.suffix=='.md':
                headings={slug(h) for h in re.findall(r'^#{1,6}\s+(.+)$',target.read_text(),re.M)}
                assert unquote(u.fragment) in headings, (name,raw,'missing heading')
            checked+=1
        for script in blocks(text,'sh'):
            subprocess.run(['sh','-n'],input=script,text=True,check=True)
    en=(ROOT/'INSTALL.md').read_text();de=(ROOT/'INSTALL.de.md').read_text()
    assert blocks(en,'sh')==blocks(de,'sh'), 'DE/EN install commands differ'
    assert blocks((ROOT/'docs/MANUAL.md').read_text(),'sh')==blocks((ROOT/'docs/MANUAL.de.md').read_text(),'sh'), 'DE/EN network checks differ'
    metadata=configparser.ConfigParser();metadata.read(ROOT/'plugin.cfg')
    version=metadata['PLUGIN']['VERSION']
    for text in (en,de):
        for required in [f'releases/download/v{version}/compose.yaml','PLX_HOST=192.0.2.10','docker compose up -d --wait','/data/config/web-password.txt','porsche2lox/#','Podman']:
            assert required in text, ('new standard start missing',required)
        for script in blocks(text,'sh'):
            assert not any(old in script for old in ['chgrp','openssl rand','secrets/plx_password']), 'Manual secret setup must not be standard'
    standard=(ROOT/'compose.registry.yaml').read_text()
    assert 'PLX_HOST: "${PLX_HOST:?' in standard and 'PLX_BIND_ADDRESS:-0.0.0.0' in standard
    assert 'secrets:' not in standard and '/run/secrets' not in standard
    assert blocks((ROOT/'README.md').read_text(),'sh')[0] == blocks((ROOT/'INSTALL.md').read_text(),'sh')[0], 'README and INSTALL start commands differ'
    assert blocks((ROOT/'README.de.md').read_text(),'sh')[0] == blocks((ROOT/'INSTALL.de.md').read_text(),'sh')[0], 'German README and INSTALL start commands differ'
    docker=(ROOT/'docs/DOCKER.md').read_text()
    assert 'Beim Login das GitHub-Paket-Token als Passwort verwenden' not in docker
    assert 'Hauptwerte + Überwachung** wählen' not in (ROOT/'docs/LOXONE.md').read_text(), 'Detailed-only setup must not be the simple default'
    assert blocks((ROOT/'docs/PROXMOX-CONTAINER.md').read_text(),'sh')==blocks((ROOT/'docs/PROXMOX-CONTAINER.de.md').read_text(),'sh'), 'Proxmox DE/EN commands differ'
    for name in ['docs/PROXMOX-CONTAINER.md','docs/PROXMOX-CONTAINER.de.md']:
        assert 'COMPOSE_FILE=compose.yaml:compose.restore.yaml' in (ROOT/name).read_text(), 'Restore file choice must persist'
    evidence=json.loads((ROOT/'docs/evidence/2026-10-24-installation-review.json').read_text())
    assert evidence['release_status']=='preview unchanged'
    assert not evidence['support_limits']['podman_acceptance_record_found']
    assert not evidence['support_limits']['arm64_real_runtime_acceptance_record_found']
    print(f'PASS: {checked} local links/anchors, shell syntax, bilingual command parity, release/runtime/MQTT documentation contract')

if __name__=='__main__':main()
