FROM python:3.11
ENV TZ=UTC

RUN groupadd -g 1000 app && \
    useradd -r -d /app -M -u 1000 -g 1000 -G video -s /usr/sbin/nologin app

WORKDIR /app

ADD --chown=app:app requirements.txt .
RUN python3 -m pip install --no-cache-dir --upgrade pip && \
    python3 -m pip install --no-cache-dir -r requirements.txt

RUN mkdir -p /app /data && chown app:app /app /data
ADD --chown=app:app . .

USER app
ENTRYPOINT ["bash", "docker-entrypoint.sh"]
