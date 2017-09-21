import logging

class NoFlankerParsingFilter(logging.Filter):
    def filter(self, record):
        return not record.name == 'flanker.addresslib.parser'

def configure_logging(debug):
    if debug:
        loglevel = logging.DEBUG
    else:
        loglevel = logging.WARNING
    logging.basicConfig(level=loglevel)

    # suppress flankers super verbose parser logs
    # first line should work
    logging.getLogger('flanker.addresslib.parser').setLevel(logging.CRITICAL+1)
    # but it doesn't so filter on the handlers

    for handler in logging.root.handlers:
        handler.addFilter(NoFlankerParsingFilter())

    log = logging.getLogger(__name__)
    log.warning('flanker.addresslib.parser compilation warnings suppressed')
