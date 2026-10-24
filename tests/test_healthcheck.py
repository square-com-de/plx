"""Exercise the actual container health check against a real local TLS socket."""
import importlib.util
from pathlib import Path
import ssl
import subprocess
import threading
import pytest
from porsche2lox.standalone import Application, Server

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('plx_docker_healthcheck',ROOT/'docker/healthcheck.py')
health=importlib.util.module_from_spec(spec);spec.loader.exec_module(health)


def test_healthcheck_connects_locally_but_verifies_configured_dns_identity(tmp_path):
    tls=tmp_path/'tls';tls.mkdir();cert=tls/'cert.pem';key=tls/'key.pem'
    subprocess.run(['openssl','req','-x509','-newkey','rsa:2048','-nodes','-keyout',str(key),'-out',str(cert),'-days','1','-subj','/CN=example.test','-addext','subjectAltName=DNS:example.test'],check=True,capture_output=True)
    app=Application(ROOT,tmp_path,'admin','independent-test-password-123')
    (tmp_path/'runtime').mkdir();(tmp_path/'runtime/control.sock').touch()
    ctx=ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER);ctx.load_cert_chain(cert,key)
    server=Server(('127.0.0.1',0),app,ctx);thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
    try:
        assert health.check(tmp_path,host='example.test',port=server.server_address[1])
        with pytest.raises(ssl.SSLCertVerificationError):health.check(tmp_path,host='wrong.test',port=server.server_address[1])
    finally:
        server.shutdown();server.server_close();thread.join()
