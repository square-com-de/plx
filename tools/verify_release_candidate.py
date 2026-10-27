"""Validate downloaded Actions artifacts before promotion; no secrets or mutation."""
import hashlib
import json
from pathlib import Path
import re
import sys
from zipfile import ZipFile
from prepare_loxberry_release import verify_archive

FILES = {'PLX-LoxBerry-Plugin-0.1.5.zip', 'PLX-Docker-0.1.5.tar.gz', 'compose.yaml', 'manifest.json', 'SHA256SUMS'}


def verify(folder, sha, run):
    folder = Path(folder)
    if not re.fullmatch('[a-f0-9]{40}', sha): raise ValueError('Invalid source SHA')
    if run.get('head_sha') != sha or run.get('head_branch') != 'main' or run.get('conclusion') != 'success' or run.get('event') != 'workflow_dispatch' or run.get('path') != '.github/workflows/release.yml' or run.get('head_repository', {}).get('full_name') != 'square-com-de/plx':
        raise ValueError('Candidate run/source is not the successful main release workflow')
    if {p.name for p in folder.iterdir()} != FILES or any(p.is_symlink() or not p.is_file() for p in folder.iterdir()): raise ValueError('Unexpected candidate files')
    checked = set()
    for line in (folder/'SHA256SUMS').read_text().splitlines():
        digest, name = line.split('  ', 1)
        if name not in FILES-{'SHA256SUMS'} or name in checked or hashlib.sha256((folder/name).read_bytes()).hexdigest() != digest: raise ValueError('Checksum/path mismatch')
        checked.add(name)
    if checked != FILES-{'SHA256SUMS'}: raise ValueError('Incomplete checksums')
    manifest = json.loads((folder/'manifest.json').read_text())
    if manifest['version'] != '0.1.5' or manifest['status'] != 'preview' or manifest['source_dirty'] or manifest['source_commit'] != sha or manifest['container']['source_commit'] != sha: raise ValueError('Candidate provenance mismatch')
    if not re.fullmatch(r'ghcr.io/square-com-de/plx@sha256:[a-f0-9]{64}',manifest['container']['image']): raise ValueError('Unpinned image')
    if manifest['container']['ci_run'] != run.get('html_url'): raise ValueError('Candidate workflow URL mismatch')
    if manifest['container']['image'] not in (folder/'compose.yaml').read_text(): raise ValueError('Compose image mismatch')
    members = verify_archive(folder/manifest['plugin_zip'])
    if members != manifest['members_sha256']: raise ValueError('Plugin member manifest mismatch')
    with ZipFile(folder/manifest['plugin_zip']) as archive:
        root=Path(__file__).resolve().parents[1]
        for name in archive.namelist():
            if name.startswith(('bin/', 'webfrontend/')) and archive.read(name) != (root/name).read_bytes(): raise ValueError('Plugin runtime differs from reviewed source')
    return manifest


if __name__ == '__main__':
    verify(sys.argv[1], sys.argv[2], json.loads(Path(sys.argv[3]).read_text()))
    print('Candidate files, source/run provenance, checksums, image and plugin verified.')
