import os, stripe

os.environ["DJANGO_SECRET_KEY"] = '*********************'
os.environ["KOBOCAT_MONGO_HOST"] = "*********************"
os.environ["KOBOFORM_URL"] = 'http://kpi.fieldsight.org'
os.environ["KOBOFORM_SERVER"] = 'http://kpi.fieldsight.org'
#os.environ["ENKETO_API_TOKEN"] = 'hellofield'

from onadata.settings.kc_environ import *
#CORS_ORIGIN_ALLOW_ALL = True
KOBOCAT_INTERNAL_HOSTNAME = "localhost"
os.environ["ENKETO_API_TOKEN"] = '*********************'
ENKETO_API_TOKEN = "*********************"

XML_VERSION_MAX_ITER = 6

DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': '*********************',
        'USER': '*********************',
        'PASSWORD': '*********************',
        'HOST': '*********************',
        'PORT': '*********************',
    },
    'defauli': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': '*********************',
        'USER': '*********************',
        'PASSWORD': '*********************',
        'HOST': '*********************',
        'PORT': '',
    }
}

INSTALLED_APPS = list(INSTALLED_APPS)
INSTALLED_APPS += ['fcm', 'channels', 'rest_framework_docs', 'social_django']
FCM_APIKEY = "*********************"

# ........Google login.......
MIDDLEWARE_CLASSES += ('social_django.middleware.SocialAuthExceptionMiddleware',)
TEMPLATE_CONTEXT_PROCESSORS += ('social_django.context_processors.backends', 'social_django.context_processors.login_redirect',)

AUTHENTICATION_BACKENDS += (
    'social_core.backends.facebook.FacebookOAuth2',
    'social_core.backends.google.GoogleOAuth2',
)

SOCIAL_AUTH_GOOGLE_OAUTH2_KEY = "*********************"
SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET ="*********************"
SOCIAL_AUTH_LOGIN_REDIRECT_URL = '/users/create-profile/'
SOCIAL_AUTH_LOGIN_URL = '/accounts/login/'
SOCIAL_AUTH_PIPELINE = (
    'social_core.pipeline.social_auth.social_details',
    'social_core.pipeline.social_auth.social_uid',
    'social_core.pipeline.social_auth.auth_allowed',
    'social_core.pipeline.user.get_username',
    'onadata.apps.users.pipeline.email_validate',
    'social_core.pipeline.social_auth.associate_by_email',
    'social_core.pipeline.user.create_user',
    'social_core.pipeline.social_auth.associate_user',
    'onadata.apps.users.pipeline.create_role',
    'onadata.apps.users.pipeline.create_profile',
    'social_core.pipeline.social_auth.load_extra_data',
    'social_core.pipeline.user.user_details',
)


FCM_MAX_RECIPIENTS = 1000

SERIALIZATION_MODULES = {
        "custom_geojson": "onadata.apps.fieldsight.serializers.GeoJSONSerializer",
}
SEND_ACTIVATION_EMAIL = True
ACCOUNT_ACTIVATION_DAYS = 30
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
DEFAULT_FROM_EMAIL = '*********************'
SERVER_EMAIL = '*********************'
EMAIL_USE_TLS = True
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_HOST_USER = '*********************'
EMAIL_HOST_PASSWORD = '*********************'
CORS_ORIGIN_WHITELIST = (
    'app.fieldsight.org',
    'kpi.fieldsight.org',
    'enketo.fieldsight.org',
    'localhost:8001',
    '127.0.0.1:8000'
)

TIME_ZONE = 'Asia/Kathmandu'

CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "asgi_redis.RedisChannelLayer",
        "CONFIG": {
            "hosts": [("localhost", 6379)],
        },
        "ROUTING": "onadata.apps.fieldsight.routing.channel_routing",
    },
}

#WEBSOCKET_URL = "app.fieldsight.org/fs-channel"
#WEBSOCKET_PORT = ""

WEBSOCKET_URL = "wss://app.fieldsight.org"
WEBSOCKET_PORT = False


#from onadata.settings.common import REST_FRAMEWORK
KPI_URL = 'https://kpi.fieldsight.org/'
KPI_LOGOUT_URL = KPI_URL + 'accounts/logout/'
KPI_ASSET_URL = KPI_URL + 'assets/'

#REST_FRAMEWORK.update({'DEFAULT_PERMISSION_CLASSES':['rest_framework.permissions.IsAuthenticated',]})
FILE_UPLOAD_HANDLERS = ("django_excel.ExcelMemoryFileUploadHandler",
                        "django_excel.TemporaryExcelFileUploadHandler")

#INSTALLED_APPS += ['debug_toolbar']

