import copy
import xml.etree.ElementTree as ET

import pytest

from porsche2lox.core import parse_overview, validate_config
from porsche2lox.loxone import enrich_schema, leaves, make_exports, path_id
from porsche2lox.mqtt import messages, selection_deletions
from test_core import payload,VIN,NOW
from test_service import configured


def snapshot():
    p=payload()
    p['measurements'].append({'key':'HVAC_SUMMARY','status':{'isEnabled':True},'value':{'active':False,'mode':'STANDBY','lastModified':'2026-10-19T17:00:00Z','target':{'temperature':20.5}}})
    return enrich_schema(parse_overview(p,VIN,NOW,3600))


def test_flat_fields_numbers_states_dates_and_unknown_text():
    s=snapshot();m=dict(messages('p2l','car',s,['HVAC_SUMMARY'],[]))
    base='p2l/car/fields/hvac_summary/'
    assert m[base+'active/value']=='0'
    assert m[base+'active/available']=='1'
    assert m[base+'target/temperature/value']=='20.5'
    assert m[base+'mode/value']=='STANDBY'
    assert m[base+'lastModified/value'].isdigit()
    assert not any('/battery_level/' in key for key in m)


def test_disappearing_field_clears_value_and_keeps_export_schema():
    old=snapshot();new=copy.deepcopy(old)
    del new['parameters']['HVAC_SUMMARY']['value']['target']
    enrich_schema(new,old)
    m=dict(messages('p2l','car',new,['HVAC_SUMMARY'],[]))
    assert m['p2l/car/fields/hvac_summary/target/temperature/value']==''
    assert m['p2l/car/fields/hvac_summary/target/temperature/available']=='0'
    new['parameters']['HVAC_SUMMARY']['value']['active']='unknown'
    enrich_schema(new,old)
    m=dict(messages('p2l','car',new,['HVAC_SUMMARY'],[]))
    assert m['p2l/car/fields/hvac_summary/active/available']=='0'


def test_export_xml_matches_selection_and_excludes_text_and_values():
    config=validate_config(configured());config['publish_fields']=['soc'];config['publish_parameters']=['HVAC_SUMMARY']
    output=make_exports(config,{'taycan':snapshot()},11883,'192.168.1.79')
    assert output['xml'].startswith('\ufeff<?xml')
    root=ET.fromstring(output['xml'])
    assert root.tag=='VirtualInUdp' and root.attrib['Port']=='11883'
    assert root[0].tag=='Info' and root[0].attrib['templateType']=='1'
    checks={n.attrib['Check'] for n in root.findall('VirtualInUdpCmd')}
    assert r'MQTT:\iporsche2lox/taycan/soc=\i\v' in checks
    assert r'MQTT:\iporsche2lox/taycan/fields/hvac_summary/active/value=\i\v' in checks
    assert not any('/mode/value=' in c for c in checks)
    assert not any('/range_km=' in c for c in checks)
    assert 'STANDBY' not in output['xml'] and 'STANDBY' not in output['csv']
    assert output['text_count']==1
    assert output['numeric_count']==len(checks)
    assert '\r\n' in output['xml']


@pytest.mark.parametrize('port,source',[(0,''),(65536,''),(True,''),(11883,'<bad>'),(11883,'example.com')])
def test_invalid_export_settings_rejected(port,source):
    with pytest.raises(ValueError):make_exports(validate_config(configured()),{},port,source)


def test_flat_paths_collision_safe_and_deselection_deletes_leaves():
    assert path_id(('a/b',))!=path_id(('a','b'))
    assert path_id(('verylong'*30,))!=path_id(('verylong'*30+'x',))
    old=validate_config(configured());new={**old,'publish_parameters':[]}
    deleted=dict(selection_deletions(old,new,{'taycan':snapshot()}))
    base='porsche2lox/taycan/fields/hvac_summary/active'
    assert deleted[base+'/value']=='' and deleted[base+'/available']==''


def test_xml_escapes_special_field_labels():
    s=snapshot();s['parameters']['HVAC_SUMMARY']['field_schema']['active']['label']='Test < & " >'
    config=validate_config(configured());config['publish_parameters']=['HVAC_SUMMARY']
    ET.fromstring(make_exports(config,{'taycan':s})['xml'])


def test_recommended_main_export_and_single_subscription():
    c=validate_config(configured());s={'taycan':snapshot()}
    result=make_exports(c,s,scope='main')
    assert result['numeric_count']==17
    assert '/fields/' not in result['xml']
    assert result['subscriptions']==['porsche2lox/#']
    c['mqtt']['prefix']='plx-test'
    assert make_exports(c,s,scope='selected')['subscriptions']==['plx-test/#']
    assert c['publish_parameters']  # Export never changes the saved selection.
    with pytest.raises(ValueError):make_exports(c,s,scope='unknown')
