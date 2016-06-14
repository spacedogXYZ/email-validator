import flanker.addresslib
import urlparse


def config_cache(app):
    if 'REDIS_URL' in app.config:
        redis_url = urlparse.urlsplit(app.config.get('REDIS_URL'))
        cache = flanker.addresslib.drivers.redis_driver.RedisCache(
            host=redis_url.hostname, port=redis_url.port)
    else:
        cache = {}

    flanker.addresslib.set_mx_cache(cache)
    return cache
