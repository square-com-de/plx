import asyncio
import copy
import json
import time
from datetime import datetime, timezone
import xml.etree.ElementTree as ET

import pytest

from porsche2lox.compact import compact_rows
from porsche2lox.core import DEFAULTS, validate_config, write_private
from porsche2lox.loxone import enrich_schema, make_exports
from porsche2lox.mqtt import selection_deletions
from test_service import configured, service

TIRES = ['TIRE_PRESSURE_FRONT_LEFT', 'TIRE_PRESSURE_FRONT_RIGHT']


def config():
    c = configured()
    c.update(mqtt_format='simple', publish_fields=[], publish_parameters=TIRES[:])
    c['mqtt']['enabled'] = True
    return validate_config(c)


def snapshot():
    now = int(time.time())
    stamp = datetime.fromtimestamp(now, timezone.utc).isoformat()
    params = {name: {'available':1, 'data_valid':1, 'measurement_epoch':now,
                    'value':{'actualPressureBar':pressure, 'differenceBar':-.2, 'lastModified':stamp}}
              for name, pressure in zip(TIRES, [2.4, 2.5])}
    params['TRIP_STATISTICS_CYCLIC_HISTORY'] = {'available':1, 'data_valid':1,
        'value':{'list':[{'distanceKm':i,'avgSpeedKmh':20} for i in range(50)]}}
    return enrich_schema({'api_ok':1, 'parameters':params})


def test_exactly_two_pressure_numbers_without_metadata_history_or_json():
    rows = compact_rows(config(), {'taycan':snapshot()})
    assert [(r['topic'],r['payload']) for r in rows] == [
        ('porsche2lox/taycan/tire_pressure_front_left','2.4'),
        ('porsche2lox/taycan/tire_pressure_front_right','2.5')]
    assert all(r['unit']=='bar' and r['kind']=='number' for r in rows)


@pytest.mark.parametrize('change', ['unavailable','missing','nan','boolean','negative'])
def test_invalid_pressure_is_null_never_guessed_from_other_fields(change):
    s = snapshot();p = s['parameters'][TIRES[0]]
    if change == 'unavailable': p['available']=0
    if change == 'missing': del p['value']['actualPressureBar']
    if change == 'nan': p['value']['actualPressureBar']=float('nan')
    if change == 'boolean': p['value']['actualPressureBar']=True
    if change == 'negative': p['value']['actualPressureBar']=-.1
    assert compact_rows(config(), {'taycan':s})[0]['payload']=='null'


def test_real_zero_is_not_treated_as_missing():
    s=snapshot();s['parameters'][TIRES[0]]['value']['actualPressureBar']=0
    assert compact_rows(config(), {'taycan':s})[0]['payload']=='0'


def test_service_never_sweeps_unselected_catalog_or_publishes_shutdown_markers(tmp_path):
    async def run():
        calls=[];app,adapter=service(tmp_path,publisher=lambda c,v:calls.append(v))
        app.config=config();app.snapshots={'taycan':snapshot()}
        await app.publish_status()
        assert len(calls)==1 and len(calls[0])==2
        app.snapshots['taycan']['parameters']['TRIP_STATISTICS_CYCLIC_HISTORY']['value']['list'].extend([{'new':1}]*50)
        await app.publish_status()
        await app.publish_status(force_invalid=True)
        assert len(calls)==2 and all(len(batch)==2 for batch in calls)
        assert all(value not in ('','null') for batch in calls for _,value in batch)
        write_private(app.config_path,app.config)
        write_private(app.data_dir/'status.json',app.snapshots)
        restarted,_=service(tmp_path,publisher=lambda c,v:calls.append(v))
        await restarted.publish_status()
        assert len(calls[-1])==2
        assert all(value not in ('','null') for _,value in calls[-1])  # Last reported values survive restart.
        adapter.overview.assert_not_awaited()
    asyncio.run(run())


