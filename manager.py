import sys
import logging
log = logging.getLogger(__name__)

from app.app import app, rq
from app import jobs

from flask_script import Manager
from flask_rq2.script import RQManager

manager = Manager(app)
manager.add_command('rq', RQManager(rq))


@manager.option('-f', '--filename', dest='filename', default=None)
def warm_cache(filename):
    import flanker

    if filename:
        if filename == '-':
            f = sys.stdin
        else:
            f = open(filename)
        log.info("flanker warmup mx cache {}".format(f.name))

        for domain in f:
            mx = flanker.addresslib.validate.mail_exchanger_lookup(domain, metrics=False)
            log.info('{}, {}'.format(domain, mx))
    else:
        log.info("flanker warmup, no filename specified")


@manager.command
def queue_nightly_tasks():
    log.info("queue_nightly_tasks")
    jobs.validate_new_emails.queue()
    jobs.validate_old_emails.queue()

if __name__ == "__main__":
    manager.run()
