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

Configure your broker in Setup, then select values under Loxone and save. One subscription, `<prefix>/#`, receives all messages PLX sends under that prefix.

**Simple output (new-install default):** one topic per selected value. Tire pressure uses the actual pressure as a number in bar, not the pressure difference. Missing data is JSON `null`; a genuine numeric zero stays zero. Other structured parameters use one JSON topic per selection. Two selected pressures mean exactly two topics.

Simple mode sends the last reported value, even if its age is unknown or too high. It has no heartbeat, availability or age topics. Retained values can remain after disconnection or shutdown. For freshness-dependent automation, use detailed output and evaluate its validity/availability signals.

**Detailed output:** optional under Advanced output options. It adds diagnostics, availability, timestamps and detailed fields. Existing installations without an explicit format keep this behavior. Switching modes or deselecting values cleans up previously selected topics once; this is different from a recurring deletion series.

The XML/CSV mapping is optional. XML targets numeric virtual UDP inputs via an MQTT Gateway; CSV also describes nonnumeric fields. Choose the gateway’s UDP port and optional source IP. Importing XML does not prove that the Gateway/Miniserver chain works; test that chain locally. See [Loxone mapping](LOXONE.md).

## Common questions

| Symptom | Check |
| --- | --- |
| Signed in but no overview values | Select a vehicle in Setup and save, then refresh status. |
| Broker unreachable | Use its network address, correct port and credentials; match TLS settings. `127.0.0.1` inside Docker is PLX itself. |
| Unexpectedly many topics | Check simple/detailed format and the saved selection. Historical monitor rows are not necessarily current retained topics. |
| Old data after refresh | Compare measurement age with cloud-fetch time; PLX does not wake the car. |
| More/fewer parameters than another car | Equipment, contract and Porsche response differ. Do not treat unavailable as numeric zero. |
| Image pull denied | Use public release `ghcr.io/square-com-de/plx:0.1.0` or its pinned digest; verify spelling, network and Docker registry configuration. No token is needed. |
| Sign-in unavailable after restart | Sign in to the PLX web interface again; the saved Porsche session is separate. |

## Backup and support

Follow the [update/backup guide](../INSTALL.md#updates-and-backup). Protect the complete data volume/plugin data and credentials; they can contain Porsche tokens, location/trip data and TLS keys. Send only sanitized screenshots/logs in [GitHub feedback](https://github.com/square-com-de/plx/issues/new?template=feedback_question.md). See [security reporting](../SECURITY.md) for vulnerabilities.
