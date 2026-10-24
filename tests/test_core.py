import copy
import json
import stat

import pytest

from porsche2lox.core import DEFAULTS, DataError, parse_overview, refresh_age, validate_config, write_private
from porsche2lox.mqtt import messages

VIN = 'WP0ZZZY1ZLSA12345'
NOW = 1792429200


def payload(battery=42, timestamp='2026-10-19T17:00:00Z'):
    value = {} if battery is None else {'percent': battery}
    if timestamp:
        value['lastModified'] = timestamp
    return {'vin': VIN, 'measurements': [
        {'key': 'BATTERY_LEVEL', 'status': {'isEnabled': True}, 'value': value},
        {'key': 'E_RANGE', 'status': {'isEnabled': True}, 'value': {'kilometers': 180}},
    ]}


@pytest.mark.parametrize('value', [None, True, '42', -1, 101, float('nan')])
def test_missing_invalid_battery_never_becomes_zero(value):
    result = parse_overview(payload(value), VIN, NOW, 3600)
    assert result["soc"] is None
    assert result["data_valid"] == 0
    assert result["range_km"] == 180


def test_real_zero_valid_and_timezones():
    result = parse_overview(payload(0, '2026-10-19T19:00:00+02:00'), VIN, NOW, 3600)
    assert result['soc'] == 0
    assert result['data_age_s'] == 0
    assert result['data_valid'] == 1


@pytest.mark.parametrize('timestamp', [None, 'invalid', '2026-10-19T17:00:00', '2026-10-18T17:00:00Z', '2026-10-20T17:00:00Z'])
def test_unknown_stale_and_future_measurements_invalid(timestamp):
    assert parse_overview(payload(timestamp=timestamp), VIN, NOW, 3600)['data_valid'] == 0


def test_disabled_battery_does_not_hide_other_measurements():
    data = payload()
    data['measurements'][0]['status']['isEnabled'] = False
    result = parse_overview(data, VIN, NOW, 3600)
    assert result["soc"] is None
    assert result["parameters"]["E_RANGE"]["available"] == 1


def test_wrong_vehicle_rejected():
    with pytest.raises(DataError):
        parse_overview(payload(), 'WP0ZZZY1ZLSA99999', NOW, 3600)


def test_profile_minimum_is_not_target_and_missing_mode_unknown():
    data = payload()
    data['measurements'].append({'key':'CHARGING_SUMMARY','status':{'isEnabled':True}, 'value':{'mode':'PROFILE','chargingProfile':{'minSoC':25}}})
    result = parse_overview(data, VIN, NOW, 3600)
    assert result['target_soc'] is None
    assert result['direct_charge_enabled'] == 0
    assert parse_overview(payload(), VIN, NOW, 3600)['direct_charge_enabled'] is None


def test_explicit_target_and_direct():
    data = payload()
    data['measurements'].append({'key':'CHARGING_SUMMARY','status':{'isEnabled':True}, 'value':{'mode':'DIRECT','targetSoC':80}})
    result = parse_overview(data, VIN, NOW, 3600)
    assert result['target_soc'] == 80
    assert result['direct_charge_enabled'] == 1


def test_staleness_advances_without_api_calls():
    data = parse_overview(payload(), VIN, NOW, 3600)
    assert refresh_age(data, NOW + 3601, 3600)['data_valid'] == 0
    data['api_ok'] = 0
    assert refresh_age(data, NOW, 3600)['data_valid'] == 0


def test_unknown_optional_value_deletes_retained_and_sets_flag():
    snapshot = parse_overview(payload(), VIN, NOW, 3600)
    result = messages('porsche2lox', 'test', snapshot)
    assert ('porsche2lox/test/target_soc', '') in result
    assert ('porsche2lox/test/target_soc_available', '0') in result
    assert result[0] == ('porsche2lox/test/data_valid', '0')
    assert result[-1] == ('porsche2lox/test/data_valid', '1')


def test_private_atomic_write(tmp_path):
    path = tmp_path / 'session.json'
    write_private(path, {'access_token':'test'})
    assert stat.S_IMODE(path.stat().st_mode) == 0o600
    assert json.loads(path.read_text())['access_token'] == 'test'
    assert list(tmp_path.iterdir()) == [path]


def test_default_disabled_and_unique_aliases():
    config = validate_config(DEFAULTS)
    assert not config['enabled'] and not config['mqtt']['enabled']
    config['vehicles'] = [{'vin':VIN,'alias':'porsche'}, {'vin':'WP0ZZZY1ZLSA99999','alias':'porsche'}]
    with pytest.raises(ValueError):
        validate_config(config)


@pytest.mark.parametrize('prefix', ['porsche/taycan', '#', 'x/../../y', 'test\n', '', '+'])
def test_prefix_never_overwrites_old_app(prefix):
    config = copy.deepcopy(DEFAULTS)
    config['mqtt']['prefix'] = prefix
    with pytest.raises(ValueError):
        validate_config(config)
