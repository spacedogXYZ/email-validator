import flanker.addresslib
import redis
import collections
import dnsq


class MxCache(object):
    def __init__(self, app=None):
        self.app = app
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        if 'REDIS_URL' in app.config:
            cache = flanker.addresslib.drivers.redis_driver.RedisCache()
            cache.r = redis.StrictRedis.from_url(app.config.get('REDIS_URL'))
        else:
            cache = collections.defaultdict(dict)

        self._cache = cache

        # cache mail server responses
        flanker.addresslib.set_mx_cache(self._cache)

        # set custom DNS timeout
        dnsq.DNS_LIFETIME_TIMEOUT_SECONDS = app.config.get('DNS_TIMEOUT')

        app.mxcache = self

    def redis_conn(self):
        if hasattr(self._cache, 'r'):
            return self._cache.r
        else:
            return self._cache
