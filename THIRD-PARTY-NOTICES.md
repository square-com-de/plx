# Dependencies

PLX installs unmodified, pinned Python wheels from PyPI. It does not vendor upstream Python source code into the plugin ZIP. Installed wheels contain their respective license metadata.

- pyporscheconnectapi 0.2.9: package metadata and LICENSE identify MIT; some source files carry Apache-2.0 SPDX identifiers. This discrepancy is recorded here and must be resolved before any future vendoring or redistribution of upstream source. https://github.com/CJNE/pyporscheconnectapi/tree/0.2.9
- paho-mqtt 2.1.0: EPL-2.0 OR BSD-3-Clause. https://github.com/eclipse-paho/paho.mqtt.python
- Other transitive dependencies and exact hashes: bin/requirements.lock.txt.

The LoxBerry V4 sample was used to understand the plugin interface and directory layout. PLX hooks and frontend were written for this integration; the sample's demonstration files are not bundled. https://github.com/mschlenstedt/LoxBerry-Plugin-SamplePlugin-V4

Porsche and Loxone are trademarks of their respective owners. This integration is independent and unsupported by Porsche. The surrounding app-icon artwork and earlier connection monogram were created for PLX. The current icon embeds the Porsche crest described below. No proprietary Porsche font is bundled.

The PLX app icon contains the Porsche crest as requested for this integration. Source: https://cdn.ui.porsche.com/porsche-design-system/crest/porsche-crest.19b4292@3x.webp (linked by https://www.porsche.com/germany/). Porsche crest and brand remain the property of Porsche. PLX is an independent project.

## Release preparation

PLX’s own source code is licensed under MIT; see LICENSE. Third-party dependencies and Porsche branding are excluded from that grant and retain their respective terms. The MIT license grants no trademark rights or ownership of Porsche artwork. Attribution does not extend the original rights. Vehicle images are fetched from the signed-in account; private image-cache files are not bundled. The public dashboard screenshot includes a Porsche Connect model illustration alongside simulated measurements. Porsche retains the rights to that model artwork; it is not covered by the PLX MIT grant. Docker images install dependency wheels; retain their bundled license metadata.
