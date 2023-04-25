import json
import logging
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.template.loader import render_to_string
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from .models import SpeedTest
from .tasks import process_data

logger = logging.getLogger('app')


def home_view(request):
    # View: /
    logger.debug('home_view')
    q = reversed(SpeedTest.objects.all())
    logger.debug(q)
    return render(request, 'home.html', {'data': q})


def result_view(request, pk):
    # View: /result/{pk}/
    logger.debug('result_view')
    q = SpeedTest.objects.get(pk=pk)
    logger.debug(q)
    d = json.loads(q.json)
    context = {'data': q, 'raw': d}
    return render(request, 'result.html', context)


@csrf_exempt
@require_http_methods(['POST'])
def tdata_view(request):
    # View: /ajax/tdata/
    logger.debug('tr_view')
    logger.debug(request.POST)
    pk = int(request.POST['pk'])
    logger.debug(pk)
    speedtest = SpeedTest.objects.get(pk=pk)
    logger.debug(speedtest)
    table_str = render_to_string('include/table-tr.html', {'data': speedtest})
    return HttpResponse(table_str, status=200)


@csrf_exempt
@require_http_methods(['POST'])
def save_iperf(request):
    # View: /save/
    logger.debug('save_iperf')
    body = request.body.decode('utf-8')
    data = json.loads(body)
    speedtest = SpeedTest.objects.create(json=data)
    logger.debug(f'test.pk: {speedtest.pk}')
    process_data.delay(speedtest.pk)
    return HttpResponse(status=204)
