import os

os.environ["DJANGO_SECRET_KEY"] = "@25)**hc^rjaiagb4#&q*84hr*uscsxwr-cv#0joiwj$))obyk"
os.environ["KOBOCAT_MONGO_HOST"] = "localhost"

from onadata.settings.kc_environ import *

DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': 'kobocat1',
        'USER': 'postgres',
        'PASSWORD': 'password',
        'HOST': '',
        'PORT': '',
    }
}

INSTALLED_APPS = list(INSTALLED_APPS)

INSTALLED_APPS += ['debug_toolbar']

# DEBUG_TOOLBAR_CONFIG = {
#     'INTERCEPT_REDIRECTS': True
# }

SESSION_ENGINE = "django.contrib.sessions.backends.signed_cookies"
SECRET_KEY = '@25)**hc^rjaiagb4#&q*84hr*uscsxwr-cv#0joiwj$))obyk'
SESSION_COOKIE_NAME = 'kobo_cookie'
SESSION_COOKIE_DOMAIN = 'localhost'
