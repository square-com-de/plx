"""Stable MQTT leaf fields and selection-aware Loxone UDP template export."""
import csv
import hashlib
import io
import ipaddress
import math
import re
import xml.etree.ElementTree as ET
from datetime import datetime
from decimal import Decimal
from urllib.parse import quote

from .compact import compact_rows

BASE_FIELDS = {'soc':('Akkustand','%'),'range_km':('Reichweite','km'),'target_soc':('Ladeziel','%'),'direct_charge_enabled':('Direktlademodus','0/1')}
HEALTH_FIELDS = {'data_valid':'Datenfreigabe','api_ok':'API erreichbar','auth_required':'Anmeldung erforderlich','error_code':'Fehlercode','data_age_s':'Messalter','age_known':'Messalter bekannt','last_fetch_epoch':'Letzter Abruf','measurement_epoch':'Messzeitpunkt'}
# Explicit paired states only. Unknown texts are never silently turned into 0.
ENUMS = {'OPEN':1,'CLOSED':0,'LOCKED':1,'UNLOCKED':0,'ON':1,'OFF':0,'ACTIVE':1,'INACTIVE':0,'CONNECTED':1,'DISCONNECTED':0,'TRUE':1,'FALSE':0}


def mqtt_scalar(value):
    return format(Decimal(str(value)), 'f') if type(value) is float else str(value)


def path_id(path):
    text='/'.join(quote(str(p),safe='-_') for p in path) or 'value'
    return text if len(text)<=48 else text[:20]+'~'+hashlib.sha256(text.encode()).hexdigest()[:16]


def scalar(value):
    if type(value) is bool:return int(value),'number','0/1'
    if type(value) in (int,float):
        return (value,'number','') if math.isfinite(value) else (None,'number','')
    if isinstance(value,str):
        if value.upper() in ENUMS:return ENUMS[value.upper()],'number','0/1'
        try:
            date=datetime.fromisoformat(value.replace('Z','+00:00'))
            if date.tzinfo is not None:return int(date.timestamp()),'number','Unixzeit'
        except (ValueError,OverflowError):pass
        return value,'text','Text'
    return None,'unknown',''


def leaves(value, path=(), result=None):
    result={} if result is None else result
    if len(result)>=256 or len(path)>9:return result
    if isinstance(value,dict):
        for key,item in value.items():leaves(item,(*path,key),result)
    elif isinstance(value,list):
        for index,item in enumerate(value):leaves(item,(*path,str(index)),result)
    else:
        converted,kind,unit=scalar(value)
        if path and not unit:
            unit={'percent':'%','kilometers':'km','latitude':'°','longitude':'°'}.get(str(path[-1]),'')
        result[path_id(path)]={'value':converted,'kind':kind,'unit':unit,'label':' · '.join(map(str,path)) or 'Wert'}
    return result


def enrich_schema(snapshot, previous=None):
    """Keep known leaf paths so missing/newly unavailable fields can be cleared."""
    old=(previous or {}).get('parameters',{})
    for key,p in snapshot.get('parameters',{}).items():
        schema=dict(old.get(key,{}).get('field_schema',{}))
        current=leaves(p.get('value')) if p.get('available') else {}
        for path,field in current.items():
            if path not in schema and len(schema)>=512:continue
            if path in schema and (field['kind']=='unknown' or (schema[path]['kind']=='number' and field['kind']=='text')):continue
            schema[path]={k:field[k] for k in ('kind','unit','label')}
        p['field_schema']=schema
    return snapshot


def parameter_fields(parameter):
    current=leaves(parameter.get('value')) if parameter.get('available') else {}
    schema=dict(parameter.get('field_schema',{}))
    for path,field in current.items():
        if path not in schema or (field['kind']!='unknown' and not (schema[path].get('kind')=='number' and field['kind']=='text')):schema[path]={k:field[k] for k in ('kind','unit','label')}
    for path,meta in schema.items():
        value=current.get(path,{}).get('value')
        if meta.get('kind')=='number' and current.get(path,{}).get('kind')=='text':value=None
        yield path,{**meta,'value':value,'available':int(value is not None and bool(parameter.get('available')))}


def flat_topics(prefix, alias, name, parameter):
    base=f'{prefix}/{alias}/fields/{name.lower()}'
    for path,field in parameter_fields(parameter):
        yield f'{base}/{path}',field


