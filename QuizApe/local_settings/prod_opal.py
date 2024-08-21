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

# Fix for OpalStack's lack of a current version of sqlite3
# https://docs.opalstack.com/topic-guides/django/#using-databases-with-django

__import__('pysqlite3')
import sys
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')
