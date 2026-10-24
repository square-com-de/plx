"""Publication is allowed only after two explicit not-found results."""
import importlib.util
from pathlib import Path
import urllib.error
import pytest

spec=importlib.util.spec_from_file_location('release_guard',Path(__file__).parents[1]/'tools/check_release_absent.py')
guard=importlib.util.module_from_spec(spec);spec.loader.exec_module(guard)

def test_two_explicit_not_found_allow_publication(monkeypatch):
    results=iter([(404,b''),(200,b'{"token":"test-only"}'),(404,b'')]);calls=[]
    def request(url,**kwargs):calls.append((url,kwargs));return next(results)
    monkeypatch.setattr(guard,'request',request);guard.main('0.1.1')
    assert len(calls)==3 and calls[2][1]['method']=='HEAD'

@pytest.mark.parametrize('results',[
 [(200,b'')],
 [(404,b''),(404,b'')],
 [(404,b''),(200,b'{}')],
 [(404,b''),(200,b'{"token":"test-only"}'),(200,b'')],
])
def test_existing_or_unauthorized_version_aborts(monkeypatch,results):
    values=iter(results);monkeypatch.setattr(guard,'request',lambda *a,**k:next(values))
    with pytest.raises(RuntimeError):guard.main('0.1.1')

@pytest.mark.parametrize('error',[
 urllib.error.HTTPError('https://example.invalid',401,'unauthorized',{},None),
 urllib.error.HTTPError('https://example.invalid',429,'rate limited',{},None),
 urllib.error.HTTPError('https://example.invalid',503,'unavailable',{},None),
 urllib.error.URLError('offline'),
])
def test_lookup_errors_are_not_absence(monkeypatch,error):
    def fail(*a,**k):raise error
    monkeypatch.setattr(guard.urllib.request,'urlopen',fail)
    with pytest.raises(RuntimeError):guard.request('https://example.invalid')
