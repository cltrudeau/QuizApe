# OpalStack has an older version of sqlite3 (3.30), Django 5.1 expects 3.31
# => use Django 5.0 release!!!
#
# If they ever get around to updating, see:
#
# https://docs.opalstack.com/topic-guides/django/#using-databases-with-django
#

DEBUG = False
ALLOWED_HOSTS = ['survey.arsensa.com', ]

CSRF_TRUSTED_ORIGINS = [
    'https://survey.arsensa.com', 'http://survey.arsensa.com'
]

HOST_PREFIX = 'https://survey.arsensa.com'

LOGGING = {
    'version':1,
    'disable_existing_loggers':False,
    'handlers': {
        'console':{
            'class':'logging.StreamHandler',
        },
    },
    'loggers':{
        'django':{
            'handlers':['console', ],
            'level':'ERROR',
            'propagate':False,
        },
    },
}
