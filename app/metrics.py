from redistimeseries import RedisTimeSeries
import time

MX_FIELDS = ['dns_lookup', 'mx_lookup', 'mx_conn', 'custom_grammar', 'parsing']


class Metrics(object):
    def __init__(self, app=None):
        self.app = app
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        for f in MX_FIELDS:
            setattr(self, f, RedisTimeSeries(f, 1, app.mxcache.redis_conn()))
        app.metrics = self

    def update(self, metrics):
        for f in MX_FIELDS:
            m = getattr(self, f)
            m.add(str(metrics[f]))

    def get(self, seconds=60*5):
        timeseries = {}
        now = float(time.time())
        for f in MX_FIELDS:
            timeseries[f] = []
            m = getattr(self, f)
            for r in m.fetch_range(now - seconds, now):
                timeseries[f].append({'time': r["time"], 'data': r["data"]})
        return timeseries
