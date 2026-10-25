#!/usr/bin/env python3
"""Check the built fresh-install ZIP and meaningful package failure cases."""
import io
from pathlib import Path
import tempfile
import unittest
import warnings
from zipfile import ZipFile, ZipInfo
from prepare_loxberry_release import ROOT, VERSION, ARCHIVE, verify_archive


class PackageTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.package = ROOT/'dist'/f'loxberry-{VERSION}'/ARCHIVE
        with ZipFile(cls.package) as z:
            cls.members = {n: z.read(n) for n in z.namelist()}

    def modified(self, extra=None, cfg=None, duplicate=False, symlink=False):
        stream = io.BytesIO()
        with ZipFile(stream, 'w') as z:
            for name, raw in self.members.items():
                z.writestr(name, cfg if name == 'plugin.cfg' and cfg is not None else raw)
            if extra:
                info = ZipInfo(extra)
                if symlink: info.external_attr = 0o120777 << 16
                z.writestr(info, b'synthetic')
            if duplicate:
                with warnings.catch_warnings():
                    warnings.simplefilter('ignore')
                    z.writestr('plugin.cfg', self.members['plugin.cfg'])
        stream.seek(0)
        return stream

    def test_real_package_and_runtime_source_unchanged(self):
        self.assertGreater(len(verify_archive(self.package)), 60)
        for name, raw in self.members.items():
            if name.startswith(('bin/', 'webfrontend/')):
                self.assertEqual(raw, (ROOT/name).read_bytes())
        self.assertIn(b'0.1.3', (ROOT/'templates/dashboard.html').read_bytes())
        self.assertIn(b'0.1.4', self.members['templates/dashboard.html'])
        self.assertIn('ghcr.io/square-com-de/plx:0.1.3', (ROOT/'compose.registry.yaml').read_text())

    def test_private_state_and_unsafe_members_are_rejected(self):
        for path in ['data/session.json', 'config/settings.json', 'config/trusted-proxies.json',
                     '/absolute', '../escape', 'runtime/marker', 'private.pem', '.env', 'bin/mqtt_auth', 'config/web-password.txt']:
            with self.subTest(path=path), self.assertRaises(ValueError):
                verify_archive(self.modified(extra=path))

    def test_duplicate_and_symlink_are_rejected(self):
        with self.assertRaises(ValueError): verify_archive(self.modified(duplicate=True))
        with self.assertRaises(ValueError): verify_archive(self.modified(extra='link', symlink=True))

    def test_historical_author_or_wrong_version_is_rejected(self):
        cfg = self.members['plugin.cfg']
        for invalid in [cfg.replace(b'NAME=square | com', b'NAME=dubctrl'),
                        cfg.replace(b'VERSION=0.1.4', b'VERSION=0.1.3')]:
            with self.assertRaises(ValueError): verify_archive(self.modified(cfg=invalid))


if __name__ == '__main__': unittest.main()
