import json
import logging
import plotly.graph_objects as go
import plotly.express as px
import plotly.io as pio
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import HttpResponse, Http404
from django.shortcuts import render, get_object_or_404
from django.template.loader import render_to_string
from django.views.decorators.cache import cache_page
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.views.decorators.vary import vary_on_headers
from .models import SpeedTest, Webhooks
from .tasks import process_data

logger = logging.getLogger('app')


def home_view(request):
    # View: /
    logger.debug('home_view')
    q = SpeedTest.objects.all()
    context = {'data': q}
    if request.user.is_authenticated:
        webhooks = Webhooks.objects.filter(owner=request.user)
        context.update({'webhooks': webhooks})
    return render(request, 'home.html', context)


def speedtest_view(request):
    # View: /speedtest/
    logger.debug('speedtest_view')
    return render(request, 'speedtest.html')


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

    data = json.loads(q.json)
    if 'intervals' not in data or not data['intervals']:
        logger.debug('intervals not in query')
        raise Http404

    x = []
    for d in data['intervals']:
        x.append(d['sum']['bits_per_second'])

    pio.templates.default = 'plotly_dark'
    fig = go.Figure(go.Indicator(
        mode='gauge+number',
        value=q.bps,
        # domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': f'{q.get_type()} Speed', 'font': {'size': 36}},
        gauge={'axis': {'range': [None, max(x) * 1.1]},
               'steps': [
                   {'range': [min(x), max(x)], 'color': 'gray'},
               ]}
    ))
    if not fig:
        logger.debug('no fig')
        raise Http404

    fig.update_layout(
        annotations=[
            dict(x=0, y=0.07, text=q.ip_city,
                 showarrow=False, xref='paper', yref='paper',
                 font=dict(family='sans serif', size=22, color='white')),
            dict(x=0, y=0, text=q.name,
                 showarrow=False, xref='paper', yref='paper',
                 font=dict(family='sans serif', size=22, color='white')),
            dict(x=1, y=0.07, text=q.ip_org,
                 showarrow=False, xref='paper', yref='paper',
                 font=dict(family='sans serif', size=22, color='white')),
            dict(x=1, y=0, text=q.ip,
                 showarrow=False, xref='paper', yref='paper',
                 font=dict(family='sans serif', size=22, color='white')),
        ],
        margin=dict(t=10, l=50, b=10, r=50),
    )
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
    return HttpResponse(fig.to_html(include_plotlyjs='cdn',
                                    config={'displaylogo': False}))


def map_view(request, pk):
    # View: /{pk}/map/
    logger.debug('map_view: %s', pk)
    q = get_object_or_404(SpeedTest, pk=pk)
    pio.templates.default = 'plotly_dark'
    fig = render_map_fig(q)
    if not fig:
        logger.debug('no fig')
        raise Http404

    return HttpResponse(fig.to_html(include_plotlyjs='cdn',
                                    config={'displaylogo': False}))


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


@login_required
@csrf_exempt
@require_http_methods(['POST'])
def del_hook_view_a(request, pk):
    logger.debug('del_hook_view_a: %s', pk)
    webhook = Webhooks.objects.get(pk=pk)
    if webhook.owner != request.user:
        return HttpResponse(status=401)
    logger.debug(webhook)
    webhook.delete()
    return HttpResponse(status=204)


# @user_passes_test(lambda u: u.is_superuser)
# @csrf_exempt
# @require_http_methods(['POST'])
# def del_result_view_a(request, pk):
#     logger.debug('del_result_view_a: %s', pk)
#     speedtest = SpeedTest.objects.filter(pk=pk)
#     if speedtest:
#         speedtest[0].delete()
#     return HttpResponse(status=204)


@csrf_exempt
# @cache_page(60 * 60 * 24)
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
        return HttpResponse(status=200)

    fig.update_layout(margin=dict(t=10, l=16, b=10, r=10))
    return HttpResponse(fig.to_html(include_plotlyjs=False,
                                    full_html=False,
                                    config={'displaylogo': False},))


@csrf_exempt
@cache_page(60 * 60 * 24)
def map_view_a(request, pk):
    # View: /ajax/{pk}/map/
    logger.debug('map_view_a: %s', pk)
    q = get_object_or_404(SpeedTest, pk=pk)
    fig = render_map_fig(q)
    if not fig:
        return HttpResponse(status=200)

    fig.update_layout(margin=dict(t=10, l=10, b=10, r=10))
    return HttpResponse(fig.to_html(include_plotlyjs=False,
                                    full_html=False,
                                    config={'displaylogo': False, 'scrollZoom': False},))


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
        ),
    )
    return fig
