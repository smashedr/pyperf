import sentry_sdk
from celery.schedules import crontab
from decouple import config, Csv
from django.contrib.messages import constants as message_constants
from pathlib import Path
from sentry_sdk.integrations.django import DjangoIntegration

BASE_DIR = Path(__file__).resolve().parent.parent
SECRET_KEY = config('SECRET_KEY')
DEBUG = config('DEBUG', False, bool)
ALLOWED_HOSTS = config('ALLOWED_HOSTS', '*', Csv())
SESSION_COOKIE_AGE = config('SESSION_COOKIE_AGE', 3600 * 24 * 14, int)


# SECURE_REFERRER_POLICY = config('SECURE_REFERRER_POLICY', 'no-referrer')
# CSRF_TRUSTED_ORIGINS = config('CSRF_ORIGINS', cast=Csv())
SPEEDTEST_URL = config('SPEEDTEST_URL')
SITE_URL = config('SITE_URL', 'http://localhost:8000')
DISCORD_INVITE = config('DISCORD_INVITE')
SUPER_USER_IDS = config('SUPER_USER_IDS', cast=Csv())
MAPBOX_TOKEN = config('MAPBOX_TOKEN', '')
USE_X_FORWARDED_HOST = config('USE_X_FORWARDED_HOST', False, bool)
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
X_FRAME_OPTIONS = 'SAMEORIGIN'
DJANGO_REDIS_IGNORE_EXCEPTIONS = config('REDIS_IGNORE_EXCEPTIONS', True, bool)


ASGI_APPLICATION = 'pyperf.asgi.application'
ROOT_URLCONF = 'pyperf.urls'
AUTH_USER_MODEL = 'oauth.CustomUser'

LOGIN_REDIRECT_URL = '/'
LOGIN_URL = '/oauth/'
STATIC_URL = '/static/'
MEDIA_URL = '/media/'
STATIC_ROOT = config('STATIC_ROOT')
MEDIA_ROOT = config('MEDIA_ROOT')
STATICFILES_DIRS = [BASE_DIR / 'static']
TEMPLATES_DIRS = [BASE_DIR / 'templates']

LANGUAGE_CODE = config('LANGUAGE_CODE', 'en-us')
USE_TZ = config('USE_TZ', True, bool)
TIME_ZONE = config('TZ', 'UTC')
USE_I18N = True
USE_L10N = True

DISCORD_API_URL = config('DISCORD_API_URL')
OAUTH_CLIENT_ID = config('OAUTH_CLIENT_ID')
OAUTH_CLIENT_SECRET = config('OAUTH_CLIENT_SECRET')
OAUTH_REDIRECT_URI = config('OAUTH_REDIRECT_URI')
OAUTH_GRANT_TYPE = config('OAUTH_GRANT_TYPE')
OAUTH_SCOPE = config('OAUTH_SCOPE')

CELERY_RESULT_BACKEND = config('CELERY_RESULT_BACKEND')
CELERY_ACCEPT_CONTENT = ['application/json']
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = config('TZ', 'UTC')

MESSAGE_TAGS = {
    message_constants.DEBUG: 'secondary',
    message_constants.INFO: 'primary',
    message_constants.SUCCESS: 'success',
    message_constants.WARNING: 'warning',
    message_constants.ERROR: 'danger',
}

CELERY_BEAT_SCHEDULE = {
    'clear_sessions': {
        'task': 'home.tasks.clear_sessions',
        'schedule': crontab(minute=0, hour=0),
    },
    'results_cleanup': {
        'task': 'home.tasks.delete_empty_results',
        'schedule': crontab('*/15')
    },
}

if config('SENTRY_URL', False):
    sentry_sdk.init(
        dsn=config('SENTRY_URL'),
        integrations=[DjangoIntegration()],
        traces_sample_rate=config('SENTRY_SAMPLE_RATE', 0.25, float),
        send_default_pii=True,
        debug=config('SENTRY_DEBUG', config('DEBUG', False), bool),
        environment=config('SENTRY_ENVIRONMENT'),
    )

CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            'hosts': [('redis', 6379)],
        },
    },
}

CACHES = {
    'default': {
        'BACKEND': config('CACHE_BACKEND',
                          'django.core.cache.backends.dummy.DummyCache'),
        'LOCATION': config('CACHE_LOCATION'),
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        },
    },
}

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': config('DATABASE_NAME'),
        'USER': config('DATABASE_USER'),
        'PASSWORD': config('DATABASE_PASS'),
        'HOST': config('DATABASE_HOST'),
        'PORT': config('DATABASE_PORT'),
        'OPTIONS': {
            'isolation_level': 'repeatable read',
            'init_command': "SET sql_mode='STRICT_ALL_TABLES'",
        },
    },
}

INSTALLED_APPS = [
    'channels',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_celery_beat',
    'django_extensions',
    'debug_toolbar',
    'home',
    'oauth',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'debug_toolbar.middleware.DebugToolbarMiddleware',
]

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': TEMPLATES_DIRS,
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.template.context_processors.media',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.static',
            ],
        },
    },
]

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format': ('%(asctime)s '
                       '%(levelname)s - '
                       '%(filename)s - '
                       '%(module)s.%(funcName)s:%(lineno)d - '
                       '%(message)s'),
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'standard',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': config('DJANGO_LOG_LEVEL', 'INFO'),
            'propagate': True,
        },
        'app': {
            'handlers': ['console'],
            'level': config('APP_LOG_LEVEL', 'DEBUG'),
            'propagate': True,
        },
    },
}

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

if DEBUG:
    def show_toolbar(request):
        return True if request.user.is_superuser else False
    DEBUG_TOOLBAR_CONFIG = {'SHOW_TOOLBAR_CALLBACK': show_toolbar}
    DEBUG_TOOLBAR_PANELS = [
        'debug_toolbar.panels.versions.VersionsPanel',
        'debug_toolbar.panels.timer.TimerPanel',
        'debug_toolbar.panels.settings.SettingsPanel',
        'debug_toolbar.panels.headers.HeadersPanel',
        'debug_toolbar.panels.request.RequestPanel',
        'debug_toolbar.panels.sql.SQLPanel',
        'debug_toolbar.panels.staticfiles.StaticFilesPanel',
        'debug_toolbar.panels.templates.TemplatesPanel',
        'debug_toolbar.panels.cache.CachePanel',
        'debug_toolbar.panels.signals.SignalsPanel',
        'debug_toolbar.panels.logging.LoggingPanel',
        'debug_toolbar.panels.redirects.RedirectsPanel',
    ]
