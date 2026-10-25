#!/usr/bin/env python3
"""Prepare the explicit 0.1.4 LoxBerry fresh-install release; never build/push Docker."""
import argparse
import configparser
import hashlib
import json
from pathlib import Path, PurePosixPath
import shutil
import stat
import subprocess
import urllib.error
import urllib.request
from zipfile import ZipFile
from build import ROOT, build

VERSION = '0.1.4'
ARCHIVE = f'PLX-LoxBerry-{VERSION}-New-Installation.zip'
REPO = 'square-com-de/plx'


def require(value, message):
    if not value:
        raise ValueError(message)


def verify_archive(path):
    with ZipFile(path) as archive:
        names = archive.namelist()
        require(len(names) == len(set(names)), 'Duplicate archive members')
        for member in archive.infolist():
            p = PurePosixPath(member.filename)
            require(not p.is_absolute() and '..' not in p.parts and '\\' not in member.filename, 'Unsafe archive path')
            require(not stat.S_ISLNK(member.external_attr >> 16), 'Archive symlink')
            require(not set(p.parts) & {'.git', '.venv', '__pycache__', 'runtime', 'secrets'}, 'Private/runtime path')
            require(p.name not in {'settings.json', 'session.json', 'trusted-proxies.json', 'mqtt_auth', 'web-password.txt', '.session'} and not p.name.startswith('.env'), 'Private state')
            require(p.suffix not in {'.pem', '.key', '.pyc', '.sock'}, 'Private/runtime file')
        required = {'plugin.cfg', 'postroot.sh', 'postinstall.sh', 'preupgrade.sh',
                    'webfrontend/htmlauth/index.php', 'templates/dashboard.html', 'LICENSE'}
        require(required <= set(names), 'Missing root-level plugin inputs')
        cfg = configparser.ConfigParser()
        cfg.read_string(archive.read('plugin.cfg').decode())
        require(cfg['AUTHOR']['NAME'] == 'square | com' and cfg['AUTHOR']['EMAIL'] == 'plx@square-com.de', 'Unexpected new author identity')
        require(cfg['PLUGIN']['VERSION'] == VERSION, 'Plugin version mismatch')
        require(cfg['PLUGIN']['NAME'] == 'porsche2lox' and cfg['PLUGIN']['FOLDER'] == 'porsche2lox', 'Unexpected technical plugin names')
        require(cfg['AUTOUPDATE']['AUTOMATIC_UPDATES'].lower() == 'false', 'Automatic updates must remain disabled')
        require((VERSION+' · Preview').encode() in archive.read('templates/dashboard.html'), 'Packaged UI version mismatch')
        return {name: hashlib.sha256(archive.read(name)).hexdigest() for name in sorted(names)}


def git(*args):
    return subprocess.check_output(['git', '-C', str(ROOT), *args], text=True).strip()


def check_absent():
    for endpoint in [f'releases/tags/v{VERSION}', f'git/ref/tags/v{VERSION}']:
        request = urllib.request.Request(f'https://api.github.com/repos/{REPO}/{endpoint}', headers={'User-Agent': 'PLX-LoxBerry-release-guard'})
        try:
            with urllib.request.urlopen(request, timeout=30):
                raise ValueError('Release/tag exists; refusing replacement')
        except urllib.error.HTTPError as error:
            require(error.code == 404, 'Release/tag check did not confirm absence')
    print('Release and tag absent; no existing artifact will be replaced.')


def prepare():
    metadata = configparser.ConfigParser()
    metadata.read(ROOT/'plugin.cfg')
    require(metadata['PLUGIN']['VERSION'] == VERSION, 'Expected explicit plugin version')
    build()
    destination = ROOT/'dist'/f'loxberry-{VERSION}'
    destination.mkdir(parents=True, exist_ok=True)
    package = destination/ARCHIVE
    shutil.copyfile(ROOT/'dist'/f'PLX-LoxBerry-{VERSION}.zip', package)
    members = verify_archive(package)
    from check_branding import inspect_bytes
    inspect_bytes(package.name, package.read_bytes())
    old_identity = hashlib.md5(b'dubctrllance.com@gmail.comporsche2loxporsche2lox').hexdigest()
    new_identity = hashlib.md5(b'square | complx@square-com.deporsche2loxporsche2lox').hexdigest()
    require(old_identity != new_identity, 'Fresh-install identity must differ from historical author')
    manifest = {
        'name': 'PLX', 'plugin_version': VERSION, 'status': 'preview',
        'distribution': 'LoxBerry 4 plugin only', 'installation': 'new installation, not an in-place upgrade',
        'author': 'square | com', 'author_email': 'plx@square-com.de',
        'source_commit': git('rev-parse', 'HEAD'), 'source_tree': git('rev-parse', 'HEAD^{tree}'),
        'source_dirty': bool(git('status', '--porcelain')),
        'plugin_zip': ARCHIVE, 'members_sha256': members,
        'generated_member': 'templates/dashboard.html: version badge rendered from plugin.cfg',
        'historical_identity': old_identity, 'new_identity': new_identity,
        'docker': {'unchanged_version': '0.1.3', 'image_published_by_this_release': False},
        'installation_test': 'not executed on a LoxBerry host for this new identity; package checks only',
    }
    (destination/'manifest.json').write_text(json.dumps(manifest, indent=2)+'\n')
    (destination/'SHA256SUMS').write_text(''.join(hashlib.sha256((destination/name).read_bytes()).hexdigest()+'  '+name+'\n' for name in [ARCHIVE, 'manifest.json']))
    print(f'Prepared {package.name}: {len(members)} members; no publication or deployment.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--check-absent', action='store_true')
    args = parser.parse_args()
    check_absent() if args.check_absent else prepare()
