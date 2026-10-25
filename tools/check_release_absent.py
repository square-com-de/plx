"""Fail closed unless public release, Git tag and registry version explicitly do not exist."""
import json
import re
import sys
import urllib.error
import urllib.parse
import urllib.request


def request(url, *, headers=None, method='GET'):
    req = urllib.request.Request(url, headers={'User-Agent': 'PLX-release-guard', **(headers or {})}, method=method)
    try:
        with urllib.request.urlopen(req, timeout=30) as response:
            return response.status, response.read()
    except urllib.error.HTTPError as error:
        if error.code == 404:
            return 404, b''
        raise RuntimeError('Release existence check failed; refusing publication.') from None
    except (OSError, urllib.error.URLError):
        raise RuntimeError('Release existence check unavailable; refusing publication.') from None


def main(version):
    if not re.fullmatch(r'\d+\.\d+\.\d+', version):
        raise ValueError('Explicit semantic version required.')
    status, _ = request('https://api.github.com/repos/square-com-de/plx/releases/tags/v' + version)
    if status != 404:
        raise RuntimeError('Release version already exists; refusing replacement.')
    status, _ = request('https://api.github.com/repos/square-com-de/plx/git/ref/tags/v' + version)
    if status != 404:
        raise RuntimeError('Git tag already exists; refusing source/tag mismatch.')
    query = urllib.parse.urlencode({'service': 'ghcr.io', 'scope': 'repository:square-com-de/plx:pull'})
    status, body = request('https://ghcr.io/token?' + query)
    if status != 200:
        raise RuntimeError('Registry authorization unavailable; refusing publication.')
    token = json.loads(body).get('token')
    if not token:
        raise RuntimeError('Registry authorization unavailable; refusing publication.')
    status, _ = request('https://ghcr.io/v2/square-com-de/plx/manifests/' + version, method='HEAD', headers={'Authorization': 'Bearer ' + token, 'Accept': 'application/vnd.oci.image.index.v1+json, application/vnd.docker.distribution.manifest.list.v2+json, application/vnd.oci.image.manifest.v1+json, application/vnd.docker.distribution.manifest.v2+json'})
    if status != 404:
        raise RuntimeError('Image version already exists; refusing replacement.')
    print('Public release, Git tag and image version explicitly absent; publication may proceed.')


if __name__ == '__main__':
    try:
        main(sys.argv[1])
    except (RuntimeError, ValueError, IndexError):
        sys.exit('Release guard failed; refusing publication. Check availability, access and existing version.')
