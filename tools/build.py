#!/usr/bin/env python3
"""Build only explicit plugin inputs; never package local settings or sessions."""
import hashlib
import configparser
import re
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile, ZipInfo

ROOT = Path(__file__).resolve().parents[1]
INCLUDE = ['plugin.cfg', 'preroot.sh', 'preupgrade.sh', 'postinstall.sh', 'postroot.sh', 'README.md', 'README.de.md', 'README.en.md', 'INSTALL.md', 'INSTALL.de.md', 'RELEASE.md', 'CHANGELOG.md', 'SECURITY.md', 'CONTRIBUTING.md', 'LICENSE', 'THIRD-PARTY-NOTICES.md', 'docs', 'bin', 'webfrontend', 'templates', 'icons', 'uninstall', 'dpkg']


def build():
    from check_branding import check_source
    check_source()
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
            if path.is_symlink():
                raise ValueError('Source symlinks are not valid package inputs.')
            relative = path.relative_to(ROOT).as_posix()
            info = ZipInfo(relative, (2026, 10, 21, 0, 0, 0))
            info.compress_type = ZIP_DEFLATED
            info.external_attr = (0o100755 if path.suffix == '.sh' else 0o100644) << 16
            data = path.read_bytes()
            if relative == 'templates/dashboard.html':
                # The plugin package has its own version; Docker source/UI is unchanged.
                data, count = re.subn(rb'<span class="beta">[^<]+ \xc2\xb7 Preview</span>',
                    lambda _: ('<span class="beta">' + version + ' · Preview</span>').encode(), data)
                if count != 1:
                    raise ValueError('Expected exactly one plugin version badge.')
            archive.writestr(info, data)
    digest = hashlib.sha256(target.read_bytes()).hexdigest()
    target.with_suffix('.zip.sha256').write_text(f'{digest}  {target.name}\n')
    print(f'{target}\nSHA256 {digest}\n{len(paths)} Dateien')


if __name__ == '__main__':
    build()
