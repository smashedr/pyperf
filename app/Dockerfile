FROM python:3.11-slim

ENV TZ=UTC
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV DEBIAN_FRONTEND=noninteractive

RUN groupadd -g 1000 app  &&\
    useradd -r -d /app -M -u 1000 -g 1000 -G video -s /usr/sbin/nologin app  &&\
    mkdir -p /app /data  &&  chown app:app /app /data  &&\
    apt-get -y update  &&  apt-get -y install gcc libmariadb-dev-compat pkg-config  &&\
    apt-get -y clean  &&  rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY --chown=app:app requirements.txt .
RUN python3 -m pip install --no-cache-dir --upgrade pip  &&\
    python3 -m pip install --no-cache-dir -r requirements.txt
COPY --chown=app:app . .
USER app
ENTRYPOINT ["bash", "docker-entrypoint.sh"]
