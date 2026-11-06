import asyncio
import copy
from unittest.mock import Mock

from porsche2lox.core import refresh_age
from porsche2lox.loxone import HEALTH_FIELDS, selected_copy_rows
from porsche2lox.mqtt import messages
from test_selected_copy import setup
from test_service import service


def cached():
    config,snapshots=setup('detailed')
    config.update(publish_fields=['soc','range_km','target_soc','direct_charge_enabled'],publish_parameters=[])
    snapshots['car_a'].update(soc=0,range_km=None,target_soc=80,direct_charge_enabled=0,
        data_valid=0,api_ok=0,auth_required=0,error_code=0,data_age_s=None,age_known=0,
        last_fetch_epoch=123,measurement_epoch=None)
    return config,snapshots


def test_detailed_diagnostics_match_actual_publisher_topics_and_zero_unknown_values():
    config,snapshots=cached();before=copy.deepcopy((config,snapshots))
    rows=selected_copy_rows(config,snapshots);by_topic={r['topic']:r for r in rows}
    published={}
    for vehicle in config['vehicles']:
        published.update(messages('custom_plx',vehicle['alias'],snapshots.get(vehicle['alias'],{}),[],config['publish_fields']))
    assert set(by_topic)<=set(published)|{'custom_plx/heartbeat'}
    for field in HEALTH_FIELDS:
        row=by_topic['custom_plx/car_a/'+field]
        assert row['group']=='diagnostic' and row['vehicle']=='car_a'
    for key in config['publish_fields']:
        assert by_topic['custom_plx/car_a/'+key+'_available']['group']=='diagnostic'
    assert by_topic['custom_plx/car_a/soc_available']['value']==1
    assert by_topic['custom_plx/car_a/range_km_available']['value']==0
    assert by_topic['custom_plx/car_a/data_valid']['value']==0
    assert by_topic['custom_plx/car_a/data_valid']['available'] is True
    assert by_topic['custom_plx/car_a/measurement_epoch']['value'] is None
    assert by_topic['custom_plx/car_a/measurement_epoch']['available'] is False
    assert (config,snapshots)==before


def test_heartbeat_is_global_once_and_has_no_invented_cached_timestamp():
    config,snapshots=cached();rows=selected_copy_rows(config,snapshots)
    heartbeat=[r for r in rows if r['topic'].endswith('/heartbeat')]
    assert len(heartbeat)==1
    assert heartbeat[0]['vehicle']=='' and heartbeat[0]['group']=='diagnostic'
    assert heartbeat[0]['value'] is None and heartbeat[0]['available'] is False
    assert heartbeat[0]['value_note']=='heartbeat_not_cached'
    assert heartbeat[0]['recognition']==r'MQTT:\icustom_plx/heartbeat=\i\v'
    # Missing cached health keys are not advertised as currently emitted routes.
    assert 'custom_plx/car_b/api_ok' not in {r['topic'] for r in rows}


def test_parameter_and_leaf_availability_diagnostics_use_the_same_publisher():
    config,snapshots=setup('detailed');rows=selected_copy_rows(config,snapshots)
    diagnostics={r['topic']:r for r in rows if r['group']=='diagnostic'}
    prefix='custom_plx/car_a/'
    assert diagnostics[prefix+'parameters/tire_pressure_front_right/available']['value']==0
    assert diagnostics[prefix+'parameters/tire_pressure_front_right/measurement_epoch']['value'] is None
    leaf=prefix+'fields/tire_pressure_front_right/actualPressureBar/available'
    assert diagnostics[leaf]['value']==0 and diagnostics[leaf]['available'] is True
    published=dict(messages('custom_plx','car_a',snapshots['car_a'],config['publish_parameters'],[]))
    assert all(topic in published for topic,row in diagnostics.items() if row['vehicle']=='car_a')


def test_simple_never_advertises_diagnostics_or_heartbeat():
    config,snapshots=cached();config['mqtt_format']='simple'
    rows=selected_copy_rows(config,snapshots)
    assert rows and all(r['group']=='measurement' for r in rows)
    assert not any(r['topic'].endswith(('/heartbeat','/data_valid','_available')) for r in rows)


def test_cached_rows_match_real_publish_status_payloads_with_synthetic_publisher(tmp_path,monkeypatch):
    publisher=Mock();app,adapter=service(tmp_path,publisher)
    app.config,app.snapshots=cached();app.config['mqtt']['enabled']=True
    monkeypatch.setattr('porsche2lox.service.time.time',lambda:200)
    # A send-attempt time is not proof of the heartbeat's last sent payload.
    app.last_mqtt=199
    before=copy.deepcopy((app.config,app.snapshots))
    result=asyncio.run(app.command({'action':'loxone_export','params':{'rows_only':True}}))
    publisher.assert_not_called()
    asyncio.run(app.publish_status())  # Mock only: no broker/network.
    payloads=dict(publisher.call_args.args[1])
    assert {r['topic'] for r in result['rows']}<=set(payloads)
    assert next(r for r in result['rows'] if r['topic']=='custom_plx/heartbeat')['value'] is None
    assert payloads['custom_plx/heartbeat']=='200'
    assert (app.config,app.snapshots)==before
    adapter.overview.assert_not_awaited();adapter.login.assert_not_awaited()
