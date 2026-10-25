# PLX 0.1.2 Preview

This separate Preview contains the reviewed LoxBerry HTTPS-proxy fix. Public0.1.1 tags, images and assets remain unchanged. No Stable/latest or production promotion follows from this release.

## Change

LoxBerry supports HTTPS termination at an explicitly trusted proxy with an HTTP backend. Set the immediate peer IPs in private `trusted-proxies.json`; the proxy must overwrite `X-Forwarded-Proto` with the actual frontend scheme. Unknown peers, comma-separated chains and frontend HTTP are rejected. Direct HTTPS continues working. The plugin rotates pre-fix/plain-HTTP PHP sessions once into Secure/HttpOnly/Strict cookies; the separate Porsche session is preserved. HTTP pages block credential-bearing forms before values are read.

## Existing evidence

[PR6](https://github.com/square-com-de/plx/pull/6) was independently reviewed at `c102158b0e5c93bd3e998cc1cb0f5e57aaed002d` and merged as `052e125453d5936ee0a7a14dc4ff910f51ec5bca`. Its separate LoxBerry test-VM candidate passed19 transport/5 config cases,8 real proxy/backend cases, auth/CSRF and scoped browser checks. Source CI passed130 tests with1 platform skip. [Details and limitations](REVERSE-PROXY.md).

This evidence covers the proxy-fix candidate on a0.1.1 base, not the final0.1.2 distribution/image. The new version changes metadata/packaging; exact artifacts still require acceptance. Browser evidence used a route adapter with verified upstream CA/IP, not native browser certificate validation. No Porsche cloud login, real MQTT publish, physical Miniserver or production/Taycan deployment was performed.

## Published-artifact acceptance

The independently reviewed source above is now released as a separate 0.1.2 Preview. Release, Git tag and image absence were checked before publication; final CI passed. All public downloads and checksums were verified. The exact Docker image/Compose and official LoxBerry ZIP passed the scoped acceptance on separate test systems, including the real LoxBerry HTTPS-proxy path and Docker restart/recreation/cold restore.

[Exact artifact identities, test results and limits](QUICKSTART-0.1.2.md) · [Sanitized evidence](evidence/2026-10-25-public-0.1.2.json). The preceding PR6 candidate evidence is historical; the linked report covers the actual public 0.1.2 distribution.

Podman/rootless, real ARM64 execution, physical Miniserver and production proxy qualification remain separate. A multiarch manifest is not a real ARM64 runtime test. Existing0.1.1 backups and immutable downloads remain usable.
