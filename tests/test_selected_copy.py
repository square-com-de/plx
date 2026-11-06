import asyncio
import copy
import xml.etree.ElementTree as ET
from unittest.mock import Mock

from porsche2lox.core import DEFAULTS, validate_config
from porsche2lox.loxone import make_exports, selected_copy_rows
from porsche2lox.mqtt import messages
from test_service import service


def setup(format='simple'):
    config=copy.deepcopy(DEFAULTS)
    config.update(mqtt_format=format,vehicles=[{'vin':'AAAAAAAAAAAAAAAAA','alias':'car_a'},{'vin':'BBBBBBBBBBBBBBBBB','alias':'car_b'}],
                  publish_fields=[],publish_parameters=['TIRE_PRESSURE_FRONT_LEFT','TIRE_PRESSURE_FRONT_RIGHT'])
    config['mqtt']['prefix']='custom_plx'
    snapshots={'car_a':{'parameters':{
        'TIRE_PRESSURE_FRONT_LEFT':{'label':'Reifendruck vorne links','available':1,'value':{'actualPressureBar':2.4}},
        'TIRE_PRESSURE_FRONT_RIGHT':{'label':'Reifendruck vorne rechts','available':0,'value':None,
                                     'field_schema':{'actualPressureBar':{'kind':'number','unit':'bar','label':'actualPressureBar'}}}}}}
    return validate_config(config),snapshots


def test_simple_selection_custom_prefix_multiple_aliases_and_missing_values():
    config,snapshots=setup();before=copy.deepcopy((config,snapshots))
    rows=selected_copy_rows(config,snapshots)
    assert len(rows)==4
    assert rows[0]['topic']=='custom_plx/car_a/tire_pressure_front_left'
    assert rows[0]['value']==2.4 and rows[0]['unit']=='bar' and rows[0]['available']
    assert rows[0]['recognition']==r'MQTT:\icustom_plx/car_a/tire_pressure_front_left=\i\v'
    assert rows[1]['value'] is None and not rows[1]['available']
    assert rows[2]['vehicle']=='car_b' and not rows[2]['available']
    assert (config,snapshots)==before
    config['publish_parameters']=[]
    assert selected_copy_rows(config,snapshots)==[]


def test_detailed_copy_uses_published_leaf_routes_and_exact_xml_recognitions():
    config,snapshots=setup('detailed');rows=selected_copy_rows(config,snapshots)
    assert len(rows)==2  # car_b has no cached leaf schema yet, not invented.
    assert rows[0]['topic']=='custom_plx/car_a/fields/tire_pressure_front_left/actualPressureBar/value'
    published=dict(messages('custom_plx','car_a',snapshots['car_a'],config['publish_parameters'],[]))
    assert published[rows[0]['topic']]=='2.4'
    assert rows[1]['topic'] in published and published[rows[1]['topic']]==''
    exported=make_exports(config,snapshots)
    checks={n.attrib['Check'] for n in ET.fromstring(exported['xml']).findall('VirtualInUdpCmd')}
    assert {r['recognition'] for r in rows} <= checks
    assert all(r['unit']=='bar' for r in rows)
    assert not any('/available' in r['topic'] or '/heartbeat' in r['topic'] for r in rows)


def test_text_and_oversized_topics_never_offer_a_false_udp_recognition():
    config,snapshots=setup('detailed');config['vehicles']=config['vehicles'][:1];config['publish_parameters']=['HVAC_SUMMARY']
    snapshots['car_a']['parameters']={'HVAC_SUMMARY':{'available':1,'label':'Klima','value':{'mode':'STANDBY','active':False}}}
    rows=selected_copy_rows(config,snapshots)
    text=next(r for r in rows if r['kind']=='text');numeric=next(r for r in rows if r['kind']=='number')
    assert text['value']=='STANDBY' and text['recognition'] is None and text['unsupported']=='text'
    assert numeric['value']==0 and numeric['available'] and numeric['recognition']
    config['mqtt']['prefix']='p'*80
    config['vehicles'][0]['alias']='c'*32
    snapshots['c'*32]=snapshots.pop('car_a')
    snapshots['c'*32]['parameters']['HVAC_SUMMARY']['value']={'mode':'STANDBY','n'*48:2.4}
    rows=selected_copy_rows(config,snapshots)
    assert all(r['recognition'] is None for r in rows)
    assert next(r for r in rows if r['kind']=='number')['unsupported']=='too_long'
    result=make_exports(config,snapshots)
    assert result['too_long_count']==2 and 'Topic für UDP zu lang' in result['csv']


def test_copy_rows_request_does_not_save_publish_or_request_porsche(tmp_path):
    publisher=Mock();app,adapter=service(tmp_path,publisher=publisher)
    app.config,app.snapshots=setup()
    before=copy.deepcopy((app.config,app.snapshots,app.job))
    files={p:p.read_bytes() for p in tmp_path.rglob('*') if p.is_file()}
    result=asyncio.run(app.command({'action':'loxone_export','params':{'rows_only':True}}))
    assert len(result['rows'])==4
    assert (app.config,app.snapshots,app.job)==before
    assert {p:p.read_bytes() for p in tmp_path.rglob('*') if p.is_file()}==files
    publisher.assert_not_called()
    adapter.overview.assert_not_awaited();adapter.vehicles.assert_not_awaited();adapter.login.assert_not_awaited()


def test_scalar_main_value_selection_and_false_are_not_treated_as_missing():
    for format in ('simple','detailed'):
        config,snapshots=setup(format)
        config['vehicles']=config['vehicles'][:1]
        config.update(publish_fields=['soc','direct_charge_enabled'],publish_parameters=[])
        snapshots['car_a'].update(soc=0,direct_charge_enabled=0)
        rows=selected_copy_rows(config,snapshots)
        assert [r['topic'] for r in rows]==['custom_plx/car_a/soc','custom_plx/car_a/direct_charge_enabled']
        assert all(r['available'] and r['value']==0 and r['recognition'] for r in rows)
        assert not any('range_km' in r['topic'] for r in rows)
