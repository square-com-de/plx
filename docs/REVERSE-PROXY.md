# LoxBerry behind an HTTPS reverse proxy

This fix is an unreleased candidate until included in a new version; public0.1.1 does not contain it.

Direct HTTPS works without extra configuration. When TLS terminates at a reverse proxy and its backend connection uses HTTP, PLX needs an explicit trust setting. It never trusts a forwarded header from an arbitrary client.

Create `trusted-proxies.json` inside this plugin's LoxBerry config directory (normally `/opt/loxberry/config/plugins/porsche2lox/`), readable by the LoxBerry web process, with private file permissions:

```json
{"trusted_proxies":["192.0.2.10"]}
```

Replace the example with the **immediate proxy peer's actual IP address**, not a client address or a whole subnet. Only exact IPv4/IPv6 addresses are supported. PLX uses the peer address PHP receives as REMOTE_ADDR; it does not use X-Forwarded-For to choose a trusted peer. If a webserver real-IP module rewrites that address, preserve the actual proxy peer appropriately or use a verified HTTPS backend; do not solve this by trusting client addresses or subnets. When this trusted peer supplies the header, it describes the browser-facing scheme even if its backend uses TLS. A trusted `http` header therefore does not become HTTPS just because the backend is encrypted. Without a forwarded header, native direct TLS remains supported.

The proxy must replace incoming `X-Forwarded-Proto` with the actual frontend scheme (`https`); ambiguous comma-separated values are rejected. Restrict backend access to trusted LAN clients/proxies. Do not add untrusted peers to this list.

This setting recognizes TLS termination; it does not encrypt an HTTP backend hop. Prefer a verified HTTPS backend where available. Configuration is local to the installation and survives a plugin upgrade. It is not included in release ZIPs. Docker's own HTTPS listener is unaffected.

Plain HTTP pages block sign-in, CAPTCHA submission and saving in the browser before any request containing those values is sent. The PHP endpoint independently checks transport security. Open the normal HTTPS address to use these actions.

Existing pre-fix/plain-HTTP PHP sessions are rotated once on recognized HTTPS so the browser receives a new Secure/HttpOnly/SameSiteStrict cookie. This does not delete or replace the separately stored Porsche session.

## Separate test-VM acceptance

The unreleased candidate was installed through the official LoxBerry installer on the dedicated test VM. Its ZIP SHA256 is `e494b7fe12bcd7cc40d244a320f335016fcc599d057bf39ed67a5c6190b8899f`; runtime source is `7febab018154df0b031e82e89baaeb40b19bacd8`. This is not the public0.1.1 ZIP, which remains unchanged.

Passed:19 PHP transport cases and5 trust-file cases; a real HTTPS reverse proxy to an authenticated HTTP backend; unknown/missing/ambiguous/forged-header rejection; direct HTTPS; Secure cookie,401 authentication and403 CSRF; official-update preservation of private settings, Porsche session bytes and proxy trust configuration. Synthetic login/save/CAPTCHA dispatches reached a local Unix-socket stub while the real PLX service was stopped. No Porsche login/API or MQTT operation was performed.

The browser checked HTTPS relay, HTTP credential-field disabling and pre-submit blocking, DE/EN warnings,390px layout and no JavaScript errors. A browser route adapter sent requests through the real VM HTTPS proxy; the Node client verified its CA and expected IP identity. This is explicitly not native browser certificate validation or an acceptance of a production proxy. The small test proxy and stub were removed afterwards. The candidate remains installed, private session preserved and other running units unchanged; automatic polling and MQTT remain paused on the test VM.

Linux CI additionally exercises replacement of an old insecure PHP cookie by a new Secure/HttpOnly cookie and rejection of the old session. Existing Docker HTTPS startup and integration tests pass. [Machine-readable result](evidence/2026-10-25-https-proxy.json). Independent review/release remain separate from this test acceptance.
