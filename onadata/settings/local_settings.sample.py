import os

CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "asgi_redis.RedisChannelLayer",
        "CONFIG": {
            "hosts": [("redis", 6379)],
        },
        "ROUTING": "onadata.apps.fieldsight.routing.channel_routing",
    },
}
# CELERY_IMPORTS = ("onadata.apps.fieldsight.tasks",)

WEBSOCKET_URL = "localhost"
WEBSOCKET_PORT = "8001"

os.environ["DJANGO_SECRET_KEY"] = "@25)**hc^rjaiagb4#&q*84hr*uscsxwr-cv#0joiwj$))obyk"
os.environ["KOBOCAT_MONGO_HOST"] = "mongo"
os.environ["CSRF_COOKIE_DOMAIN"] = "localhost"

TESTING_MODE = os.environ.get('KOBO_TEST_MODE', False)
if not TESTING_MODE:
    from onadata.settings.kc_environ import *
else:
    from onadata.settings.test_environ import *

CORS_ORIGIN_ALLOW_ALL = True
DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': 'kobocat1',
        'USER': 'postgres',
        'PASSWORD': 'password',
        'HOST': 'db',
        'PORT': '',
    }
}

INSTALLED_APPS = list(INSTALLED_APPS)

MIDDLEWARE_CLASSES += (
    # 'debug_toolbar.middleware.DebugToolbarMiddleware',
    
)

INSTALLED_APPS += ['fcm',]
INSTALLED_APPS += ['channels']
INTERNAL_IPS = ['127.0.0.1',]

FCM_APIKEY = "<YOUR_FCM_API_KEY>"

FCM_MAX_RECIPIENTS = 1000


CORS_ORIGIN_WHITELIST = (
    'dev.ona.io',
    'google.com',
    'app.fieldsight.org',
    'kpi.fieldsight.org',
    'bcss.com.np.com',
    'kc.bcss.com.np',
    'localhost:8001',
    'kpi:8000'
)

TIME_ZONE = 'Asia/Kathmandu'

from onadata.settings.common import REST_FRAMEWORK
REST_FRAMEWORK.update({'DEFAULT_PERMISSION_CLASSES':['rest_framework.permissions.IsAuthenticated',]})


# DEBUG_TOOLBAR_CONFIG = {
#     'INTERCEPT_REDIRECTS': True
# }

FILE_UPLOAD_HANDLERS = ("django_excel.ExcelMemoryFileUploadHandler",
                        "django_excel.TemporaryExcelFileUploadHandler")

# DEBUG = False

SESSION_ENGINE = "django.contrib.sessions.backends.signed_cookies"
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', '@25)**hc^rjaiagb4#&q*84hr*uscsxwr-cv#0joiwj$))obyk')
SESSION_COOKIE_NAME = 'kobo_cookie'
# SESSION_COOKIE_DOMAIN = '192.168.1.17'
# SESSION_COOKIE_DOMAIN = None
SESSION_COOKIE_DOMAIN = 'localhost'

BROKER_URL = 'amqp://guest:guest@localhost:5672/'
