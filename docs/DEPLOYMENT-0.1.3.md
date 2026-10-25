# PLX 0.1.3 Preview — fresh Portainer deployment acceptance

Executed on 25 October 2026. This records a real fresh installation of the already published image, not a new release or a claim that every installation path has been tested. Deployment addresses, account identifiers and private evidence are omitted.

## Artifact and environment

- Image: `ghcr.io/square-com-de/plx@sha256:e5fbe30974c6e8ac4510438a6d47e38756225e10d3133ec511e029de4ae66542`.
- Existing Linux/AMD64 Docker host, managed through Portainer's standalone-stack API.
- Separate fresh stack and persistent named volume; no old password, TLS files, settings or Porsche session imported.
- The public release Compose configuration was adapted for the site's hostname, host binding/port, container name and explicit persistent volume name. This was not an execution of the README's CLI commands verbatim. Those commands retain their [earlier quickstart evidence](QUICKSTART-0.1.2.md).
- Existing services and container data were outside the deployment scope.

## Passed checks

1. Confirmed target stack/container/volume names and backend port were unused. Verified the intended image digest, source metadata and Compose definition.
2. Created the separate stack through Portainer. First start generated the private web password and host-matched TLS certificate in the new data volume.
3. Verified native backend TLS with the expected DNS identity and certificate trust, then a real PLX admin login, authenticated UI showing 0.1.3 and Secure/HttpOnly/SameSite cookies.
4. Made a private cold archive, verified it was readable, performed a controlled stop/start, logged in again and checked saved file bytes remained unchanged. The archive was not restored into production; this record does not claim an independently verified restore test.
5. Applied the requested container-name change through Portainer's supported existing-stack update. The container was recreated; the volume, web password and TLS identity were retained. Read back the stored stack definition and new container identity.
6. Activated the site's HTTPS reverse-proxy route with verified backend TLS/DNS identity, preserved Host, and a backend access rule limited to the immediate proxy. Certificate verification stayed enabled. Direct access from another LAN client to the restricted backend timed out as intended.
7. Verified the public HTTPS frontend: unauthenticated login page, actual admin login, authenticated UI, read-only status API, rejection of invalid CSRF and foreign Origin. A browser independently displayed the login page without a certificate-warning bypass; no authenticated browser-dashboard walkthrough is claimed.
8. Confirmed the fresh state contained no vehicles; automatic polling and MQTT remained disabled. Password storage was verified privately, without exporting its value into chat, source files or local screenshots.
9. Revoked the temporary Portainer setup key, confirmed it subsequently received HTTP 401, and removed its temporary host file. The PLX web password remained intact.
10. Compared neighboring container identities, images and start times across the app checks. Their services remained available; no unrelated application data was migrated or changed by the PLX deployment.

## Observed deployment issues and recovery

Portainer returned before its asynchronous container deployment had finished. The first verification attempted to inspect a container that did not exist yet. A later inspection found the intended container healthy; it was deliberately stopped while the verification helper was corrected. A second early inspection exposed a case-sensitive Docker error-message matcher. The matcher was corrected to recognize only the exact missing-container errors, case-insensitively, with bounded polling. Other Docker errors still fail the check.

No second stack or replacement volume was created to recover from those verification failures. The existing stack was retained, the API update and stored definition were read back, and the completed login/restart/frontend checks above were performed on the resulting installation. A stopped container with exit code 0 during that sequence was a controlled stop, not proof of an application crash.

## Scope and remaining work

This qualifies the recorded AMD64 Portainer deployment and HTTPS topology only. It does not make 0.1.3 Stable, qualify real ARM64/Podman/rootless/native installation, or replace [public-artifact acceptance](QUICKSTART-0.1.3.md).

No Porsche account login, CAPTCHA, live token refresh, vehicle fetch, vehicle command or MQTT publish was executed as part of this fresh-install acceptance. The owner must complete Porsche setup and deliberately enable polling/MQTT. A complete production MQTT Gateway → Loxone Miniserver chain remains a separate gate.

[Installation](../INSTALL.md) · [Release status](../RELEASE.md) · [Manual](MANUAL.md) · [Installation lessons](INSTALLATION-LESSONS.md)
