"""Confirm the public version tag resolves to the exact accepted OCI index."""
import hashlib
import json
from pathlib import Path
import sys
import urllib.parse
import urllib.request


def verify(manifest):
    expected = manifest['container']['image'].split('@',1)[1]
    query = urllib.parse.urlencode({'service':'ghcr.io','scope':'repository:square-com-de/plx:pull'})
    with urllib.request.urlopen('https://ghcr.io/token?'+query,timeout=30) as response: token=json.load(response)['token']
    request=urllib.request.Request('https://ghcr.io/v2/square-com-de/plx/manifests/0.1.5',headers={'Authorization':'Bearer '+token,'Accept':'application/vnd.oci.image.index.v1+json, application/vnd.docker.distribution.manifest.list.v2+json'})
    with urllib.request.urlopen(request,timeout=30) as response:
        blob=response.read();digest=response.headers.get('Docker-Content-Digest')
    if digest != expected or 'sha256:'+hashlib.sha256(blob).hexdigest() != expected: raise ValueError('Version tag differs from accepted image')


if __name__=='__main__':
    verify(json.loads(Path(sys.argv[1]).read_text()))
    print('Public version tag matches the accepted immutable image exactly.')
