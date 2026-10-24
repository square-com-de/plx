# PLX manual

[Deutsch](MANUAL.de.md) · [Installation](../INSTALL.md) · [Project page](../README.md)

## Overview and Porsche account

Overview shows your selected vehicles, battery, range and measurement age where available. “Cloud fetch” is when PLX requested the data; it is not the time the vehicle measured it. The connection label describes the Porsche session, not the freshness of every measurement.

In Porsche account, sign in, complete CAPTCHA if needed and load vehicles. A saved/connected session normally does not need another sign-in; PLX renews tokens automatically. Sign out deletes only this PLX Porsche session. Docker’s separate “Sign out of PLX” ends only the web session.

## Setup

Choose vehicles near the top and **save**. Seeing a discovered car does not mean it has been selected. The technical alias is used in MQTT topics and accepts lowercase letters, digits, `_` and `-`, up to 32 characters, starting with a letter.

Automatic polling and MQTT are independent switches. The suggested polling interval is 15 minutes; manual refresh is limited to once in five minutes. “Maximum vehicle data age” controls validity indicators, not how often the vehicle reports data. A sleeping vehicle can return old measurements even after a new cloud request.

## Vehicle data

Search names, technical identifiers and values. Filters show available, current, stale, unavailable or MQTT-selected parameters. A missing value is not automatically unsupported hardware: vehicle equipment, contract, account permissions, cloud response and timestamps can all affect availability. An empty history can simply mean no entries.

The interface keeps all parameters visible regardless of your MQTT selection. Each group has its own measurement age/availability.

## MQTT and Loxone

Configure the **actual MQTT broker**, not a hostname that only serves the HTTPS web UI. A web reverse proxy can resolve successfully while refusing TCP/1883; HTTPS/443 proves no MQTT reachability. Use the broker listener's port/TLS setting (commonly 1883 plain or 8883 TLS, but match its configuration). A container's `127.0.0.1` is not another host's broker.

After saving the broker address, run this from the **same Compose directory and project** (replace `-p plx` with an existing installation's actual project). It reads only host/port/TLS, never prints credentials and does not publish or subscribe:

```sh
docker compose -p plx exec -T plx python - <<'PYTHON'
import json, socket, ssl
c = json.load(open('/data/config/settings.json'))['mqtt']
host, port = c['host'], c['port']
print('Broker:', host, 'Port:', port)
print('Resolved:', sorted({a[4][0] for a in socket.getaddrinfo(host, port, type=socket.SOCK_STREAM)}))
with socket.create_connection((host, port), timeout=5) as connection:
    if c.get('tls'):
        with ssl.create_default_context().wrap_socket(connection, server_hostname=host):
            print('TCP and verified TLS connected')
    else:
        print('TCP connected; TLS is disabled in PLX')
PYTHON
```

TCP/TLS success proves reachability, **not** MQTT credentials or publish ACLs. A refused connection usually needs address/listener/firewall investigation before password changes. Do not weaken TLS certificate checks. Under Portainer, use its PLX container console to perform the equivalent check.

Then choose values under Loxone and save. For the default prefix the entire subscription is:

```text
porsche2lox/#
```

For a custom prefix use `<prefix>/#`. That subscription receives all matching messages; it does not cause PLX to send all parameters. Saved selections and simple/detailed format determine publication.

**Simple output (new-install default):** one topic per selected value. Tire pressure uses the actual pressure as a number in bar, not the pressure difference. Missing data is JSON `null`; a genuine numeric zero stays zero. Other structured parameters use one JSON topic per selection. Two selected pressures mean exactly two topics.

Simple mode sends the last reported value, even if its age is unknown or too high. It has no heartbeat, availability or age topics. Retained values can remain after disconnection or shutdown. For freshness-dependent automation, use detailed output and evaluate its validity/availability signals.

**Detailed output:** optional under Advanced output options. It adds diagnostics, availability, timestamps and detailed fields. Existing installations without an explicit format keep this behavior. Switching modes or deselecting values cleans up previously selected topics once; this is different from a recurring deletion series.

The XML/CSV mapping is optional. XML targets numeric virtual UDP inputs via an MQTT Gateway; CSV also describes nonnumeric fields. Choose the UDP port that the Gateway sends to on the Miniserver (export default 11883) and optional **UDP sender IP**. That means the MQTT Gateway host as seen by the Miniserver, not automatically the Docker host, broker, LoxBerry or Miniserver. Leave the filter empty if unsure; a wrong filter can discard every value. The broker TCP port and UDP bridge port are different settings. Importing XML does not prove that the Gateway/Miniserver chain works; test that chain locally. See [Loxone mapping](LOXONE.md).

## Common questions

| Symptom | Check |
| --- | --- |
| Signed in but no overview values | Select a vehicle in Setup and save, then refresh status. |
| Broker unreachable | Check container DNS/TCP above. A web-proxy hostname may be wrong for MQTT; TCP refused is not proof of a bad password. Match broker port/TLS, then test MQTT authorization. |
| Unexpectedly many topics | Check simple/detailed format and the saved selection. Historical monitor rows are not necessarily current retained topics. |
| Old data after refresh | Compare measurement age with cloud-fetch time; PLX does not wake the car. |
| More/fewer parameters than another car | Equipment, contract and Porsche response differ. Do not treat unavailable as numeric zero. |
| Image pull denied | Use public release `ghcr.io/square-com-de/plx:0.1.0` or its pinned digest; verify spelling, network and Docker registry configuration. No token is needed. |
| HTTPS address rejected by LoxBerry | 0.1.0 does not recognize frontend TLS with an HTTP backend. Use direct LoxBerry HTTPS; do not disable the guard. [Known limitation](../INSTALL.md#loxberry-plugin). |
| Sign-in unavailable after restart | Sign in to the PLX web interface again; the saved Porsche session is separate. |

Runtime support, including the unqualified Podman/rootless path: [installation matrix](../INSTALL.md#runtime-status). No Stable acceptance is claimed; see [lessons and gate](INSTALLATION-LESSONS.md).

## Backup and support

Follow the [update/backup guide](../INSTALL.md#updates-backup-and-rollback). Protect the complete data volume/plugin data and credentials; they can contain Porsche tokens, location/trip data and TLS keys. Send only sanitized screenshots/logs in [GitHub feedback](https://github.com/square-com-de/plx/issues/new?template=feedback_question.md). See [security reporting](../SECURITY.md) for vulnerabilities.
