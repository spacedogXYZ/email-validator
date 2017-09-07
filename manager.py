import sys
import logging
# suppress some of flankers verbose parser logs
logging.getLogger("flanker.addresslib.parser").setLevel(logging.ERROR)

from flask.ext.script import Manager
from flask_rq2.script import RQManager

from app.app import app, rq
from app import jobs

manager = Manager(app)
manager.add_command('rq', RQManager(rq))

log = logging.getLogger(__name__)

@manager.option('-f', '--filename', dest='filename', default=None)
def warm_cache(filename):
    import flanker

    if(not(filename) or filename == '-'):
        f = sys.stdin
    else:
        f = open(filename)
    log.info("warm mx cache {}".format(f.name))

    for domain in f:
        mx = flanker.addresslib.validate.mail_exchanger_lookup(domain, metrics=False)
        log.info('{}, {}'.format(domain, mx))


@manager.command
def queue_nightly_tasks():
    jobs.validate_new_emails.queue()
    # jobs.validate_old_emails.queue()

if __name__ == "__main__":
    manager.run()
