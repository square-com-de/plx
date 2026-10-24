# PLX 0.1.1 Preview

Docker first start now needs only the server IP/DNS name (`PLX_HOST`). The standard Compose path is LAN-accessible; it automatically creates a private persistent web password and a host-matched self-signed certificate in the named data volume. No external secret-file ownership steps are needed. Existing explicit external secrets remain supported.

Read the first password in the Docker/Portainer console with `docker compose exec -T plx cat /data/config/web-password.txt`. It is never printed in startup logs or served over HTTP. Browser trust for a self-signed private-LAN certificate is still an explicit one-time step; no certificate-error bypass is enabled. Invalid hosts or mismatched existing certificates fail clearly before the service starts.

The existing Simple mode remains the default, without a first-start mode chooser. The data-age hint now distinguishes simple versus detailed MQTT correctly (issue #4). The sign-in language script uses a fresh CSP nonce. Status-only vehicle access is unchanged.

This remains a preview. No claim of physical Miniserver, Podman/ARM64 runtime or production acceptance. Immutable image/asset provenance is in the attached manifest; 0.1.0 artifacts are not replaced.
