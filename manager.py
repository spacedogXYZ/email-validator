from flask.ext.script import Manager
from app import app
import flanker
import sys

manager = Manager(app)


@manager.option('-f', '--filename', dest='filename', default=None)
def warm_cache(filename):
    if(not(filename) or filename == '-'):
        f = sys.stdin
    else:
        f = open(filename)
    print "warm mx cache", f.name

    for domain in f:
        mx = flanker.addresslib.validate.mail_exchanger_lookup(domain, metrics=False)
        print domain, mx
    print "done"

if __name__ == "__main__":
    manager.run()
