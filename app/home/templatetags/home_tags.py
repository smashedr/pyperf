import flag
import json
import logging
from django import template
from django.conf import settings
from django.templatetags.static import static

logger = logging.getLogger('app')
register = template.Library()


@register.simple_tag(name='get_config')
def get_config(value):
    # get django setting value or return none
    return getattr(settings, value, None)


@register.filter(name='absolute_url')
def absolute_url(absolute_uri):
    # returns the absolute_url from the absolute_uri
    return '{0}//{2}'.format(*absolute_uri.split('/'))


@register.filter(name='tag_to_class')
def tag_to_class(message_tag):
    # returns bootstrap tag from django message tag
    return {
        'info': 'primary',
        'success': 'success',
        'warning': 'warning',
        'error': 'danger',
    }[message_tag]


@register.filter(name='avatar_url')
def avatar_url(user):
    # return discord avatar url from user model
    if user.avatar_hash:
        return f'https://cdn.discordapp.com/avatars/' \
               f'{ user.username }/{ user.avatar_hash }.png'
    else:
        return static('images/assets/default.png')


@register.filter(name='crstrip')
def crstrip(value, string=' '):
    # custom rstrip filter for django
    return value.rstrip(string)


@register.filter(name='json_to_dict')
def json_to_dict(value):
    # custom json.loads filter for django
    return json.loads(value)


@register.filter(name='cc_to_flag')
def cc_to_flag(cc):
    # returns flag for given country code
    return flag.flag(cc) if cc else cc
