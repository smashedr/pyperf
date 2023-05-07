import httpx
import logging
import urllib.parse
from datetime import datetime, timedelta
from decouple import config, Csv
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login, logout
from django.shortcuts import HttpResponseRedirect, redirect
from django.views.decorators.http import require_http_methods
from home.models import Webhooks
from .models import CustomUser

logger = logging.getLogger('app')


def oauth_start(request):
    """
    View  /oauth/
    """
    logger.debug('oauth_start')
    request.session['login_redirect_url'] = get_next_url(request)
    params = {
        'redirect_uri': config('OAUTH_REDIRECT_URL'),
        'client_id': config('OAUTH_CLIENT_ID'),
        'response_type': config('OAUTH_RESPONSE_TYPE', 'code'),
        'scope': config('OAUTH_SCOPE', 'identify'),
        'prompt': config('OAUTH_PROMPT', 'none'),
    }
    url_params = urllib.parse.urlencode(params)
    url = f'https://discord.com/api/oauth2/authorize?{url_params}'
    return HttpResponseRedirect(url)


def oauth_callback(request):
    """
    View  /oauth/callback/
    """
    logger.debug('oauth_callback')
    if 'code' not in request.GET:
        messages.warning(request, 'User aborted or no code in response...')
        return HttpResponseRedirect(get_login_redirect_url(request))
    try:
        logger.debug('code: %s', request.GET['code'])
        auth_data = get_access_token(request.GET['code'])
        logger.debug('auth_data: %s', auth_data)
        profile = get_user_profile(auth_data)
        logger.debug('profile: %s', profile)
        user, _ = CustomUser.objects.get_or_create(username=profile['id'])
        update_profile(user, profile)
        login(request, user)
        if 'webhook' in auth_data:
            logger.debug('webhook in profile')
            webhook = add_webhook(request, auth_data)
            messages.info(request, f'Webhook successfully added: {webhook.id}')
        else:
            messages.info(request, f'Successfully logged in. {user.first_name}.')
    except Exception as error:
        logger.exception(error)
        messages.error(request, f'Exception during login: {error}')
    return HttpResponseRedirect(get_login_redirect_url(request))


@require_http_methods(['POST'])
def oauth_logout(request):
    """
    View  /oauth/logout/
    """
    next_url = get_next_url(request)
    logger.debug('oauth_logout: %s', next_url)

    # Hack to prevent login loop when logging out on a secure page
    logger.debug('next_url: %s', next_url.split('/')[1])
    secure_views_list = ['profile']
    if '/' in next_url and next_url.split('/')[1] in secure_views_list:
        next_url = '/'

    request.session['login_next_url'] = next_url
    logout(request)
    messages.info(request, f'Successfully logged out.')
    return redirect(next_url)


def oauth_webhook(request):
    """
    View  /oauth/webhook/
    """
    request.session['login_redirect_url'] = get_next_url(request)
    logger.debug('oauth_webhook: %s', request.session['login_redirect_url'])
    params = {
        'redirect_uri': config('OAUTH_REDIRECT_URL'),
        'client_id': config('OAUTH_CLIENT_ID'),
        'response_type': config('OAUTH_RESPONSE_TYPE', 'code'),
        'scope': config('OAUTH_SCOPE', 'identify'),
    }
    url_params = urllib.parse.urlencode(params)
    url = f'https://discord.com/api/oauth2/authorize?{url_params}'
    return HttpResponseRedirect(url)


def add_webhook(request, profile):
    """
    Add webhook
    """
    webhook = Webhooks(
        hook_id=profile['webhook']['id'],
        guild_id=profile['webhook']['guild_id'],
        channel_id=profile['webhook']['channel_id'],
        url=profile['webhook']['url'],
        owner=request.user,
    )
    webhook.save()
    return webhook


def get_access_token(code):
    """
    Post OAuth code and Return access_token
    """
    url = 'https://discord.com/api/v8/oauth2/token'
    data = {
        'redirect_uri': config('OAUTH_REDIRECT_URL'),
        'client_id': config('OAUTH_CLIENT_ID'),
        'client_secret': config('OAUTH_CLIENT_SECRET'),
        'grant_type': config('OAUTH_GRANT_TYPE', 'authorization_code'),
        'code': code,
    }
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    r = httpx.post(url, data=data, headers=headers, timeout=10)
    if not r.is_success:
        logger.info('status_code: %s', r.status_code)
        logger.error('content: %s', r.content)
        r.raise_for_status()
    return r.json()


def get_user_profile(data):
    """
    Get Profile for Authenticated User
    """
    url = 'https://discord.com/api/v8/users/@me'
    headers = {'Authorization': f"Bearer {data['access_token']}"}
    r = httpx.get(url, headers=headers, timeout=10)
    if not r.is_success:
        logger.info('status_code: %s', r.status_code)
        logger.error('content: %s', r.content)
        r.raise_for_status()
    logger.info('r.json(): %s', r.json())
    profile = r.json()

    # CUSTOM USER PROFILE DATA - profile
    data = {
        'id': profile['id'],
        'username': profile['username'],
        'discriminator': profile['discriminator'],
        'avatar': profile['avatar'],
        'access_token': data['access_token'],
        'refresh_token': data['refresh_token'],
        'expires_in': datetime.now() + timedelta(0, data['expires_in']),
    }
    if 'webhook' in profile:
        webhook = {'webhook': {
            'id': profile['webhook']['id'],
            'url': profile['webhook']['url'],
            'guild_id': profile['webhook']['guild_id'],
            'channel_id': profile['webhook']['channel_id'],
        }}
        data.update(webhook)
    return data


def update_profile(user, profile):
    """
    Update Django user profile with provided data
    """
    user.first_name = profile['username']
    user.last_name = profile['discriminator']
    user.avatar_hash = profile['avatar']
    user.access_token = profile['access_token']
    if profile['id'] in config('SUPER_USERS', '', Csv()):
        logger.info('Super user login: %s', profile['id'])
        user.is_staff = True
        user.is_admin = True
        user.is_superuser = True
    user.save()
    return


def get_next_url(request):
    """
    Determine 'next' parameter
    """
    if 'next' in request.GET:
        return request.GET['next']
    if 'next' in request.POST:
        return request.POST['next']
    if 'next_url' in request.session:
        url = request.session['next_url']
        del request.session['next_url']
        request.session.modified = True
        return url
    return '/'


def get_login_redirect_url(request):
    """
    Determine 'login_redirect_url' parameter
    """
    if 'login_redirect_url' in request.session:
        url = request.session['login_redirect_url']
        del request.session['login_redirect_url']
        request.session.modified = True
        return url
    return '/'