def test_simple_save_does_not_invalidate_and_allows_broker_repair(tmp_path):
    async def run():
        def unavailable(*_):raise OSError('old broker offline')
        app,_=service(tmp_path,publisher=unavailable);app.config=config()
        new=copy.deepcopy(app.config);new['mqtt']['host']='192.0.2.10'
        await app.command({'action':'save','params':new})
        assert app.config['mqtt']['host']=='192.0.2.10'
        assert app.config['publish_parameters']==TIRES
    asyncio.run(run())


def test_deselection_removes_only_previous_simple_topic():
    old=config();new=copy.deepcopy(old);new['publish_parameters']=TIRES[:1]
    assert selection_deletions(old,new,{'taycan':snapshot()})==[
        ('porsche2lox/taycan/tire_pressure_front_right','')]


def test_migration_deletes_only_actual_old_selected_routes_once(tmp_path):
    async def run():
        calls=[];app,_=service(tmp_path,publisher=lambda c,v:calls.append(v))
        app.config=config();app.config['mqtt_format']='detailed';app.snapshots={'taycan':snapshot()}
        new=copy.deepcopy(app.config);new['mqtt_format']='simple'
        await app.command({'action':'save','params':new})
        assert not calls and app.pending_cleanup
        await app.retry_cleanup()
        assert len(calls)==1 and len(calls[0])==29
        assert all(value=='' and 'history' not in topic for topic,value in calls[0])
        await app.publish_status()
        assert len(calls[-1])==2 and all(value!='' for _,value in calls[-1])
    asyncio.run(run())


def test_simple_export_matches_only_selected_topics_for_both_scopes():
    for scope in ['main','selected']:
        out=make_exports(config(),{'taycan':snapshot()},scope=scope)
        assert out['numeric_count']==2 and out['text_count']==0
        root=ET.fromstring(out['xml'])
        assert len(root.findall('VirtualInUdpCmd'))==2
        assert '/tire_pressure_front_left=' in out['xml']
        assert 'heartbeat' not in out['xml'] and 'available' not in out['xml']
        assert len(out['csv'].splitlines())==3


def test_existing_format_remains_compatible_and_new_install_is_simple():
    assert validate_config(DEFAULTS)['mqtt_format']=='simple'
    old=copy.deepcopy(DEFAULTS);del old['mqtt_format']
    assert validate_config(old)['mqtt_format']=='detailed'
    with pytest.raises(ValueError):validate_config({**DEFAULTS,'mqtt_format':'unknown'})


def test_simple_selection_save_preserves_measurements_and_cloud_schedule(tmp_path):
    async def run():
        app,adapter=service(tmp_path);app.config=config();app.snapshots={'taycan':snapshot()}
        app.next_poll=time.time()+600
        planned=app.next_poll
        new=copy.deepcopy(app.config);new['max_age_s']=7200
        await app.command({'action':'save','params':new})
        assert app.snapshots['taycan']['api_ok']==1
        assert app.next_poll==planned
        adapter.overview.assert_not_awaited()
    asyncio.run(run())


def test_older_settings_form_cannot_restore_detailed_output(tmp_path):
    async def run():
        app,_=service(tmp_path);app.config=config();app.snapshots={'taycan':snapshot()}
        old_form=copy.deepcopy(app.config);del old_form['mqtt_format']
        await app.command({'action':'save','params':old_form})
        assert app.config['mqtt_format']=='simple'
        assert len(compact_rows(app.config,app.snapshots))==2
    asyncio.run(run())


def test_simple_format_keeps_last_reported_pressure_when_age_is_unknown_or_stale():
    s=snapshot();s['api_ok']=0
    for p in s['parameters'].values():p.update(data_valid=0,age_known=0,measurement_epoch=None)
    rows=compact_rows(config(),{'taycan':s})
    assert [row['payload'] for row in rows]==['2.4','2.5']
