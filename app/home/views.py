import json
import logging
import plotly.graph_objects as go
import plotly.express as px
import plotly.io as pio
from django.conf import settings
from django.http import HttpResponse, Http404
from django.shortcuts import render, get_object_or_404
from django.template.loader import render_to_string
from django.views.decorators.cache import cache_page
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.views.decorators.vary import vary_on_headers
from .models import SpeedTest
from .tasks import process_data

logger = logging.getLogger('app')


def home_view(request):
    # View: /
    logger.debug('home_view')
    q = SpeedTest.objects.all()
    return render(request, 'home.html', {'data': q})


# @vary_on_headers('Cookie')
# @cache_page(60 * 60 * 24)
def test_view(request, pk=0):
    # View: /test/{pk}/
    logger.debug('test_view: %s', pk)
    q = SpeedTest.objects.get(pk=pk) if pk else None
    return render(request, 'test.html', {'pk': pk, 'data': q})


def result_view(request, pk):
    # View: /{pk}/
    logger.debug('result_view: %s', pk)
    q = get_object_or_404(SpeedTest, pk=pk)
    return render(request, 'result.html', {'data': q})


@cache_page(60 * 60 * 24)
def image_view(request, pk):
    # View: /{pk}.png
    logger.debug('image_view: %s', pk)
    q = get_object_or_404(SpeedTest, pk=pk)
    pio.templates.default = 'plotly_dark'
    fig = go.Figure(go.Indicator(
        mode='gauge+number',
        value=q.bps,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': f'{q.get_type()} Speed'},
    ))
    if not fig:
        logger.debug('no fig')
        raise Http404

    return HttpResponse(fig.to_image(), content_type='image/x-png')


def graph_view(request, pk):
    # View: /{pk}/graph/
    logger.debug('graph_view: %s', pk)
    q = get_object_or_404(SpeedTest, pk=pk)
    pio.templates.default = 'plotly_dark'
    fig = render_graph_fig(q)
    if not fig:
        logger.debug('no fig')
        raise Http404

    fig.layout.title.text = f'{q.get_type()} Speed'
    return HttpResponse(fig.to_html(config={'displaylogo': False}))


def map_view(request, pk):
    # View: /{pk}/map/
    logger.debug('map_view: %s', pk)
    q = get_object_or_404(SpeedTest, pk=pk)
    pio.templates.default = 'plotly_dark'
    fig = render_map_fig(q)
    if not fig:
        logger.debug('no fig')
        raise Http404

    return HttpResponse(fig.to_html(config={'displaylogo': False}))


@csrf_exempt
@require_http_methods(['POST'])
def save_iperf(request):
    # View: /save/
    logger.debug('save_iperf')
    data = json.loads(request.body.decode('utf-8'))
    q = SpeedTest.objects.create(json=data)
    logger.debug(f'pk: {q.pk}')
    process_data.delay(q.pk)
    return HttpResponse(status=204)


@csrf_exempt
@cache_page(60 * 60 * 24)
def tdata_view_a(request, pk):
    # View: /ajax/{pk}/tdata/
    logger.debug('tr_view: %s', pk)
    q = get_object_or_404(SpeedTest, pk=pk)
    response = render_to_string('include/table-tr.html', {'data': q})
    return HttpResponse(response)


@csrf_exempt
@cache_page(60 * 60 * 24)
def graph_view_a(request, pk):
    # View: /ajax/{pk}/graph/
    logger.debug('graph_view_a: %s', pk)
    q = get_object_or_404(SpeedTest, pk=pk)
    fig = render_graph_fig(q)
    if not fig:
        return HttpResponse(status=204)

    fig.update_layout(margin=dict(t=10, l=16, b=10, r=10))
    return HttpResponse(fig.to_html(include_plotlyjs="cdn",
                                    full_html=False,
                                    config={'displaylogo': False}))


@csrf_exempt
@cache_page(60 * 60 * 24)
def map_view_a(request, pk):
    # View: /ajax/{pk}/map/
    logger.debug('map_view_a: %s', pk)
    q = get_object_or_404(SpeedTest, pk=pk)
    fig = render_map_fig(q)
    if not fig:
        return HttpResponse(status=204)

    fig.update_layout(margin=dict(t=10, l=10, b=10, r=10))
    return HttpResponse(fig.to_html(include_plotlyjs="cdn",
                                    full_html=False,
                                    config={'displaylogo': False}))


def render_graph_fig(query_or_pk):
    logger.debug('render_graph_fig')
    if not isinstance(query_or_pk, SpeedTest):
        query_or_pk = SpeedTest.objects.get(pk=int(query_or_pk))
    q = query_or_pk
    data = json.loads(q.json)
    if 'intervals' not in data or not data['intervals']:
        logger.debug('intervals not in query')
        return None

    x, y = [], []
    for i, d in enumerate(data['intervals']):
        x.append(i)
        y.append(d['sum']['bits_per_second'])
    df = {'Seconds': x, 'Speed': y}
    pio.templates.default = 'plotly_dark'
    fig = px.line(df, x='Seconds', y='Speed', markers=True, line_shape='linear')
    return fig


def render_map_fig(query_or_pk):
    logger.debug('render_map_fig')
    if not isinstance(query_or_pk, SpeedTest):
        query_or_pk = SpeedTest.objects.get(pk=int(query_or_pk))
    q = query_or_pk
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
