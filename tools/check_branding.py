#!/usr/bin/env python3
"""Verify original artwork identity and reject known old logo bytes, including archives.
Hash checks complement visual review; they do not detect every re-encoded motif.
"""
import base64,hashlib,io,json,re,struct,sys,tarfile,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
ORIGINAL='bbd8b07d633b944703f651eacbf96984956b6b6e0f5fb6803e93caaffa63470b'
OLD_SVG='cb1b1f2baf2476b3f02ab8a0f9ec60e987f72078e470f85d17a14052b5a35414'
OLD_SCREENSHOTS={'c876400ba295f2d1749adb453b73a1936089a5011fe5a2b9753b8923968cd88b', '9e28a20d5c7e3b5675f67bf4c4ff4c1e0cca334a178f62a2b3e485fa399b981a', 'ce6108775269357899f248def5ecf3723eef183fac352f5f72a6ccaf1642e3d0', '04cd140e7f5e835881e5aff7e66dd6eea340182972fa3c3417a3f692b80bdd58', '58ef8c8f1c67460b829f8383547d398efb1c8ee16dfe38a249fd8792be3540e0', '1069222528b0d216b4c448187dd94514dd49ca9127cfb33fef9beef7e2f2fc27', '8f12b86e5c928b32c7dfe2bc1c5ca1d0f7c7159ed2268d82cfa54e12b13b532c', '2d24b4632d6c839e7b215d15e055ba74f5f981d7a5b205860e9ac7a7231e9b05'}
OLD_CREST='3b315177c1c53ded2560891e286188394a0ce036af47cf2ff06b787981483ab3'
def digest(raw):return hashlib.sha256(raw).hexdigest()
def inspect_bytes(name,raw,depth=0):
 if digest(raw) in {OLD_SVG,OLD_CREST}|OLD_SCREENSHOTS:raise ValueError('Known old branding: '+name)
 for m in re.finditer(rb'data:image/[\w.+-]+;base64,([A-Za-z0-9+/=]+)',raw):
  if digest(base64.b64decode(m.group(1),validate=True))==OLD_CREST:raise ValueError('Embedded old crest: '+name)
 if depth>=4:raise ValueError('Archive nesting limit exceeded: '+name)
 if name.endswith('.zip'):
  with zipfile.ZipFile(io.BytesIO(raw)) as z:
   for n in z.namelist():
    if not n.endswith('/'):inspect_bytes(name+'!'+n,z.read(n),depth+1)
 elif name.endswith(('.tar.gz','.tgz')):
  with tarfile.open(fileobj=io.BytesIO(raw)) as z:
   for m in z.getmembers():
    if m.isfile():inspect_bytes(name+'!'+m.name,z.extractfile(m).read(),depth+1)
def check_source():
 raw=(ROOT/'icons/plx-logo-original.png').read_bytes();assert digest(raw)==ORIGINAL,'Original PNG changed';assert raw[:8]==b'\x89PNG\r\n\x1a\n' and struct.unpack('>II',raw[16:24])==(1254,1254)
 prov=json.loads((ROOT/'icons/provenance.json').read_text());assert prov['sha256']==ORIGINAL
 for name in ['icons/icon.svg','webfrontend/htmlauth/logo.svg']:
  svg=(ROOT/name).read_bytes();assert digest(svg)==prov['svg_sha256'];embedded=re.findall(rb'data:image/png;base64,([A-Za-z0-9+/=]+)',svg);assert len(embedded)==1 and base64.b64decode(embedded[0])==raw,'Wrapper PNG differs'
 count=0
 for p in ROOT.rglob('*'):
  if not p.is_file() or any(x in p.relative_to(ROOT).parts for x in ['.git','dist','__pycache__','.venv']):continue
  if p.suffix.lower() in {'.svg','.png','.webp','.jpeg','.jpg','.ico','.html','.php','.css','.js'}:inspect_bytes(str(p.relative_to(ROOT)),p.read_bytes());count+=1
 return count
if __name__=='__main__':
 n=check_source()
 for name in sys.argv[1:]:inspect_bytes(name,Path(name).read_bytes())
 print(f'PASS: original PNG/wrappers, {n} source image/UI files and {len(sys.argv)-1} archives; visual review still required')
