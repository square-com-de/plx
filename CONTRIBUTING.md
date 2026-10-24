# Contributing to PLX

Feedback, fixes and documentation improvements are welcome. Start with the [project page](README.md), [manual](docs/MANUAL.md) and [release limits](RELEASE.md). Use the [issue templates](https://github.com/square-com-de/plx/issues/new/choose) for a bug, idea or question.

Describe PLX version, Docker/LoxBerry environment, vehicle model and expected versus observed behavior. Do not post Porsche IDs, VINs, locations, passwords, tokens, real account responses or private backups. Report vulnerabilities through [SECURITY.md](SECURITY.md).

## Local development

Python 3.11+ is required. In the repository root:

```sh
python3 -m venv .venv
.venv/bin/pip install --require-hashes -r bin/requirements.lock.txt
.venv/bin/pip install pytest==8.4.2
.venv/bin/python -m pytest tests -q
.venv/bin/python tools/prepare_release.py
```

Some tests require Linux, PHP and Mosquitto; platform skips on macOS do not prove those paths. The [CI workflow](https://github.com/square-com-de/plx/actions/workflows/docker.yml) runs Linux tests and a real container smoke test. Browser checks in `tools/check-language.cjs` use simulated data, Playwright and Chrome; set `NODE_PATH` and `PYTHON` for your local runtime. That script never needs a real Porsche account or broker.

Keep the two distributions consistent while preserving their separate installation paths. LoxBerry upgrade hooks must retain configuration/session across the official installer’s purge step. Verify simple MQTT does not grow metadata or history topics implicitly. Keep German and English user-facing text aligned.

Use synthetic data in tests and public illustrations. Do not include your local settings, secrets, certificates, session files or private logs in commits or release archives. Existing production integrations are outside development/test scope.

By contributing, you agree that your original contribution may be distributed under the project’s [MIT license](LICENSE). Third-party code/assets require their own notices and compatible permission.
