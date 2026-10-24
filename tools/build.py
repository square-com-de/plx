#!/usr/bin/env python3
"""Build only explicit plugin inputs; never package local settings or sessions."""
import hashlib
import configparser
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile, ZipInfo

ROOT = Path(__file__).resolve().parents[1]
INCLUDE = ['plugin.cfg', 'preroot.sh', 'preupgrade.sh', 'postinstall.sh', 'postroot.sh', 'README.md', 'README.de.md', 'README.en.md', 'INSTALL.md', 'INSTALL.de.md', 'RELEASE.md', 'CHANGELOG.md', 'SECURITY.md', 'CONTRIBUTING.md', 'LICENSE', 'THIRD-PARTY-NOTICES.md', 'docs', 'bin', 'webfrontend', 'templates', 'icons', 'uninstall', 'dpkg']


def build():
    output = ROOT / 'dist'
    output.mkdir(exist_ok=True)
    metadata = configparser.ConfigParser()
    metadata.read(ROOT / 'plugin.cfg')
    version = metadata['PLUGIN']['VERSION']
    target = output / f'PLX-LoxBerry-{version}.zip'
    paths = []
    for name in INCLUDE:
        path = ROOT / name
        paths.extend([path] if path.is_file() else [p for p in path.rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.suffix != '.pyc'])
    with ZipFile(target, 'w', ZIP_DEFLATED) as archive:
        for path in sorted(paths):
            relative = path.relative_to(ROOT).as_posix()
            info = ZipInfo(relative, (2026, 10, 21, 0, 0, 0))
            info.compress_type = ZIP_DEFLATED
            info.external_attr = (0o100755 if path.suffix == '.sh' else 0o100644) << 16
            archive.writestr(info, path.read_bytes())
    digest = hashlib.sha256(target.read_bytes()).hexdigest()
    target.with_suffix('.zip.sha256').write_text(f'{digest}  {target.name}\n')
    print(f'{target}\nSHA256 {digest}\n{len(paths)} Dateien')


if __name__ == '__main__':
    build()
