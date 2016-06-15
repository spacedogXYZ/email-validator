import flanker.addresslib
import urlparse
import dnsq


class MxCache(object):
    def __init__(self, app=None):
        self.app = app
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        if 'REDIS_URL' in app.config:
            redis_url = urlparse.urlsplit(app.config.get('REDIS_URL'))
            cache = flanker.addresslib.drivers.redis_driver.RedisCache(
                host=redis_url.hostname, port=redis_url.port)
        else:
            cache = {}

        self._cache = cache
        # cache mail server responses
        flanker.addresslib.set_mx_cache(self._cache)

        # set custom DNS timeout
        dnsq.DNS_LIFETIME_TIMEOUT_SECONDS = app.config.get('DNS_TIMEOUT')

        app.mxcache = self

    def redis_conn(self):
        return self._cache.r
