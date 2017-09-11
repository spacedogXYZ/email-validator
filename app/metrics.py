import warnings
with warnings.catch_warnings():
    warnings.simplefilter('ignore', UserWarning)
    from kairos import Timeseries
    # ignore undefined backend warnings

from collections import defaultdict
import time


MX_FIELDS = ['dns_lookup', 'mx_lookup', 'mx_conn', 'custom_grammar', 'parsing']


class Metrics(object):
    def __init__(self, app=None):
        self.app = app
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        self.t = Timeseries(app.mxcache.redis_conn(),
           type='series', read_func=float, intervals={
                'minute': {
                    'step': 60,         # 60 seconds
                    'steps': 12 * 60,   # last 12 hours
                }
            })
        app.metrics = self

    def update(self, metrics):
        for f in MX_FIELDS:
            try:
                self.t.insert(f, metrics[f])
            except AttributeError:
                # default cache does not allow append
                pass

    def get_latest(self, minutes=5):
        now = float(time.time())
        joined_data = {}
        for f in MX_FIELDS:
            series_data = self.t.series(f, 'minute', start=now - minutes * 60, end=now)
            joined_data[f] = series_data
        return joined_data
