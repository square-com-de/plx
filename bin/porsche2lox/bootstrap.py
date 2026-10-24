"""Private first-start password and host-matched TLS for the Docker shell."""
from __future__ import annotations
import ipaddress
import os
from pathlib import Path
import re
import secrets
import stat
import subprocess
import tempfile


def configured_host(env=None):
    env = os.environ if env is None else env
    # Existing external-secret deployments keep their localhost-compatible setup.
    value = env.get('PLX_HOST', 'localhost').strip()
    if not value or any(c in value for c in '/@,\\\r\n\t '):
        raise ValueError('PLX_HOST: IP oder DNS-Name ohne https://, Pfad oder Port angeben.')
    if value.startswith('[') or value.endswith(']'):
        if not (value.startswith('[') and value.endswith(']')):
            raise ValueError('PLX_HOST: ungültige IP-Klammern.')
        value = value[1:-1]
    if '%' in value:
        raise ValueError('PLX_HOST: IP ohne Zonenkennung angeben.')
    try:
        address = ipaddress.ip_address(value)
    except ValueError:
        address = None
    if address is not None:
        if address.version != 4:
            raise ValueError('PLX_HOST: IPv4 oder DNS mit IPv4 verwenden; IPv6 ist im Standardweg nicht abgenommen.')
        return str(address)
    if re.fullmatch(r'[0-9.]+', value):
        raise ValueError('PLX_HOST: gültige IPv4-Adresse oder gültigen DNS-Namen angeben.')
    try:
        value = value.rstrip('.').encode('idna').decode('ascii').lower()
    except UnicodeError:
        raise ValueError('PLX_HOST: gültige IPv4-Adresse oder gültigen DNS-Namen angeben.') from None
    if len(value) > 253 or not all(re.fullmatch(r'[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?', p) for p in value.split('.')):
        raise ValueError('PLX_HOST: IPv4 oder DNS-Name ohne Protokoll, Pfad oder Port angeben.')
    return value


def web_password(data, env=None):
    env = os.environ if env is None else env
    external = env.get('PLX_PASSWORD_FILE')
    if external is None and Path('/run/secrets/plx_password').is_file():
        external = '/run/secrets/plx_password'
    if external == '':
        raise ValueError('PLX_PASSWORD_FILE darf nicht leer sein; Variable weglassen für automatisches Passwort.')
    if external:
        try:
            value = Path(external).read_text().rstrip('\r\n')
        except (OSError, UnicodeError):
            raise ValueError('PLX_PASSWORD_FILE ist nicht lesbar. Dateirechte des eingebundenen Secrets prüfen.') from None
    else:
        directory = Path(data) / 'config'
        if directory.is_symlink():
            raise ValueError('PLX-Konfigurationsverzeichnis darf kein symbolischer Link sein.')
        directory.mkdir(parents=True, exist_ok=True, mode=0o700)
        path = directory / 'web-password.txt'
        try:
            fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
        except FileExistsError:
            pass
        else:
            with os.fdopen(fd, 'w') as stream:
                stream.write(secrets.token_urlsafe(32) + '\n')
        try:
            fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW)
            with os.fdopen(fd) as stream:
                mode = os.fstat(stream.fileno()).st_mode
                if not stat.S_ISREG(mode) or mode & 0o077:
                    raise ValueError('Die gespeicherte PLX-Passwortdatei benötigt private Dateirechte (0600).')
                value = stream.read(1025).rstrip('\r\n')
        except (OSError, UnicodeError):
            raise ValueError('Gespeicherte PLX-Passwortdatei nicht lesbar; Sicherung und Dateirechte prüfen.') from None
    if not 16 <= len(value) <= 1024:
        raise ValueError('PLX-Passwort muss 16 bis 1024 Zeichen enthalten; bestehendes Secret prüfen.')
    return value


def prepare_tls(data, host):
    directory = Path(data) / 'tls'
    if directory.is_symlink():
        raise ValueError('PLX-TLS-Verzeichnis darf kein symbolischer Link sein.')
    directory.mkdir(parents=True, exist_ok=True, mode=0o700)
    cert, key = directory / 'cert.pem', directory / 'key.pem'
    if cert.is_symlink() or key.is_symlink():
        raise ValueError('PLX-Zertifikat und Schlüssel müssen reguläre Dateien sein.')
    if cert.exists() != key.exists():
        raise ValueError('TLS-Dateien unvollständig. cert.pem und key.pem als passendes Paar wiederherstellen.')
    if not cert.exists():
        try:
            address = ipaddress.ip_address(host)
            san = 'IP:' + str(address)
        except ValueError:
            san = 'DNS:' + host
        sans = ','.join(dict.fromkeys(['DNS:localhost', 'IP:127.0.0.1', san]))
        with tempfile.TemporaryDirectory(dir=directory, prefix='.first-start-') as tmp:
            fresh_cert, fresh_key = Path(tmp)/'cert.pem', Path(tmp)/'key.pem'
            subprocess.run(['openssl','req','-x509','-newkey','rsa:3072','-nodes','-keyout',str(fresh_key),'-out',str(fresh_cert),'-days','365','-subj','/CN=PLX','-addext','subjectAltName='+sans],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
            fresh_key.chmod(0o600); fresh_cert.chmod(0o600)
            os.replace(fresh_key,key); os.replace(fresh_cert,cert)
    try:
        flag = '-checkip' if ipaddress.ip_address(host) else '-checkhost'
    except ValueError:
        flag = '-checkhost'
    for args in ([flag,host], ['-checkend','0']):
        result = subprocess.run(['openssl','x509','-in',str(cert),'-noout',*args],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
        if result.returncode:
            raise ValueError('TLS-Zertifikat passt nicht zu PLX_HOST oder ist abgelaufen. Passendes cert.pem/key.pem-Paar einsetzen; bestehende Dateien bleiben erhalten.')
    return cert,key
