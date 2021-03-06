import os
from distutils.util import strtobool

DEBUG = strtobool(os.environ.get('DEBUG', False))
REDIS_URL = os.environ.get('REDIS_URL', 'redis://localhost:6379/')
RQ_REDIS_URL = REDIS_URL
RQ_QUEUES = ['high', 'low']
RQ_TIMEOUT = os.environ.get('RQ_TIMEOUT', 500)
DNS_TIMEOUT = os.environ.get('DNS_TIMEOUT', 2)  # originally 5.2
SENTRY_DSN = os.environ.get('SENTRY_DSN')

ADMIN_EMAILS = os.environ.get('ADMIN_EMAILS', 'info@spacedog.xyz,').split(',')
MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER', 'info@spacedog.xyz')
if 'SENDGRID_USERNAME' in os.environ:
    # smtp via sendgrid
    MAIL_SERVER = 'smtp.sendgrid.net'
    MAIL_PORT = 587
    MAIL_USERNAME = os.environ.get('SENDGRID_USERNAME')
    MAIL_PASSWORD = os.environ.get('SENDGRID_PASSWORD')
    MAIL_USE_TLS = True
else:
    MAIL_SERVER = os.environ.get('MAIL_SERVER', 'localhost')
    MAIL_PORT = os.environ.get('MAIL_PORT', 25)
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', False)
MAIL_DEBUG = DEBUG

ADMIN_WEBHOOK = os.environ.get('ADMIN_WEBHOOK', None)

ACCEPT_FLANKER_SUGGESTIONS = os.environ.get('ACCEPT_FLANKER_SUGGESTIONS', False)