import flag
import logging
from django import template
from django.conf import settings
from django.templatetags.static import static
from home.views import render_graph_fig

logger = logging.getLogger('app')
register = template.Library()


@register.simple_tag(name='get_config')
def get_config(value):
    return getattr(settings, value, None)


@register.filter(name='absolute_url')
def absolute_url(value):
    return '{0}//{2}'.format(*value.split('/'))


@register.filter(name='crstrip')
def crstrip(value, string):
    return value.rstrip(string)


@register.filter(name='cc_to_flag')
def cc_to_flag(value):
    return flag.flag(value) if value else value


@register.filter(name='tag_to_class')
def tag_to_class(value):
    return {
        'info': 'primary',
        'success': 'success',
        'warning': 'warning',
        'error': 'danger',
    }[value]


@register.filter(name='avatar_url')
def avatar_url(avatar_hash, username):
    if avatar_hash:
        return f'https://cdn.discordapp.com/avatars/{ username }/{ avatar_hash }.png'
    else:
        return static('images/assets/default.png')


@register.filter(name='render_graph')
def render_graph(value):
    fig = render_graph_fig(value)
    fig.update_layout(
        margin=dict(t=10, l=16, b=10, r=10)
    )
    return fig.to_html(full_html=False, config={'displaylogo': False})
