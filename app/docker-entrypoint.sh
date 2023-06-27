#!/usr/bin/env bash

set -x

if echo "${*}" | grep -q "gunicorn";then
    if [ -n "${DJANGO_SUPERUSER_PASSWORD}" ] &&
    [ -n "${DJANGO_SUPERUSER_USERNAME}" ] &&
    [ -n "${DJANGO_SUPERUSER_EMAIL}" ];then
        python manage.py createsuperuser --noinput
    fi
    set -e
    python manage.py collectstatic --noinput
fi

set -e

exec "$@"
