from flask import Flask, make_response, render_template, jsonify, request
from mxcache import MxCache
from metrics import Metrics
from flask_rq2 import RQ

import logging

app = Flask('mailvalidate')
app.config.from_object('app.config')
# setup logging before further config
if app.config.get('DEBUG'):
    loglevel = logging.INFO
else:
    loglevel = logging.ERROR
logging.basicConfig(level=loglevel)


mxcache = MxCache(app)
metrics = Metrics(app)

RQ_ASYNC = app.config.get('RQ_ASYNC', False)
rq = RQ(async=RQ_ASYNC)
rq.app_worker_path = 'app.worker_preload'
rq.init_app(app)

from views import address
app.register_blueprint(address)

@app.route('/')
def index():
    return make_response('ok')


@app.route('/test')
def test_form():
    return render_template('form.html')


@app.route('/test-credo')
def test_credo():
    return render_template('credo-form.html')


@app.route('/data/metrics.json')
def metrics_json():
    minutes = request.values.get('minutes', 60)  # default to last hour of stats
    data = metrics.get_latest(minutes=int(minutes))
    return jsonify(data)


@app.route('/metrics')
def metrics_graph():
    return render_template('metrics.html')
