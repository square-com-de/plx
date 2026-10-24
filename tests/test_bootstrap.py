"""Fresh-start and recovery behavior, without any Porsche account or network."""
import os
from pathlib import Path
import ssl
import subprocess
import pytest
from porsche2lox.bootstrap import configured_host, prepare_tls, web_password

@pytest.mark.parametrize('value', ['', 'https://car.local', 'host:8443', 'car/path', 'user@host', 'host,IP:evil', '192.168.1.999','bad_name','[127.0.0.1', 'fe80::1%eth0','[::1]','::1','2001:db8::1'])
def test_invalid_browser_host_is_rejected_before_start(value):
    with pytest.raises(ValueError,match='PLX_HOST'):
        configured_host({'PLX_HOST':value})

@pytest.mark.parametrize('value,expected',[('192.0.2.10','192.0.2.10'),('LOCALHOST','localhost'),('plx.example.org.','plx.example.org')])
def test_browser_host_identity(value,expected):
    assert configured_host({'PLX_HOST':value})==expected

def test_first_password_is_private_stable_and_not_fixed(tmp_path):
    a,b=tmp_path/'a',tmp_path/'b'
    password=web_password(a,{})
    assert len(password)>=32 and password==web_password(a,{})
    assert password!=web_password(b,{})
    assert (a/'config/web-password.txt').stat().st_mode&0o777==0o600

def test_existing_external_secret_is_preserved(tmp_path):
    secret=tmp_path/'secret';secret.write_text('external-secret-password-123\n')
    assert web_password(tmp_path,{'PLX_PASSWORD_FILE':str(secret)})=='external-secret-password-123'
    assert not (tmp_path/'config/web-password.txt').exists()

def test_password_symlink_or_public_file_is_rejected(tmp_path):
    (tmp_path/'config').mkdir();outside=tmp_path/'outside';outside.write_text('independent-long-password-123')
    p=tmp_path/'config/web-password.txt';p.symlink_to(outside)
    with pytest.raises(ValueError):web_password(tmp_path,{})
    p.unlink();p.write_text(outside.read_text());p.chmod(0o644)
    with pytest.raises(ValueError):web_password(tmp_path,{})

def test_matching_lan_certificate_health_identity_and_restart(tmp_path):
    cert,key=prepare_tls(tmp_path,'192.0.2.10');old=(cert.read_bytes(),key.read_bytes())
    for flag,host in [('-checkip','192.0.2.10'),('-checkhost','localhost'),('-checkip','127.0.0.1')]:
        subprocess.run(['openssl','x509','-in',str(cert),'-noout',flag,host],check=True,capture_output=True)
    prepare_tls(tmp_path,'192.0.2.10');assert (cert.read_bytes(),key.read_bytes())==old
    ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER).load_cert_chain(cert,key)
    with pytest.raises(ValueError,match='TLS-Zertifikat'):
        prepare_tls(tmp_path,'192.0.2.11')
    assert (cert.read_bytes(),key.read_bytes())==old

def test_partial_existing_tls_pair_is_never_overwritten(tmp_path):
    (tmp_path/'tls').mkdir();key=tmp_path/'tls/key.pem';key.write_text('do-not-replace')
    with pytest.raises(ValueError,match='unvollständig'):prepare_tls(tmp_path,'localhost')
    assert key.read_text()=='do-not-replace' and not (tmp_path/'tls/cert.pem').exists()
