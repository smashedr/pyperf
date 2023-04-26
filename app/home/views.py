import json
import logging
import plotly.graph_objects as go
import plotly.express as px
import plotly.io as pio
from django.conf import settings
from django.http import HttpResponse, Http404, JsonResponse
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
    # View: /{pk}/
    logger.debug('result_view')
    q = SpeedTest.objects.get(pk=pk)
    logger.debug(q)
    d = json.loads(q.json)
    context = {'data': q, 'raw': d}
    return render(request, 'result.html', context)


def graph_view(request, pk):
    # View: /{pk}/graph/
    logger.debug('image_view')
    q = SpeedTest.objects.get(pk=pk)
    logger.debug(q)
    if not q:
        raise Http404

    fig = render_graph_fig(q)
    fig.layout.title.text = f'{q.get_type()} Speed'
    return HttpResponse(fig.to_html(config={'displaylogo': False}))


def map_view(request, pk):
    # View: /{pk}/map/
    logger.debug('map_view')
    q = SpeedTest.objects.get(pk=pk)
    logger.debug(q)
    if not q:
        raise Http404

    fig = render_map_fig(q)
    return HttpResponse(fig.to_html(config={'displaylogo': False}))


def image_view(request, pk):
    # View: /{pk}.png
    logger.debug('image_view')
    q = SpeedTest.objects.get(pk=pk)
    logger.debug(q)
    if not q:
        raise Http404

    pio.templates.default = 'plotly_dark'
    fig = go.Figure(go.Indicator(
        mode='gauge+number',
        value=q.bps,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': f'{q.get_type()} Speed'},
    ))
    return HttpResponse(fig.to_image(), content_type='image/x-png')


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


def render_graph_fig(query_or_pk):
    logger.debug('render_graph_html')
    if not isinstance(query_or_pk, SpeedTest):
        query_or_pk = SpeedTest.objects.get(pk=int(query_or_pk))
    q = query_or_pk
    logger.debug(q)
    d = json.loads(query_or_pk.json)
    x, y = [], []
    for i, d in enumerate(d['intervals']):
        x.append(i)
        y.append(d['sum']['bits_per_second'])
    df = {'Seconds': x, 'Speed': y}
    pio.templates.default = 'plotly_dark'
    fig = px.line(df, x='Seconds', y='Speed', markers=True, line_shape='linear')
    return fig


def render_map_fig(query_or_pk):
    logger.debug('render_graph_html')
    if not isinstance(query_or_pk, SpeedTest):
        query_or_pk = SpeedTest.objects.get(pk=int(query_or_pk))
    q = query_or_pk
    logger.debug(q)
    if not q.ip_lat or not q.ip_lon:
        return None

    pio.templates.default = 'plotly_dark'
    fig = go.Figure(go.Scattermapbox(
        lat=[str(q.ip_lat)],
        lon=[str(q.ip_lon)],
        mode='markers',
        marker=go.scattermapbox.Marker(size=14),
        text=[q.ip_city or 'Unknown'],
    ))
    fig.update_layout(
        hovermode='closest',
        mapbox=dict(
            accesstoken=settings.MAPBOX_TOKEN,
            bearing=0,
            center=go.layout.mapbox.Center(
                lat=int(q.ip_lat),
                lon=int(q.ip_lon),
            ),
            pitch=0,
            zoom=5,
        )
    )
    return fig
