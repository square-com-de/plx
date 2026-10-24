# PLX 0.1.1 Preview — published quickstart acceptance

The **new** one-file Docker start was accepted on 24–25 October 2026. This is separate from the historical [0.1.0 procedure](PROXMOX-CONTAINER.md), which needed a host secret and certificate provisioning. 0.1.0 archives are unchanged.

## Exact public artifacts

- [Compose download](https://github.com/square-com-de/plx/releases/download/v0.1.1/compose.yaml), SHA256 `5c11b912cfdb3999142724eb133b92b48806d9a75e7fdc085b2c617d34ef6587`.
- Image `ghcr.io/square-com-de/plx@sha256:5ba106f4c3de9e90b19e4772a5df217ba87d65a86b2a99e8c7343ada1254dfd8`.
- Reviewed runtime source `46c2208de1f280245f3d405e9363f63d18393472`.
- [Release CI](https://github.com/square-com-de/plx/actions/runs/40136887049) passed; public manifest and checksums verified before deployment. No registry login was required.
- Runtime: dedicated Proxmox Linux test VM, Ubuntu26.04.1 AMD64, Docker29.9.2, Compose5.6.1. The OS was initially provisioned clean for acceptance; the new quickstart reused that isolated lab host with a **fresh PLX volume**, not a second freshly installed OS.

## Standard commands that were exercised

Run in an administrator shell with Docker access, once in a new directory. Replace `192.0.2.10` with the Docker server's real IPv4 address or resolvable DNS name; no scheme or port. DNS/mDNS must already work for the client. Simple mode is the usable default, without a mode-selection wizard.

```sh
set -eu
mkdir plx && cd plx
curl -fLO https://github.com/square-com-de/plx/releases/download/v0.1.1/compose.yaml
printf 'PLX_HOST=192.0.2.10\n' > .env
docker compose up -d --wait --wait-timeout 90
docker compose exec -T plx cat /data/config/web-password.txt
```

Open `https://<your-server>:8443`, username `admin`, password from the last console command. The only required first-start setting is `PLX_HOST`. Password, TLS and settings are created in the named volume. No host secret file, manual ownership change or manual certificate generation was used. Keep the generated password private; it is not emitted in startup logs.

**TLS trust is explicit:** the generated certificate matches the configured server, but private-LAN self-signed certificates are not automatically publicly trusted. Verify the fingerprint from your own server console and trust that certificate, or provide an appropriate trusted certificate. Do not disable certificate validation. The browser test used an isolated temporary NSS database with explicit trust for the generated server certificate, without `ignoreHTTPSErrors` or certificate-ignore flags. A separate Mac LAN client also checked CA trust and IP SAN before login.

The executed lab used the same downloaded file byte-for-byte. Its `.env` additionally selected an assigned test port and existing owned Compose project name to reuse the lab's narrow firewall exception; those are **test-environment differences**, not hidden user prerequisites. A preexisting disposable prototype volume was privately backed up and removed before the public-artifact run; its working restored volume and older test instance remained preserved. The application task did not change firewall rules or contact production endpoints.

## Passed checks and limits

- Fresh volume: healthy non-root startup, random stable password, password/private-key modes0600; no predefined secret or credential logging.
- Real Chrome156 LAN browser login, login-page DE/EN, authenticated UI DE/EN, Secure/HttpOnly/SameSiteStrict cookie, save/reload, draft retention, mobile390px without horizontal overflow and no JavaScript errors.
- Automatic polling and MQTT disabled, no vehicles/session imported; Simple MQTT default.
- Restart, forced recreation and **same-image, matching-state cold restore into a different owned volume** retained settings, password and TLS bytes. Persisted Compose override kept the restored volume on subsequent bare `up`. Browser login passed again after restore.
- Isolated protocol mock received exactly two selected simulated pressure values; a separate missing-value case received two `null` values. QoS1/retain passed, zero extra topics or deletion messages. This is not a production broker ACL/TLS or live vehicle test.
- Rendered DE/EN data-age hints matched Simple versus detailed MQTT semantics; original Simple setting restored.
- New public image accepted a network-isolated clone of old settings/TLS with the existing external secret and did not generate a replacement password. Existing old instance was untouched; this is not schema downgrade qualification.
- A coordinated VM reboot **before the published-artifact run**, on the pre-release prototype, preserved container/image/volume and settings/password/TLS hashes; strict external TLS login and browser login passed again. Do not represent this as an additional cold reboot of the final public image; that image separately passed process restart/recreation/restore.

No Porsche login, live tokens, vehicle fetch, production MQTT publish or physical Miniserver operation was performed. Portainer uses the same Compose and console password retrieval, but its GUI was not independently operated in this run. Podman/rootless and real ARM64 execution remain unqualified. LoxBerry HTTP-backend TLS termination remains a separate open gate. No Stable/`latest` promotion or production deployment follows from this acceptance.

## Separate LoxBerry ZIP acceptance

The [dedicated PLX-LoxBerry-0.1.1.zip](https://github.com/square-com-de/plx/releases/download/v0.1.1/PLX-LoxBerry-0.1.1.zip), SHA256 `a9f56c92743dcbc630890ff8be39d3caa5462111c91b0ae438694e34587189b5`, passed official clean import and 0.1.0→0.1.1 update on a separate LoxBerry4.0.0.15 test VM (Debian13.7, Python3.13.5, PHP7.4.33). Settings, saved session bytes and two pressure selections survived update;17 installed runtime/UI files matched the exact public ZIP. This does not authenticate the retained Porsche session.

Direct HTTPS PHP/API checks verified the pinned CA,401 authentication and403 CSRF behavior. Clean install starts signed out with Simple mode, polling and MQTT disabled. Rendered DE/EN Simple/detailed age hints, harmless save/restoration and390px layout passed. **This LoxBerry browser check used a local loopback proxy with verified direct HTTPS upstream; the browser itself did not validate the test-VM certificate.** Keep this distinction from the Docker native browser TLS acceptance above.

The full original test-plugin state, private data, service unit and registration were restored afterwards, including25 original code/UI file comparisons; other running units stayed unchanged. Public PHP is byte-identical to0.1.0: the HTTP-backend TLS-terminating proxy issue remains unqualified. No Porsche login/cloud fetch or MQTT was activated. [LoxBerry evidence](evidence/2026-10-25-loxberry-0.1.1.json).

[Machine-readable evidence](evidence/2026-10-25-quickstart.json) · [Installation](../INSTALL.md) · [Deutsch](../INSTALL.de.md) · [Remaining gates](https://github.com/square-com-de/plx/issues/1)
