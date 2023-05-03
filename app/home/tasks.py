import ipaddress
import httpx
import json
import logging
import socket
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from celery import shared_task
from django.conf import settings
from django.core import management
from django.core.cache import cache
from django.core.cache.utils import make_template_fragment_key
from django.template.loader import render_to_string
from .models import SpeedTest, Webhooks


logger = logging.getLogger('celery')


@shared_task()
def clear_sessions():
    # Cleanup session data for supported backends
    return management.call_command('clearsessions')


@shared_task(autoretry_for=(Exception,), retry_kwargs={'max_retries': 3, 'countdown': 10}, rate_limit='2/m')
def flush_template_cache():
    # Flush template cache on request
    logger.info('flush_template_cache')
    return cache.delete_many(cache.keys('*.cache.*'))


@shared_task()
def clear_home_cache():
    # Clear Home Results cache on model update
    logger.info('clear_home_cache')
    key = make_template_fragment_key('home_body')
    return cache.delete(key)


@shared_task()
def delete_empty_results():
    logger.info('delete_empty_results')
    data = SpeedTest.objects.all()
    for q in data:
        if not q.ip:
            logger.info('Deleted result #%s', q.id)
            q.delete()


@shared_task(autoretry_for=(Exception,), retry_kwargs={'max_retries': 5, 'countdown': 60}, rate_limit='10/m')
def delete_discord_webhook(hook_url):
    try:
        r = httpx.delete(hook_url, timeout=30)
        if not r.is_success or r.status_code == 404:
            logger.warning(r.content.decode(r.encoding))
            r.raise_for_status()

        return r.status_code

    except Exception as error:
        logger.exception(error)
        raise


@shared_task(autoretry_for=(Exception,), retry_kwargs={'max_retries': 5, 'countdown': 60}, rate_limit='10/m')
def send_discord(hook_pk, message):
    try:
        hook = Webhooks.objects.get(pk=hook_pk)
        body = {'content': message}
        r = httpx.post(hook.url, json=body, timeout=30)
        if r.status_code == 404:
            logger.warning('Hook %s removed by owner %s', hook.hook_id, hook.owner.username)
            hook.delete()
            return 404

        if not r.is_success:
            logger.warning(r.content.decode(r.encoding))
            r.raise_for_status()

        return r.status_code

    except Exception as error:
        logger.exception(error)
        raise


@shared_task(autoretry_for=(Exception,), retry_kwargs={'max_retries': 5, 'countdown': 60}, rate_limit='10/m')
def send_success_message(hook_pk):
    logger.info('send_success_message: %s', hook_pk)
    # hook = Webhooks.objects.get(pk=hook_pk)
    context = {'site_url': settings.SITE_URL}
    message = render_to_string('discord/welcome.html', context)
    send_discord.delay(hook_pk, message)


@shared_task(autoretry_for=(Exception,), retry_kwargs={'max_retries': 3, 'countdown': 60})
def process_webhooks(pk):
    context = {'data': SpeedTest.objects.get(pk=pk)}
    message = render_to_string('discord/message.html', context)
    hooks = Webhooks.objects.all()
    if not hooks:
        logger.info('No hooks found, nothing to do.')
        return

    for hook in hooks:
        if not hook.active:
            continue
        logger.info('Sending alert to: %s', hook.id)
        send_discord.delay(hook.id, message)


@shared_task()
def process_data(pk):
    logger.info('process_data')
    q = SpeedTest.objects.get(pk=pk)

    # Make sure we have valid json, and it has an IP address
    try:
        data = json.loads(q.json)
        ip = data['start']['accepted_connection']['host']
        if not ip:
            logger.warning('NO IP IN DATA, DELETING: %s', ip)
            q.delete()
            return

    except Exception as error:
        logger.info(error)
        q.delete()
        return

    # Get IP hostname, and geolocation
    ip_info = {
        'ip': ip,
        'name': socket.getfqdn(ip),
        'geo': ip_addr_geo(ip),
    }

    # Parse the data and assign to model values
    q.ip = ip_info['ip']
    q.name = ip_info['name']
    bps = data['end']['sum_received']['bits_per_second'] or \
          data['end']['sum_sent']['bits_per_second']
    q.bps = bps
    q.bps_human = format_bps(bps)
    q.bytes = data['start']['test_start']['bytes']
    q.bytes_human = format_bytes(data['start']['test_start']['bytes'])
    q.reverse = data['start']['test_start']['reverse']
    q.duration = data['start']['test_start']['duration']
    q.protocol = data['start']['test_start']['protocol']
    if data['start']['test_start']['protocol'] == 'UDP':
        q.jitter = data['end']['sum']['jitter_ms']
        q.packets = data['end']['sum']['packets']
        q.lost = data['end']['sum']['lost_packets']
    if ip_info['geo']:
        q.ip_cc = ip_info['geo']['country_code']
        q.ip_country = ip_info['geo']['country_name']
        q.ip_rc = ip_info['geo']['region_code']
        q.ip_region = ip_info['geo']['region']
        q.ip_city = ip_info['geo']['city']
        q.ip_org = ip_info['geo']['org']
        q.ip_lat = ip_info['geo']['latitude']
        q.ip_lon = ip_info['geo']['longitude']
    q.version = data['start']['version']
    q.save()

    # Invalidate the results cache - SEE home/signals.py
    # key = make_template_fragment_key('home_body')
    # cache.delete(key)

    # Queue discord message task
    # send_discord_message.delay(pk)
    process_webhooks.delay(pk)

    # Update websocket with data
    #
    # socket_dict = {
    #     'id': q.id,
    #     'reverse': q.reverse,
    #     'ip': q.ip,
    #     'name': q.name,
    #     'bps_human': q.bps_human,
    #     'protocol': q.protocol,
    #     'created_at': q.created_at,
    # }
    #
    socket_dict = {'pk': q.pk}
    channel_layer = get_channel_layer()
    group_name = 'home_group'
    event = {
        'type': 'websocket.send',
        'text': json.dumps(socket_dict),
    }
    async_to_sync(channel_layer.group_send)(group_name, event)
    return


def format_bytes(size):
    # Convert bytes to human-readable size
    units = ['B', 'KB', 'MB', 'GB', 'TB']
    for unit in units:
        if size < 1024:
            return f'{size:.2f} {unit}'
        size /= 1024
    return f'{size:.2f} {units[-1]}'


def format_bps(bps):
    # Convert bits per second to human-readable size
    units = ['bps', 'Kbps', 'Mbps', 'Gbps', 'Tbps']
    for unit in units:
        if bps < 1000:
            return f'{bps:.2f} {unit}'
        bps /= 1000
    return f'{bps:.2f} {units[-1]}'


def ip_addr_geo(ip):
    # Get ipapi.co data for given IP Address
    if ipaddress.ip_address(ip).is_private:
        logger.info('is_private: %s', ip)
        return None
    url = f'https://ipapi.co/{ip}/json/'
    r = httpx.get(url)
    if 'error' in r.json():
        logger.info(r)
        return None
    return r.json()
