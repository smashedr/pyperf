import json
import logging
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from .models import SpeedTest
from .tasks import process_data

logger = logging.getLogger('app')


def home_view(request):
    # View: /
    logger.debug('home_view')

    # channel_layer = get_channel_layer()
    # async_to_sync(channel_layer.group_send)(
    #     'test',
    #     {
    #         'type': 'chat_message',
    #         'message': "event_trigered_from_views"
    #     }
    # )

    q = reversed(SpeedTest.objects.all())
    logger.debug(q)
    return render(request, 'home.html', {'data': q})


def result_view(request, pk):
    # View: /result/{pk}
    logger.debug('result_view')
    q = SpeedTest.objects.get(pk=pk)
    logger.debug(q)
    d = json.loads(q.json)
    context = {'data': q, 'raw': d}
    return render(request, 'result.html', context)


@csrf_exempt
@require_http_methods(['POST'])
def save_iperf(request):
    # View: /save/
    logger.debug('save_iperf')
    body = request.body.decode('utf-8')
    data = json.loads(body)
    test = SpeedTest.objects.create(json=data)
    logger.debug(f'test.pk: {test.pk}')
    process_data.delay(test.pk)
    return JsonResponse({}, status=204)
