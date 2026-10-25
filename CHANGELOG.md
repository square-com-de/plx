# Changelog

## 0.1.2 Preview — prepared, not published

- Recognize TLS termination only from explicitly configured immediate proxy IPs and one unambiguous X-Forwarded-Proto value.
- Upgrade pre-fix/plain-HTTP PHP sessions to a new Secure cookie on first recognized HTTPS request; retain CSRF protection.
- Block login, CAPTCHA and configuration submission in HTTP browser pages before sending credentials; direct HTTPS and Docker HTTPS stay supported.
- Local proxy trust config survives official plugin updates and is excluded from distributed ZIPs. See docs/REVERSE-PROXY.md.

## 0.1.1 Preview

- One Compose path with server host as the only required setting, LAN default, persistent generated password and matching TLS SAN.
- Early host/certificate errors, verified local health check and legacy external-secret compatibility.
- Correct data-age guidance for simple/detailed MQTT and nonce-protected login language switch.
- No first-start mode chooser, no vehicle commands, no production activation implied.

## 0.1.0 Preview — unreleased

- Standalone HTTPS Docker deployment for AMD64/ARM64 and LoxBerry 4 plugin.
- Independent Porsche session, account sign-in/CAPTCHA and token renewal.
- Vehicle selection, account-provided vehicle image, compact overview and searchable parameters.
- German/English interface with aligned header and subtle Porsche connection indicator.
- Simple MQTT: one selected value per topic; tire pressure as a number in bar, missing values as `null`.
- Optional detailed MQTT, Loxone XML and CSV mappings.
- Fixed LoxBerry upgrade data loss: stop the plugin service and preserve private state before the installer purges old directories.
- MIT license for original PLX code; third-party dependencies/branding retain their own terms.
- Bilingual project pages, installation/manual, feedback templates and release overview, using the public Hue2Lox documentation structure as a reference.

See [test evidence](docs/TESTS.md) and [release limits](RELEASE.md). This is not a publication announcement.
