# TODO, figure out how to load gevent monkey patch cleanly in production
# try:
#     from gevent.monkey import patch_all
#     patch_all()
# except ImportError:
#     print "unable to apply gevent monkey.patch_all"

import os

from werkzeug.contrib.fixers import ProxyFix

from app import app as application

if os.environ.get('SENTRY_DSN'):
    from raven.contrib.flask import Sentry
    sentry = Sentry()
    sentry.init_app(application)

application.wsgi_app = ProxyFix(application.wsgi_app)
