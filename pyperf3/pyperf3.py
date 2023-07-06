import json
import httpx
import os
import subprocess
import sys
import time


def run(cmd):
    return subprocess.check_output(
        cmd.split(),
        stderr=subprocess.STDOUT,
        universal_newlines=True,
    )


if __name__ == '__main__':
    port = os.environ.get('IPERF_PORT', '5201')
    print(f'Starting PyPerf3 Server on port: {port}\n')
    url = 'http://nginx/save/'
    counter = 0
    while True:
        try:
            counter += 1
            print(f'\nWaiting for test #{str(counter).zfill(3)}...\n')
            r = run(f'iperf3 -p {port} -s -J -1')
            d = json.loads(r)
            r = httpx.post(url=url, json=json.dumps(d), timeout=3)
            print(r.status_code)
        except (KeyboardInterrupt, SystemExit):
            print('\nCaught exit signal, shutting down...')
            sys.exit(0)
        except Exception as error:
            print('\nCaught Exception in __main__:')
            print(error)
            time.sleep(2)
            continue
