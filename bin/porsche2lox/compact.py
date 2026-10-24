"""One last-reported measurement per topic; age/status remain in the UI."""
import json
import math

from .core import FIELDS
from .parameters import LABELS, READ_MEASUREMENTS

BASE = {'soc':('Akkustand','%'),'range_km':('Reichweite','km'),
        'target_soc':('Ladeziel','%'),'direct_charge_enabled':('Direktlademodus','0/1')}


def compact_rows(config, snapshots):
    rows = []
    def add(topic, label, value, unit='', numeric=False):
        if type(value) is bool:
            value = int(value)
        if type(value) is float and not math.isfinite(value):
            value = None
        kind = 'number' if numeric or type(value) in (int, float) else 'text'
        rows.append({'topic':topic, 'label':label, 'unit':unit, 'kind':kind,
                     'value':value, 'payload':json.dumps(value, ensure_ascii=False, allow_nan=False, separators=(',', ':'))})
    for vehicle in config['vehicles']:
        alias = vehicle['alias']
        base = config['mqtt']['prefix'] + '/' + alias
        snapshot = snapshots.get(alias, {})
        for name in config.get('publish_fields', FIELDS):
            label, unit = BASE[name]
            value = snapshot.get(name)
            add(base+'/'+name, alias+' · '+label, value, unit, True)
        parameters = snapshot.get('parameters', {})
        for name in config.get('publish_parameters', READ_MEASUREMENTS):
            parameter = parameters.get(name, {})
            value = parameter.get('value') if parameter.get('available') else None
            numeric = name.startswith('TIRE_PRESSURE_')
            if numeric:
                value = value.get('actualPressureBar') if isinstance(value, dict) else None
                if type(value) not in (int, float) or not math.isfinite(value) or value < 0:
                    value = None
            add(base+'/'+name.lower(), alias+' · '+LABELS.get(name,name), value, 'bar' if numeric else '', numeric)
    return rows
