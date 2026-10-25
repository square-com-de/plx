# PLX 0.1.2 Preview — public-artifact acceptance

Accepted on 25 October 2026 on separate Docker and LoxBerry test systems. No production or Taycan application was contacted or changed. This is Preview qualification, with the limits below.

## Exact distribution

- [Release](https://github.com/square-com-de/plx/releases/tag/v0.1.2), built by [release CI](https://github.com/square-com-de/plx/actions/runs/40171862451) from independently reviewed source `261ff1d32d20b17e725893c798b18666ef9fbb43`.
- [Compose](https://github.com/square-com-de/plx/releases/download/v0.1.2/compose.yaml): SHA256 `c9a3a2d2a011762f11442e7b1d16317545d8f8cf1af33274b6507720253ebc3c`.
- Image: `ghcr.io/square-com-de/plx@sha256:b0fadb6e2103315b07fc1ebe795486e3e3f4f94757257b6b3a682717afb8e827`.
- [LoxBerry installer ZIP](https://github.com/square-com-de/plx/releases/download/v0.1.2/PLX-LoxBerry-0.1.2.zip): SHA256 `2e657baee6aae211338c0a7ae9b4bb777f10e34aadf74479aada39c9ca5d3e71`.
- [Docker bundle](https://github.com/square-com-de/plx/releases/download/v0.1.2/PLX-Docker-0.1.2.tar.gz): SHA256 `76766fa1bc87cfb2b6f1142ccec6c9dd133ee19c59fed92b06431b88254e465a`.

All five assets were downloaded anonymously and checked against the public manifest/checksums. All 43 inner Docker checksums passed; bundled Compose equals the standalone download. Published assets and tag remain unchanged; this later documentation commit does not rebuild or replace them.

## Docker

Ubuntu 26.04.1 AMD64, Docker 29.9.2, Compose 5.6.1 on the isolated test host, with a fresh PLX volume. The host was originally provisioned clean; this run reused it rather than claiming a newly installed OS. The exact downloaded Compose was used unchanged. Test-only environment settings chose an assigned port and owned project name in addition to the required `PLX_HOST`.

The [standard installation commands](../INSTALL.md) passed without a host secret, manual chown or certificate creation. Generated password and TLS key were private mode 0600, stable across restart/recreation/restore and absent from startup logs. Simple MQTT is the default; polling/MQTT were disabled and Porsche signed out.

Chrome for Testing 156 opened the real LAN HTTPS URL with explicit certificate trust in an isolated NSS database and no certificate-ignore option. An external Mac client independently verified CA/IP SAN and login. DE/EN, Secure/HttpOnly/Strict cookies, harmless save/reload, draft retention, 390px layout and no JavaScript errors passed. Process restart, forced recreation and cold restore into a distinct owned volume preserved matching settings/password/TLS; browser and external HTTPS login passed again afterwards. The original volume remains preserved. No final-image VM cold reboot was performed: the older prototype reboot is historical evidence only.

An isolated MQTT protocol mock received exactly two selected simulated pressure values, and a separate missing-value case received two nulls: QoS1/retain, zero extra topics or deletion messages. This is not real vehicle data or production broker ACL/TLS qualification. Rendered Simple/detailed age hints passed in DE/EN. A network-isolated legacy settings/TLS clone with the old external secret started on the new public image without generating a replacement password; the existing legacy instance remained untouched. This is not schema downgrade testing.

## LoxBerry

The exact public ZIP passed official update and clean import on the separate LoxBerry 4.0.0.15 VM (Debian 13.7, Python 3.13.5, PHP 7.4.33). Update preserved settings, saved Porsche session bytes and trusted-proxy configuration. Clean import started signed out with Simple MQTT and polling/MQTT disabled. Original private test state was restored afterwards, with polling/MQTT paused; public 0.1.2 remains installed. Eighteen installed runtime/UI files match the public ZIP. Other running units were unchanged; temporary proxy/stub fixtures were removed.

Nineteen PHP transport and five configuration cases passed, plus eight real proxy/backend cases covering trusted HTTPS, untrusted/ambiguous/missing headers, forged frontend HTTP and direct HTTPS. A real test TLS proxy forwarded to the authenticated HTTP backend. Secure cookie, 401 authentication and 403 CSRF checks passed. Login/CAPTCHA/save dispatch used only a local stub with the real PLX service stopped during mutation tests, never Porsche. DE/EN, HTTP credential blocking, 390px layout and no JavaScript errors passed.

**LoxBerry browser TLS scope:** a browser route adapter used a Node client that verified upstream CA/IP. The browser itself did not validate that VM certificate. This differs from the native Docker browser TLS check. After fixture removal, the real service and direct HTTPS status API were checked again successfully. Retained session bytes do not prove live Porsche token validity. Production proxy configuration was not changed; follow [trusted proxy setup](REVERSE-PROXY.md).

## Remaining scope

No live Porsche login/token refresh/vehicle fetch, production MQTT publish, physical Miniserver, final-image VM cold reboot, Portainer GUI, Podman/rootless or real ARM64 execution was qualified in this run. Multiarch image build does not prove ARM64 runtime acceptance. No Stable/latest or production promotion.

[Sanitized machine-readable evidence](evidence/2026-10-25-public-0.1.2.json) · [Remaining gates](https://github.com/square-com-de/plx/issues/1) · [Historical 0.1.1 acceptance](QUICKSTART-0.1.1.md)
