#!/usr/bin/env python3
"""Prepare reviewable preview artifacts locally; never publish, tag or deploy."""
import configparser
import hashlib
import gzip
import io
import tarfile
import json
import os
from pathlib import Path
import shutil
import subprocess
from zipfile import ZipFile

from build import build, ROOT

IMAGE_COMMIT = os.environ.get('PLX_RELEASE_COMMIT')
IMAGE = os.environ.get('PLX_RELEASE_IMAGE', 'ghcr.io/square-com-de/plx:0.1.2')
CI_RUN = os.environ.get('PLX_RELEASE_CI', 'https://github.com/square-com-de/plx/actions/workflows/release.yml')


def git(*args):
    return subprocess.check_output(['git', '-C', str(ROOT), *args], text=True).strip()


def prepare():
    cfg = configparser.ConfigParser()
    cfg.read(ROOT / 'plugin.cfg')
    version = cfg['PLUGIN']['VERSION']
    if version != '0.1.2':
        raise ValueError('Update release provenance and notes for the new version first.')
    if '@sha256:' not in IMAGE:
        raise ValueError('Set PLX_RELEASE_IMAGE to the reviewed immutable image digest.')
    build()
    bundle = ROOT / 'dist' / f'release-v{version}'
    if bundle.exists():
        shutil.rmtree(bundle)
    bundle.mkdir()
    package = ROOT / 'dist' / f'PLX-LoxBerry-{version}.zip'
    with ZipFile(package) as archive:
        required = {'plugin.cfg', 'postinstall.sh', 'postroot.sh', 'templates/dashboard.html',
                    'webfrontend/htmlauth/app.js', 'README.md', 'README.de.md', 'README.en.md', 'INSTALL.md', 'INSTALL.de.md', 'LICENSE'}
        names = set(archive.namelist())
        if not required <= names:
            raise ValueError('Missing plugin files.')
        for name in names:
            parts = Path(name).parts
            if (name.startswith('/') or '..' in parts or
                    set(parts) & {'runtime', 'secrets', '.git', '.venv', '__pycache__'} or
                    Path(name).name in {'settings.json', 'session.json'} or
                    name.endswith(('.pem', '.key', '.pyc', '.sock'))):
                raise ValueError('Unexpected private/runtime file in plugin archive.')
    shutil.copy2(package, bundle / package.name)
    for name in ('README.md', 'README.de.md', 'README.en.md', 'INSTALL.md', 'INSTALL.de.md', 'RELEASE.md', 'CHANGELOG.md', 'SECURITY.md', 'CONTRIBUTING.md', 'LICENSE', 'THIRD-PARTY-NOTICES.md'):
        shutil.copy2(ROOT / name, bundle / name)
    shutil.copytree(ROOT / 'docs', bundle / 'docs')
    shutil.copytree(ROOT / 'icons', bundle / 'icons')
    compose = (ROOT / 'compose.registry.yaml').read_text()
    expected = 'image: ghcr.io/square-com-de/plx:0.1.2'
    if compose.count(expected) != 1:
        raise ValueError('Unexpected registry compose image declaration.')
    (bundle / 'compose.yaml').write_text(compose.replace(expected, 'image: ' + IMAGE))
    manifest = {
        'name': 'PLX', 'version': version,
        'public_repository': 'square-com-de/plx',
        'plugin_kind': 'LoxBerry plugin import ZIP', 'status': 'preview',
        'release_url': f'https://github.com/square-com-de/plx/releases/tag/v{version}', 'source_commit': git('rev-parse', 'HEAD'),
        'source_tree': git('rev-parse', 'HEAD^{tree}'),
        'source_dirty': bool(git('status', '--porcelain')),
        'container': {'image': IMAGE, 'source_commit': IMAGE_COMMIT or git('rev-parse', 'HEAD'),
                      'ci_run': CI_RUN, 'platforms': ['linux/amd64', 'linux/arm64'],
                      'visibility': 'public'},
        'plugin_zip': package.name,
        'docker_bundle': f'PLX-Docker-{version}.tar.gz',
        'docker_bundle_kind': 'compose-and-docs; image pulled from GHCR',
        'acceptance_pending': ['miniserver-acceptance'],
    }
    (bundle / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
    # Separate Docker distribution: Compose and documentation, no plugin or private data.
    docker_name = f'PLX-Docker-{version}'
    docker_files = [p for p in sorted(bundle.rglob('*')) if p.is_file() and p.suffix != '.zip']
    docker_sums = ''.join(hashlib.sha256(p.read_bytes()).hexdigest() + '  ' + p.relative_to(bundle).as_posix() + '\n' for p in docker_files)
    with (bundle / (docker_name + '.tar.gz')).open('wb') as output:
        with gzip.GzipFile(fileobj=output, mode='wb', filename='', mtime=0) as compressed:
            with tarfile.open(fileobj=compressed, mode='w') as archive:
                for path in docker_files:
                    data = path.read_bytes()
                    info = tarfile.TarInfo(docker_name + '/' + path.relative_to(bundle).as_posix())
                    info.size = len(data)
                    info.mode = 0o644
                    archive.addfile(info, io.BytesIO(data))
                data = docker_sums.encode()
                info = tarfile.TarInfo(docker_name + '/SHA256SUMS')
                info.size = len(data)
                info.mode = 0o644
                archive.addfile(info, io.BytesIO(data))
    lines = []
    for path in sorted(bundle.rglob('*')):
        if path.is_file() and path.name != 'SHA256SUMS':
            lines.append(hashlib.sha256(path.read_bytes()).hexdigest() + '  ' + path.relative_to(bundle).as_posix())
    (bundle / 'SHA256SUMS').write_text('\n'.join(lines) + '\n')
    print(f'Prepared {bundle} ({len(lines)} checksummed artifacts); no publication performed.')


if __name__ == '__main__':
    prepare()
