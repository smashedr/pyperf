import logging
from django import template
from django.conf import settings
from django.templatetags.static import static

logger = logging.getLogger('app')
register = template.Library()


@register.simple_tag(name='get_config')
def get_config(value):
    return getattr(settings, value, None)


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
