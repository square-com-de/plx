FROM python:3.13-slim-bookworm
LABEL org.opencontainers.image.title="PLX" \
      org.opencontainers.image.description="Independent Porsche Connect status dashboard and MQTT integration" \
      org.opencontainers.image.source="https://github.com/square-com-de/plx"
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PYTHONPATH=/app/bin
RUN apt-get update && apt-get install -y --no-install-recommends openssl ca-certificates \
    && rm -rf /var/lib/apt/lists/* \
    && groupadd --gid 10001 plx && useradd --uid 10001 --gid plx --no-create-home plx \
    && mkdir -p /data && chown plx:plx /data
WORKDIR /app
COPY bin/requirements.lock.txt /tmp/requirements.lock.txt
RUN pip install --no-cache-dir --require-hashes -r /tmp/requirements.lock.txt \
    && rm /tmp/requirements.lock.txt
COPY bin/porsche2lox /app/bin/porsche2lox
COPY templates/dashboard.html /app/templates/dashboard.html
COPY webfrontend/htmlauth/app.css webfrontend/htmlauth/app.js webfrontend/htmlauth/logo.svg /app/webfrontend/htmlauth/
COPY docker/healthcheck.py /app/healthcheck.py
COPY LICENSE THIRD-PARTY-NOTICES.md /app/
USER 10001:10001
VOLUME ["/data"]
EXPOSE 8443
HEALTHCHECK --interval=30s --timeout=5s --start-period=30s --retries=3 CMD ["python", "/app/healthcheck.py"]
STOPSIGNAL SIGTERM
ENTRYPOINT ["python", "-m", "porsche2lox.standalone"]
