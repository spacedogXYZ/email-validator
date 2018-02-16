#!/usr/bin/env python
import sys, os
from rq import Connection, Worker

# Preload expensive libraries
import flanker.addresslib.address

# ensure worker can send exceptions via Sentry
from raven import Client
from raven.transport import HTTPTransport
from rq.contrib.sentry import register_sentry

class SentryAwareWorker(rq.Worker):
    def __init__(self, *args, **kwargs):
        super(SentryAwareWorker, self).__init__(*args, **kwargs)
        dsn = os.environ.get('SENTRY_DSN')
        client = Client(dsn, transport=HTTPTransport)
        register_sentry(client, self)

# Provide queue names to listen to as arguments to this script,
# similar to rq worker
with Connection():
    qs = sys.argv[1:] or ['default']

    w = SentryAwareWorker(qs)
    w.work()

