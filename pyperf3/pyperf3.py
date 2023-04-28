import json
import httpx
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
    print('Starting PyPerf3 Server.\n')
    counter = 0
    while True:
        try:
            counter += 1
            print(f'\nWaiting for test #{str(counter).zfill(3)}...\n')
            r = run('iperf3 -s -J -1')
            d = json.loads(r)
            url = 'http://nginx/save/'
            r = httpx.post(url=url, json=json.dumps(d), timeout=3)
            print(r.status_code)
        except (KeyboardInterrupt, SystemExit):
            print('\nCaught exit signal, shutting down...')
            sys.exit(0)
        except Exception as error:
            print('\nCaught Exception in __main__:')
            print(error)
            time.sleep(3)
            continue