#DEBUG_TOOLBAR_CONFIG = {
#     'INTERCEPT_REDIRECTS': True
#}
SESSION_ENGINE = "django.contrib.sessions.backends.signed_cookies"
SECRET_KEY = '*********************'
SESSION_COOKIE_NAME = '*********************'
SESSION_COOKIE_DOMAIN = '*********************'
#CSRF_COOKIE_DOMAIN = '.fieldsight.org'
DEFAULT_DEPLOYMENT_BACKEND = 'kobocat'
BROKER_URL = 'amqp://guest:guest@localhost:5672//'
ADMINS = []

#ENKETO_URL = "http://enketo.fieldsight.org/"
ENKETO_PROTOCOL = 'https'
ENKETO_API_ENDPOINT_SURVEYS = '/survey'
ENKETO_URL = os.environ.get('ENKETO_URL', 'https://enketo.fieldsight.org')


#os.environ["ENKETO_API_TOKEN"] = 'hellofield'


BROKER_BACKEND = "redis"
CELERY_RESULT_BACKEND = "redis"  # telling Celery to report results to RabbitMQ
#CELERY_ALWAYS_EAGER = True
BROKER_URL = 'redis://localhost:6379/1'
REDIS_HOST = "localhost"
CELERY_BROKER_URL = BROKER_URL
CELERY_RESULT_BACKEND = BROKER_URL


AWS_ACCESS_KEY_ID = "*********************"
AWS_SECRET_ACCESS_KEY = "*********************"
AWS_STORAGE_BUCKET_NAME = "*********************"
AWS_DEFAULT_ACL = '*********************'
DEFAULT_FILE_STORAGE = '*********************'
AWS_S3_REGION_NAME = '*********************'
AWS_QUERYSTRING_AUTH = False
AWS_S3_FILE_OVERWRITE = False

#DEBUG = False

#STATIC_ROOT = "/srv/fieldsight/fieldsight-kobocat/onadata/static'"
#STATICFILES_DIRS = (
 #   os.path.join(ONADATA_DIR, "static"),
#)
DEBUG = False
STATIC_URL = '/static/'
STATIC_ROOT= os.path.join(BASE_DIR,'static')
SITE_URL = 'https://app.fieldsight.org'

# ........STRIPE CONFIG...............

STRIPE_SECRET_KEY = '*********************'
STRIPE_PUBLISHABLE_KEY = '*********************'

#stripe.verify_ssl_certs = False


MONTHLY_PLANS = {
         'free_plan': 'free',
         'starter_plan': '*********************',
         'basic_plan': '*********************',
         'extended_plan': '*********************',
         'pro_plan': '*********************',
         'scale_plan': '*********************'
        }


MONTHLY_PLANS_OVERRAGE = {
         'free_plan': 'free',
         'starter_plan': '*********************',
         'basic_plan': '*********************',
         'extended_plan': '*********************',
         'pro_plan': '*********************',
         'scale_plan': '*********************'
        }

YEARLY_PLANS = {
         'free_plan': 'free',
         'starter_plan': '*********************',
         'basic_plan': '*********************',
         'extended_plan': '*********************',
         'pro_plan': '*********************',
         'scale_plan': '*********************'
        }

YEARLY_PLANS_OVERRAGE = {
         'free_plan': 'free',
         'starter_plan': '*********************',
         'basic_plan': '*********************',
         'extended_plan': '*********************',
         'pro_plan': '*********************',
         'scale_plan': '*********************'
        }


PLANS = {
    'free': 0,                 # free
    '********************': 1,  # basic monthly plan
    '*******************': 2,  # basic yearly plan
    '******************': 3,  # extended monthly plan
    '*****************': 4,  # extended yearly plan
    '****************': 5,  # pro monthly plan
    '**************': 6,  # pro yearly plan
    '*************': 7,  # scale monthly plan
    '************': 8,  # scale yearly plan
    '***********': 9,  # starter monthly plan
    '*********': 10  # starter yearly plan



}
# ..............END STRIPE CONFIG..............


DEFAULT_FORM_2 = {
    'id_string': 'atYfmSxxyCZhKb7gDHU4wt',
    'name': 'Daily Site Diary - Default Form',
    'type':'schedule '
}

DEFAULT_FORM_1 = {
    'id_string': 'ahLRXcGG23uNkKYCm6empb',
    'name': 'Health, Safety, Social and Environmental Inspection Report - Default Form',
    'type':'schedule '
}
DEFAULT_FORM_3 = {
    'id_string': 'azmvMmr4dP9Fyo8rVt654G',
    'name': 'Incident Report',
    'type':'general'

}
