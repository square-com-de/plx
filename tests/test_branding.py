import importlib.util
import io
from pathlib import Path
import zipfile
import pytest
spec=importlib.util.spec_from_file_location('check_branding',Path(__file__).resolve().parents[1]/'tools/check_branding.py')
branding=importlib.util.module_from_spec(spec);spec.loader.exec_module(branding)

def test_approved_original_and_both_delivery_wrappers():
    assert branding.check_source()>0

def test_known_branding_is_rejected_inside_nested_archives(monkeypatch):
    # Synthetic bytes exercise archive scanning without storing the real old logo.
    old=b'synthetic obsolete branding fixture'
    monkeypatch.setattr(branding,'OLD_SVG',branding.digest(old))
    inner=io.BytesIO()
    with zipfile.ZipFile(inner,'w') as z:z.writestr('neutral-name.bin',old)
    outer=io.BytesIO()
    with zipfile.ZipFile(outer,'w') as z:z.writestr('nested.zip',inner.getvalue())
    with pytest.raises(ValueError,match='neutral-name.bin'):
        branding.inspect_bytes('candidate.zip',outer.getvalue())

def test_clean_archive_is_accepted():
    data=io.BytesIO()
    with zipfile.ZipFile(data,'w') as z:z.writestr('harmless.txt','PLX')
    branding.inspect_bytes('candidate.zip',data.getvalue())
