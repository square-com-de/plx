"""Promotion must be bound to the reviewed workflow/source and exact artifact bytes."""
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import sys
import pytest

TOOLS=Path(__file__).resolve().parents[1]/'tools'
sys.path.insert(0,str(TOOLS))
from verify_release_candidate import verify


def write_checksums(folder):
    (folder/'SHA256SUMS').write_text(''.join(hashlib.sha256(p.read_bytes()).hexdigest()+'  '+p.name+'\n' for p in sorted(folder.iterdir()) if p.name!='SHA256SUMS'))


@pytest.fixture
def candidate(tmp_path):
    # Build only the local candidate, without any network or publication.
    import prepare_release
    monkey_image=prepare_release.IMAGE
    try:
        prepare_release.IMAGE='ghcr.io/square-com-de/plx@sha256:'+'a'*64
        prepare_release.prepare()
    finally:prepare_release.IMAGE=monkey_image
    source=TOOLS.parent/'dist/release-v0.1.5'
    for name in ['PLX-LoxBerry-Plugin-0.1.5.zip','PLX-Docker-0.1.5.tar.gz','manifest.json','compose.yaml','SHA256SUMS']:shutil.copyfile(source/name,tmp_path/name)
    m=json.loads((tmp_path/'manifest.json').read_text());m['source_dirty']=False
    m['container']['ci_run']='https://github.com/square-com-de/plx/actions/runs/123'
    (tmp_path/'manifest.json').write_text(json.dumps(m));write_checksums(tmp_path)
    run=dict(head_sha=m['source_commit'],head_branch='main',conclusion='success',event='workflow_dispatch',path='.github/workflows/release.yml',head_repository={'full_name':'square-com-de/plx'},html_url=m['container']['ci_run'])
    return tmp_path,m['source_commit'],run


def test_exact_candidate_accepts(candidate):
    assert verify(*candidate)['version']=='0.1.5'


@pytest.mark.parametrize('change',[{'head_branch':'unreviewed'},{'conclusion':'failure'},{'event':'pull_request'},{'head_sha':'0'*40},{'path':'.github/workflows/docker.yml'}])
def test_other_run_or_source_rejected(candidate,change):
    folder,sha,run=candidate
    with pytest.raises(ValueError):verify(folder,sha,dict(run,**change))


def test_modified_file_and_unsafe_checksum_rejected(candidate):
    folder,sha,run=candidate
    (folder/'compose.yaml').write_text('tampered')
    with pytest.raises(ValueError):verify(folder,sha,run)
    (folder/'SHA256SUMS').write_text('a'*64+'  ../outside\n')
    with pytest.raises(ValueError):verify(folder,sha,run)
