FROM python:3.11-alpine
ENV PYTHONUNBUFFERED=1

RUN addgroup -g 1000 app && \
    adduser -S -H -h /app -s /sbin/nologin -u 1000 -G app app && \
    apk add --no-cache iperf3

WORKDIR /app

ADD --chown=app:app requirements.txt .
RUN python3 -m pip install -r requirements.txt --no-cache-dir
ADD --chown=app:app . .

USER app
ENTRYPOINT ["python3", "pyperf3.py"]
