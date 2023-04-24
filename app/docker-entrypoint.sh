#!/usr/bin/env bash

set -ex

if [[ $* == gun* ]];then
  python3 manage.py collectstatic --noinput
fi

exec "$@"
