FROM python:3.11-alpine

ENV TZ=UTC
ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1

RUN addgroup -g 1000 app && \
    adduser -S -H -h /app -s /sbin/nologin -u 1000 -G app app && \
    apk add --no-cache iperf3

WORKDIR /app
COPY --chown=app:app requirements.txt .
RUN python3 -m pip install --no-cache-dir --upgrade pip && \
    python3 -m pip install --no-cache-dir -r requirements.txt

COPY --chown=app:app . .
USER app
ENTRYPOINT ["python3", "pyperf3.py"]
