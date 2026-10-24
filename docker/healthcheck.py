"""Local connection with verification of the configured certificate identity."""
from contextlib import closing
import http.client
from pathlib import Path
import socket
import ssl
from porsche2lox.bootstrap import configured_host


def check(data=Path('/data'), host=None, port=8443):
    context = ssl.create_default_context()
    context.load_verify_locations(cafile=str(Path(data)/'tls/cert.pem'))
    with closing(http.client.HTTPConnection('127.0.0.1',port,timeout=3)) as connection:
        connection.sock = context.wrap_socket(socket.create_connection(('127.0.0.1',port),timeout=3),server_hostname=host or configured_host())
        connection.request('GET','/healthz')
        response = connection.getresponse()
        return response.status == 200


if __name__ == '__main__':
    raise SystemExit(0 if check() else 1)
