"""Read-only measurement catalogue and bounded, secret-free status values."""
import json
import math
import re
from .core import epoch
from pyporscheconnectapi.const import MEASUREMENTS, TRIP_STATISTICS, HISTORY_MEASUREMENTS, DESTINATIONS

# Pairing credentials and digital-key payloads do not belong in status or MQTT.
EXCLUDED = {'MDK_PAIRING_PASSWORD', 'PAIRING_CODE', 'BLEID_DDADATA', 'VTS_CERTIFICATE_LIST'}
READ_MEASUREMENTS = tuple(dict.fromkeys(k for k in [*MEASUREMENTS, *TRIP_STATISTICS, *HISTORY_MEASUREMENTS, *DESTINATIONS] if k not in EXCLUDED))
LABELS = {
 'BATTERY_LEVEL':'Akkustand', 'BATTERY_CONDITION':'Batteriezustand', 'BEM_LEVEL':'Batteriemanagement',
 'E_RANGE':'Elektrische Reichweite', 'RANGE':'Gesamtreichweite', 'CHARGING_RATE':'Ladeleistung und Ladegeschwindigkeit',
 'CHARGING_SESSION':'Ladevorgang', 'CHARGING_SUMMARY':'Ladeübersicht', 'CHARGING_SETTINGS':'Ladeeinstellungen',
 'CHARGING_PROFILES':'Ladeprofile', 'DIRECT_CHARGING':'Direktladen', 'DEPARTURES':'Abfahrtszeiten',
 'HVAC_SUMMARY':'Klimatisierung', 'MILEAGE':'Kilometerstand', 'GPS_LOCATION':'Standort',
 'LOCK_STATE_VEHICLE':'Verriegelung', 'PARKING_BRAKE':'Parkbremse', 'PARKING_LIGHT':'Parklicht',
 'GLOBAL_TIMESTAMP':'Fahrzeug-Zeitstempel', 'GLOBAL_PRIVACY_MODE':'Privatsphäre', 'CONNECT_CONTRACT':'Connect-Vertrag',
 'ALARM_STATE':'Alarmanlage', 'THEFT_STATE':'Diebstahlstatus', 'TIMERS':'Timer', 'TIMEZONE':'Zeitzone',
 'FUEL_LEVEL':'Tankfüllstand', 'FUEL_RESERVE':'Kraftstoffreserve', 'INSTRUMENT_CLUSTER_ALERTS':'Fahrzeugmeldungen',
 'SERVICE_PREDICTIONS':'Wartungsprognose', 'DESTINATIONS':'Navigationsziele',
}
POSITIONS = {'FRONT_LEFT':'vorne links','FRONT_RIGHT':'vorne rechts','REAR_LEFT':'hinten links','REAR_RIGHT':'hinten rechts'}
for position, label in POSITIONS.items():
 LABELS['TIRE_PRESSURE_'+position] = 'Reifendruck '+label
 LABELS['OPEN_STATE_DOOR_'+position] = 'Tür '+label
 LABELS['OPEN_STATE_WINDOW_'+position] = 'Fenster '+label
LABELS.update({'OPEN_STATE_LID_FRONT':'Fronthaube','OPEN_STATE_LID_REAR':'Heckklappe','OPEN_STATE_SERVICE_FLAP':'Serviceklappe','OPEN_STATE_SPOILER':'Spoiler','OPEN_STATE_SUNROOF':'Schiebedach','OPEN_STATE_SUNROOF_REAR':'Schiebedach hinten','OPEN_STATE_TOP':'Verdeck'})
for prefix, label in [('MAIN','Hauptservice'),('INTERMEDIATE','Zwischenservice'),('OIL','Ölservice')]:
 LABELS[prefix+'_SERVICE_RANGE']=label+' · Kilometer'
 LABELS[prefix+'_SERVICE_TIME']=label+' · Zeit'
for prefix, label in [('SHORT_TERM','Kurzzeit'),('LONG_TERM','Langzeit'),('CYCLIC','Zyklus'),('MONTHLY_REPORT','Monatsbericht')]:
 LABELS['TRIP_STATISTICS_'+prefix]='Fahrtstatistik · '+label
 LABELS['TRIP_STATISTICS_'+prefix+'_HISTORY']='Fahrthistorie · '+label


def category(key):
 if key.startswith(('BATTERY','BEM','CHARG','DIRECT','E_RANGE','DEPART')):return 'Batterie & Laden'
 if key.startswith(('OPEN_','LOCK_','TIRE_','PARK','ALARM','THEFT','VALET','VTS','LOCATION_ALARM','SPEED_ALARM')):return 'Fahrzeug & Sicherheit'
 if key.startswith(('HVAC','TIMER')):return 'Klima & Timer'
 if key.startswith(('GPS','TRIP','DESTIN','MILEAGE','RANGE','FUEL')):return 'Standort & Fahrten'
 if 'SERVICE' in key or key.startswith(('OIL','INSTRUMENT','OTA')):return 'Wartung & Meldungen'
 return 'Weitere Fahrzeugdaten'


def clean_value(value, depth=0):
 if depth > 8:return None
 if isinstance(value, dict):
  return {str(k)[:80]:clean_value(v,depth+1) for k,v in list(value.items())[:100]
          if not re.search(r'password|secret|token|pin$|pairing.?code|certificate|authorization',str(k),re.I)}
 if isinstance(value,list):return [clean_value(v,depth+1) for v in value[:50]]
 if isinstance(value,str):return value[:1000]
 if type(value) is float and not math.isfinite(value):return None
 if value is None or type(value) in (int,float,bool):return value
 return None


def parse_parameters(measurements, now, max_age):
 by_key={m.get('key'):m for m in measurements if isinstance(m,dict) and m.get('key') in READ_MEASUREMENTS}
 result={}
 for key in READ_MEASUREMENTS:
  m=by_key.get(key,{})
  status=m.get('status') if isinstance(m.get('status'),dict) else {}
  available=status.get('isEnabled') is True and isinstance(m.get('value'),(dict,list,int,float,bool,str))
  value=clean_value(m.get('value')) if available else None
  if len(json.dumps(value,ensure_ascii=False))>12000:
   value={'summary':'Antwort zu umfangreich für die Statusansicht.'}
  measured=epoch(m.get('value',{}).get('lastModified')) if isinstance(m.get('value'),dict) else None
  if measured is None:measured=epoch(m.get('lastModified'))
  age=now-measured if measured is not None else None
  result[key]={'label':LABELS.get(key,key.replace('_',' ').capitalize()),'group':category(key),
   'available':int(available),'value':value,'measurement_epoch':measured,
   'data_age_s':max(0,age) if age is not None else None,'age_known':int(age is not None),
   'data_valid':int(available and age is not None and -300<=age<=max_age),
   'reason':str(status.get('cause') or status.get('code') or 'Nicht verfügbar')[:160] if not available else ''}
 return result


def refresh_parameters(parameters, now, max_age, api_ok):
 result={}
 for key,p in parameters.items():
  p=dict(p);measured=p.get('measurement_epoch');age=now-measured if measured is not None else None
  p['data_age_s']=max(0,age) if age is not None else None
  p['data_valid']=int(bool(api_ok) and bool(p.get('available')) and age is not None and -300<=age<=max_age)
  result[key]=p
 return result
