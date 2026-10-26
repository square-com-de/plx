import asyncio
import copy

import pytest

from porsche2lox.core import DEFAULTS, validate_config, parse_overview
from porsche2lox.mqtt import messages, selection_deletions
from porsche2lox.parameters import READ_MEASUREMENTS
from test_core import payload, VIN, NOW
from test_service import service, configured


def test_default_keeps_existing_topics_and_none_is_explicit():
    full=validate_config(DEFAULTS)
    assert full['publish_parameters']==list(READ_MEASUREMENTS)
    assert len(full['publish_fields'])==4
    config={**DEFAULTS,'publish_parameters':[],'publish_fields':[]}
    assert validate_config(config)['publish_parameters']==[]
    with pytest.raises(ValueError):validate_config({**DEFAULTS,'publish_parameters':['PAIRING_CODE']})


def test_publish_only_selected_data_but_keep_health():
    snapshot=parse_overview(payload(),VIN,NOW,3600)
    result=dict(messages('test','car',snapshot,['E_RANGE'],['range_km']))
    assert 'test/car/range_km' in result
    assert 'test/car/soc' not in result
    assert 'test/car/soc_available' not in result
    assert 'test/car/parameters/e_range/value' in result
    assert not any('/battery_level/' in key for key in result)
    assert result['test/car/api_ok']=='1'
    empty=dict(messages('test','car',snapshot,[],[]))
    assert not any('/parameters/' in key for key in empty)
    assert not any(key.endswith('/range_km') for key in empty)
    assert 'test/car/data_valid' in empty


def test_deselection_deletes_all_retained_parameter_routes():
    old=validate_config(configured())
    new={**old,'publish_fields':[],'publish_parameters':[]}
    deleted=dict(selection_deletions(old,new))
    base=old['mqtt']['prefix']+'/taycan'
    assert deleted[base+'/soc']==''
    assert deleted[base+'/soc_available']==''
    for field in ('value','available','data_valid','measurement_epoch'):
        assert deleted[base+'/parameters/gps_location/'+field]==''
    assert base+'/api_ok' not in deleted


def test_save_deselection_queues_cleanup_without_blocking_persistence(tmp_path):
    async def run():
        calls=[]
        app,_=service(tmp_path, publisher=lambda config,values:calls.append(values))
        app.config=validate_config(configured());app.config['mqtt']['enabled']=True
        app.snapshots={'taycan':parse_overview(payload(),VIN,NOW,3600)}
        new=copy.deepcopy(app.config);new['publish_parameters']=[];new['publish_fields']=[]
        await app.command({'action':'save','params':new})
        assert app.config['publish_parameters']==[]
        assert not calls and app.pending_cleanup
        await app.retry_cleanup()
        assert any((app.config['mqtt']['prefix']+'/taycan/parameters/e_range/value','') in values for values in calls)
    asyncio.run(run())


def test_enable_mqtt_does_not_delete_unselected_catalog_topics(tmp_path):
    async def run():
        calls=[]
        app,_=service(tmp_path,publisher=lambda config,values:calls.append(values))
        app.config=validate_config(configured())
        app.config['mqtt']['enabled']=True
        app.config['publish_parameters']=[];app.config['publish_fields']=[]
        await app.publish_status()
        key=app.config['mqtt']['prefix']+'/taycan/parameters/gps_location/value'
        assert (key,'') not in calls[-1]
        await app.publish_status()
        assert not any(topic==key for topic,_ in calls[-1])
    asyncio.run(run())
