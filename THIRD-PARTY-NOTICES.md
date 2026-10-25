# Dependencies

PLX installs unmodified, pinned Python wheels from PyPI. It does not vendor upstream Python source code into the plugin ZIP. Installed wheels contain their respective license metadata.

- pyporscheconnectapi 0.2.9: package metadata and LICENSE identify MIT; some source files carry Apache-2.0 SPDX identifiers. This discrepancy is recorded here and must be resolved before any future vendoring or redistribution of upstream source. https://github.com/CJNE/pyporscheconnectapi/tree/0.2.9
- paho-mqtt 2.1.0: EPL-2.0 OR BSD-3-Clause. https://github.com/eclipse-paho/paho.mqtt.python
- Other transitive dependencies and exact hashes: bin/requirements.lock.txt.

The LoxBerry V4 sample was used to understand the plugin interface and directory layout. PLX hooks and frontend were written for this integration; the sample's demonstration files are not bundled. https://github.com/mschlenstedt/LoxBerry-Plugin-SamplePlugin-V4

Porsche and Loxone are trademarks of their respective owners. This integration is independent and unsupported by Porsche. No proprietary Porsche font is bundled.

## PLX artwork

From 0.1.3 the project icon uses the user-selected original PLX artwork: abstract silver vehicle line, dark smart-home circuit motif and red X. The original PNG is retained byte-for-byte in `icons/plx-logo-original.png`; SVG delivery wrappers embed that same PNG. Provenance and checksums are in `icons/provenance.json`. It replaces the former Porsche crest app icon. The icon is project artwork, not a Porsche badge or endorsement. Historical versions and Git history may retain prior artwork until separately withdrawn; no history rewrite is performed by this change.

## Release preparation and vehicle illustrations

PLX’s own source code is licensed under MIT; see LICENSE. Third-party dependencies and Porsche branding are excluded from that grant and retain their respective terms. The MIT license grants no trademark rights or ownership of Porsche artwork. Attribution does not extend the original rights. Vehicle images in the running app are fetched from the signed-in account; private runtime image-cache files are not bundled. The public preview fixture `docs/preview/model.png` and regenerated dashboard screenshots contain a Porsche Connect model illustration alongside simulated measurements. Porsche retains the rights to that model artwork; the illustration and its appearance in screenshots are not covered by the PLX MIT grant. It is distinct from the new PLX project icon. Docker images install dependency wheels; retain their bundled license metadata.
