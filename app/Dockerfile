FROM python:3.11-slim

ENV TZ=UTC
ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1

RUN groupadd -g 1000 app && \
    useradd -r -d /app -M -u 1000 -g 1000 -G video -s /usr/sbin/nologin app && \
    mkdir -p /app /data && chown app:app /app /data && \
    apt -y update && apt -y install gcc libmariadb-dev-compat

#RUN addgroup -g 1000 app && \
#    adduser -S -H -h /app -s /sbin/nologin -u 1000 -G app app && \
#    mkdir -p /app /data && chown app:app /app /data && \
#    apk add --update --no-cache alpine-sdk mysql-dev

WORKDIR /app
COPY --chown=app:app requirements.txt .
RUN python3 -m pip install --no-cache-dir --upgrade pip && \
    python3 -m pip install --no-cache-dir -r requirements.txt
COPY --chown=app:app . .
USER app
ENTRYPOINT ["bash", "docker-entrypoint.sh"]
