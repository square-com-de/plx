import json
from porsche2lox.core import parse_overview, refresh_age
from porsche2lox.parameters import READ_MEASUREMENTS
from porsche2lox.mqtt import messages
from test_core import payload, VIN, NOW


def test_parameters_keep_zero_and_false_and_independent_timestamps():
    data=payload(timestamp='2026-10-18T17:00:00Z')
    data['measurements'].append({'key':'HVAC_SUMMARY','status':{'isEnabled':True},'value':{'active':False,'temperature':0,'lastModified':'2026-10-19T17:00:00Z'}})
    s=parse_overview(data,VIN,NOW,3600)
    assert s['data_valid']==0
    p=s['parameters']['HVAC_SUMMARY']
    assert p['value']['active'] is False and p['value']['temperature']==0
    assert p['data_valid']==1
    old=refresh_age(s,NOW+3601,3600)
    assert old['parameters']['HVAC_SUMMARY']['data_valid']==0
    assert s['parameters']['HVAC_SUMMARY']['data_valid']==1


def test_missing_parameters_not_zero_and_pairing_credentials_excluded():
    s=parse_overview(payload(),VIN,NOW,3600)
    assert s['parameters']['GPS_LOCATION']['available']==0
    assert s['parameters']['GPS_LOCATION']['value'] is None
    assert 'PAIRING_CODE' not in READ_MEASUREMENTS
    assert 'MDK_PAIRING_PASSWORD' not in READ_MEASUREMENTS


def test_nested_secrets_never_reach_status_or_mqtt():
    data=payload()
    data['measurements'].append({'key':'CHARGING_SETTINGS','status':{'isEnabled':True},'value':{'targetSoc':80,'token':'secret-value','nested':{'password':'private-value'}}})
    s=parse_overview(data,VIN,NOW,3600)
    wire=json.dumps(s)
    assert 'secret-value' not in wire and 'private-value' not in wire
    m=dict(messages('porsche2lox','test',refresh_age(s,NOW,3600)))
    assert 'parameters' not in m
    assert json.loads(m['porsche2lox/test/parameters/charging_settings/value'])['targetSoc']==80
    assert m['porsche2lox/test/parameters/gps_location/value']==''
    assert m['porsche2lox/test/parameters/gps_location/available']=='0'
