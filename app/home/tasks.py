import ipaddress
import httpx
import json
import logging
import socket
from celery import shared_task
from channels.layers import get_channel_layer
from django.conf import settings
from django.core import management
from django.template.loader import render_to_string
from ipwhois import IPWhois
from .models import SpeedTest

from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

logger = logging.getLogger('celery')


@shared_task()
def clear_sessions():
    return management.call_command('clearsessions')


@shared_task()
def send_discord_message(pk):
    logger.info('send_discord_message')
    context = {'data': SpeedTest.objects.get(pk=pk)}
    message = render_to_string('discord/message.html', context)
    logger.info(message)
    data = {'content': message}
    r = httpx.post(settings.DISCORD_WEBHOOK, json=data, timeout=10)
    logger.info(r.status_code)
    if not r.is_success:
        logger.warning(r.content)
        r.raise_for_status()
    return r.status_code


@shared_task()
def process_data(pk):
    logger.info('process_data')
    q = SpeedTest.objects.get(pk=pk)
    data = json.loads(q.json)
    ip = data['start']['accepted_connection']['host']
    if not ip:
        logger.warning('NO IP IN DATA, DELETING: %s', ip)
        q.delete()
        return False

    ip_data = get_ip_data(ip)
    q.ip = ip_data['ip']
    q.name = ip_data['name']
    q.reverse = data['start']['test_start']['reverse']
    bps = data['end']['sum_received']['bits_per_second'] or \
          data['end']['sum_sent']['bits_per_second']
    q.bps = bps
    q.bps_human = format_bps(bps)
    q.bytes = data['start']['test_start']['bytes']
    q.bytes_human = format_bytes(data['start']['test_start']['bytes'])
    q.duration = data['start']['test_start']['duration']
    q.protocol = data['start']['test_start']['protocol']
    if data['start']['test_start']['protocol'] == 'UDP':
        q.jitter = data['end']['sum']['jitter_ms']
        q.packets = data['end']['sum']['packets']
        q.lost = data['end']['sum']['lost_packets']
    q.version = data['start']['version']
    q.save()
    logger.info('--------------------')

    # channel_layer = get_channel_layer()
    # async_to_sync(channel_layer.group_send)("chat", {"type": "chat.force_disconnect"})

    # channel_layer = get_channel_layer()
    # async_to_sync(channel_layer.send)(self.channel_name, {
    #     "type": "websocket.send",
    #     "text": "Hello from my_function!",
    # })

    # channel_layer = get_channel_layer()
    # channel_name = "home"
    # async_to_sync(channel_layer.send)(channel_name, {
    #     "type": "websocket.send",
    #     "text": json.dumps({"message": "Hello, World!"}),
    # })

    # logger.info('--------------------')
    # socket_message = 'Hello Earth!'
    # channel_layer = get_channel_layer()
    # group_name = "home_group"
    # async_to_sync(channel_layer.group_send)(
    #     group_name,
    #     {
    #         "type": "websocket.send",
    #         "text": json.dumps({"message": socket_message}),
    #     },
    # )
    # logger.info('--------------------')

    logger.info('--------------------')

    socket_dict = {'message': f'New Result for {q.ip}. Refresh now to see...'}

    channel_layer = get_channel_layer()
    group_name = "home_group"
    event = {
        "type": "websocket.send",
        "text": json.dumps(socket_dict),
    }
    async_to_sync(channel_layer.group_send)(group_name, event)

    logger.info('--------------------')
    logger.info('--------------------')
    send_discord_message.delay(pk)
    return True


def format_bytes(size):
    units = ["B", "KB", "MB", "GB", "TB"]
    for unit in units:
        if size < 1024:
            return f"{size:.2f} {unit}"
        size /= 1024
    return f"{size:.2f} {units[-1]}"


def format_bps(bps):
    units = ["bps", "Kbps", "Mbps", "Gbps", "Tbps"]
    for unit in units:
        if bps < 1000:
            return f"{bps:.2f} {unit}"
        bps /= 1000
    return f"{bps:.2f} {units[-1]}"


def get_ip_data(ip_addr):
    try:
        host_name = socket.gethostbyaddr(ip_addr)[0]
    except:
        host_name = ''

    private = ipaddress.ip_address(ip_addr).is_private
    if not private:
        try:
            ip_whois = IPWhois(ip_addr)
            ip_info = ip_whois.lookup_rdap(depth=1)
        except:
            ip_info = {}

    return {
        'ip': ip_addr,
        'name': host_name,
        'private': private,
        'data': ip_info if 'ip_info' in vars() else {},
    }
