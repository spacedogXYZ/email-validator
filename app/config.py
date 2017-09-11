import os

DEBUG = os.environ.get('DEBUG', False)
REDIS_URL = os.environ.get('REDIS_URL', 'redis://localhost:6379/')
RQ_REDIS_URL = REDIS_URL
DNS_TIMEOUT = os.environ.get('DNS_TIMEOUT', 2)  # originally 5.2
