import os
from pathlib import Path
import logging.config

BASE_DIR = Path(__file__).parent.parent

LOG_LEVEL = "DEBUG"

os.makedirs(os.path.join(BASE_DIR, 'log'), exist_ok=True)

# Logging setting
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s %(process)d-%(thread)d:%(lineno)s:%(message)s'
        },
        'main': {
            'datefmt': '%Y-%m-%d %H:%M:%S',
            'format': '%(asctime)s [%(module)s %(levelname)s %(lineno)s] %(message)s',
        },
        'simple': {
            'format': '%(levelname)s %(lineno)s %(message)s'
        },
    },
    'handlers': {
        'null': {
            'level': 'DEBUG',
            'class': 'logging.NullHandler',
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'formatter': 'main',
            'filename': os.path.join(BASE_DIR, 'log', 'package.log'),
            'encoding': 'utf-8',
        },
        'all': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'formatter': 'main',
            'filename': os.path.join(BASE_DIR, 'log', 'all.log'),
            'encoding': 'utf-8',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['null'],
            'propagate': False,
            'level': LOG_LEVEL,
        },
        'django.request': {
            'handlers': ['console', 'file'],
            'level': LOG_LEVEL,
            'propagate': False,
        },
        'package': {
            'handlers': ['console', 'file'],
            'level': LOG_LEVEL,
            'propagate': False,
        },
        '': {
            'handlers': ['console', 'all'],
            'level': LOG_LEVEL,
            'propagate': False,
        }
    }
}

logging.config.dictConfig(LOGGING)
