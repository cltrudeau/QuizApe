DEBUG = False
ALLOWED_HOSTS = ['qape.arsensa.com', ]

CSRF_TRUSTED_ORIGINS = ['https://qape.arsensa.com', 'http://qape.arsensa.com']

HOST_PREFIX = 'https://qape.arsensa.com'

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
