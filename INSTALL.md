# Install PLX

[Deutsch](INSTALL.de.md) · [Project page](README.md)

**0.1.0 Preview:** download `PLX-Docker-0.1.0.tar.gz`, `PLX-LoxBerry-0.1.0.zip` and `SHA256SUMS` from the [versioned release](https://github.com/square-com-de/plx/releases/tag/v0.1.0). The Docker image is public; no GitHub account or registry token is required to pull it. This is a preview, not a stable release.

## Docker / Compose

Requires Docker Engine with Compose v2 on AMD64 or ARM64, a compatible Porsche Connect account and internet access. An MQTT broker is needed only for MQTT output. Mac/Windows can be used to manage your server.

1. Extract the Docker bundle into its own directory. Its `compose.yaml` pins the reviewed image digest. Verify `SHA256SUMS` after extraction; verify the archive itself against the release checksums before extraction.
2. Create your own PLX password:

   ```sh
   mkdir -p secrets
   openssl rand -base64 32 > secrets/plx_password.txt
   chmod 600 secrets/plx_password.txt
   # Linux bind-mounted secret must be readable by container group 10001:
   # sudo chgrp 10001 secrets/plx_password.txt
   # chmod 640 secrets/plx_password.txt
   ```

3. No registry login is needed for the public release image.
4. Run `docker compose pull`, then `docker compose up -d`.
5. Open `https://localhost:8443`, username `admin`, password from your secret file. The generated certificate needs local trust or replacement with a suitable certificate. See [TLS and SAN requirements](docs/DOCKER.md#https-und-anmeldung).

The default bind address is local-only. Set `PLX_BIND_ADDRESS` to your server’s LAN address when LAN access is required. `PLX_PORT` changes the host port; `PLX_USERNAME` changes the username. Do not mount a production Porsche/Taycan directory.

For Portainer, use the bundle’s Compose definition as a separate stack. The file-secret path must be available to that Portainer environment; paths refer to the deployment host, not your desktop. Preserve the named data volume when updating.

**Build from source instead:** from the repository root, create the same secret and run `docker compose up -d --build` using the repository’s build-enabled `compose.yaml`. The source repository is public.

## LoxBerry plugin

Requires LoxBerry 4, Debian 12 or newer, Python 3.11+, HTTPS and internet access during installation.

1. Download the release’s `PLX-LoxBerry-0.1.0.zip` and verify its checksum. Do not use GitHub’s generic source ZIP as the plugin package.
2. Open the LoxBerry plugin manager and install the ZIP.
3. Open PLX through the protected LoxBerry interface **over HTTPS**. The plugin uses your LoxBerry web credentials, not the Docker PLX password.
4. Keep the existing technical plugin ID `porsche2lox` when updating. The UI name is PLX; technical directories remain compatible.

## First setup

1. In **Porsche account**, sign in with your Porsche ID and complete CAPTCHA if requested.
2. Load vehicles, continue to Setup, select a vehicle and save.
3. Use **Refresh status** in Overview. Enable automatic polling separately if desired; 15 minutes is the suggested interval.
4. Enter the MQTT broker’s network address and credentials. In Docker, `127.0.0.1` means the container itself.
5. Under **Loxone**, select only the values you want and save. Then enable MQTT output in Setup. Subscribe to `<prefix>/#`, default `porsche2lox/#`.

No vehicle commands or wake requests are sent. See the [manual](docs/MANUAL.md) for simple versus detailed MQTT and data age.

## Updates and backup

Back up the PLX data and credentials before updating; backups contain private tokens and TLS keys.

- **Docker:** preserve the entire data volume and web-password secret. Change to the reviewed image digest/version, pull, then recreate only the PLX service. Do not use `docker compose down -v` when retaining data. PLX web sign-in is needed again after restart; the Porsche session persists.
- **LoxBerry:** install the newer plugin ZIP over the existing plugin. The preparation hook stops only its own service. The preupgrade hook saves private state before LoxBerry deletes the old directories; the new installation restores it and rebuilds its Python environment. Do not uninstall first when you want to keep data.
- **Rollback:** use the previous reviewed image or plugin package and your private backup. Do not assume an older version can read a future configuration format. Follow the volume/file ownership rules in the [technical reference](docs/TECHNICAL.de.md).

Changing the MQTT selection may delete previously selected retained topics once. Simple mode does not send periodic deletion bursts or extra heartbeat topics.