def export_rows(config,snapshots):
    if config.get('mqtt_format', 'detailed') == 'simple':
        return [{k:row[k] for k in ('topic','label','unit','kind')} for row in compact_rows(config,snapshots)]
    from .parameters import READ_MEASUREMENTS
    rows=[]
    def add(topic,label,unit='',kind='number'):
        rows.append({'topic':topic,'label':label,'unit':unit,'kind':kind})
    for vehicle in config['vehicles']:
        alias=vehicle['alias'];base=f"{config['mqtt']['prefix']}/{alias}"
        for key in config.get('publish_fields',BASE_FIELDS):
            label,unit=BASE_FIELDS[key]
            add(f'{base}/{key}',f'{alias} · {label}',unit)
            add(f'{base}/{key}_available',f'{alias} · {label} verfügbar','0/1')
        for key,label in HEALTH_FIELDS.items():
            add(f'{base}/{key}',f'{alias} · {label}','Unixzeit' if key.endswith('_epoch') else 's' if key=='data_age_s' else '')
        parameters=snapshots.get(alias,{}).get('parameters',{})
        for name in config.get('publish_parameters',READ_MEASUREMENTS):
            p=parameters.get(name,{})
            label=f"{alias} · {p.get('label',name)}"
            group=f'{base}/parameters/{name.lower()}'
            for field,suffix,unit in [('available','verfügbar','0/1'),('data_valid','gültig','0/1'),('measurement_epoch','Messzeitpunkt','Unixzeit')]:
                add(f'{group}/{field}',f'{label} · {suffix}',unit)
            for route,field in flat_topics(config['mqtt']['prefix'],alias,name,p):
                add(route+'/value',label+' · '+field['label'],field['unit'],field['kind'])
                add(route+'/available',label+' · '+field['label']+' verfügbar','0/1')
    add(config['mqtt']['prefix']+'/heartbeat','PLX · Heartbeat','Unixzeit')
    return rows


def make_exports(config,snapshots,port=11883,source='',scope='selected'):
    if type(port) is not int or not 1<=port<=65535:raise ValueError('UDP-Port zwischen 1 und 65535 angeben.')
    if not isinstance(source,str):raise ValueError('Ungültige Absender-IP.')
    if source:
        try:source=str(ipaddress.ip_address(source))
        except ValueError:raise ValueError('Bitte eine gültige Absender-IP oder ein leeres Feld angeben.') from None
    if not config['vehicles']:raise ValueError('Bitte zuerst ein Fahrzeug auswählen und speichern.')
    if scope not in ('main','selected'):raise ValueError('Ungültiger Exportumfang.')
    if scope=='main' and config.get('mqtt_format','detailed')!='simple':config=dict(config,publish_parameters=[])
    rows=export_rows(config,snapshots)
    root=ET.Element('VirtualInUdp',Title='PLX',Comment='MQTT Gateway · gespeicherte Datenauswahl',Address=source,Port=str(port))
    ET.SubElement(root,'Info',templateType='1',minVersion='14051207')
    numeric=0;text=0;too_long=0
    for row in rows:
        if row['kind']!='number':text+=1;continue
        # The LoxBerry SDK bundles pairs into 220-character UDP packets.
        if len(row['topic'].encode())+40>220:too_long+=1;continue
        check='MQTT:\\i'+row['topic']+'=\\i\\v'
        comment=row['topic']+('; Zuletzt gemeldeter Wert; nicht verfügbar: null.' if config.get('mqtt_format')=='simple' else '; Freigabe/Verfügbarkeit und Heartbeat beachten.')
        if row['unit']=='0/1':comment+=' Zustände: open/locked/on/active/connected=1, Gegenwert=0 (je nach Feld).'
        ET.SubElement(root,'VirtualInUdpCmd',Title=row['label'],Comment=comment,Address='',Check=check,Signed='true',Analog='true',SourceValLow='0',DestValLow='0',SourceValHigh='100',DestValHigh='100',DefVal='0',MinVal='-9007199254740991',MaxVal='9007199254740991',Unit='<v>'+(' '+row['unit'] if row['unit'] not in ('0/1','Unixzeit','') else ''),HintText=('Zuletzt gemeldeter Wert; fehlend: null. Messalter in PLX.' if config.get('mqtt_format')=='simple' else 'Unbekannte Werte sind nicht 0. Freigabesignale verwenden.'))
        numeric+=1
    ET.indent(root,space='\t')
    xml='\ufeff<?xml version="1.0" encoding="utf-8"?>\r\n'+ET.tostring(root,encoding='unicode').replace('\n','\r\n')+'\r\n'
    output=io.StringIO();writer=csv.writer(output,delimiter=';',lineterminator='\r\n')
    writer.writerow(['Topic','Bezeichnung','Einheit','Typ','UDP-Befehlserkennung'])
    for row in rows:writer.writerow([row['topic'],row['label'],row['unit'],row['kind'],'MQTT:\\i'+row['topic']+'=\\i\\v' if row['kind']=='number' else 'Text: HTTP-Texteingang verwenden'])
    return {'xml':xml,'csv':'\ufeff'+output.getvalue(),'numeric_count':numeric,'text_count':text,'too_long_count':too_long,'port':port,'subscriptions':[config['mqtt']['prefix']+'/#']}
