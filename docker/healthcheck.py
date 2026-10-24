"""Trust the locally generated/persisted certificate, never disable TLS checks."""
import ssl
import urllib.request

context = ssl.create_default_context(cafile='/data/tls/cert.pem')
with urllib.request.urlopen('https://localhost:8443/healthz', context=context, timeout=3) as response:
    if response.status != 200:
        raise SystemExit(1)
