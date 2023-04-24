import json
import httpx
import subprocess
import sys
import time
from decouple import config

DISCORD_WEBHOOK = config('DISCORD_WEBHOOK')


def run(cmd):
    return subprocess.check_output(
        cmd.split(),
        stderr=subprocess.STDOUT,
        universal_newlines=True,
    )


if __name__ == '__main__':
    print('Starting PyPerf3 Server.\n')
    print(f'Hook URL: {DISCORD_WEBHOOK[:-60]}')
    counter = 0
    while True:
        try:
            counter += 1
            print(f'\nWaiting for test #{str(counter).zfill(3)}...\n')
            r = run('iperf3 -s -J -1')
            d = json.loads(r)
            # msg = generate_jinja(format_result(d))
            # print(msg)
            # if DISCORD_WEBHOOK:
            #     send_discord(msg)
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
