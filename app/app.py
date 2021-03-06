from flask import Flask, make_response, render_template, jsonify, request
from logger import configure_logging

from mxcache import MxCache
from metrics import Metrics
from flask_mail import Mail

app = Flask('app')
app.config.from_object('app.config')
configure_logging(app.config.get('DEBUG'))

mxcache = MxCache(app)
metrics = Metrics(app)
mail = Mail(app)

from flask_rq2 import RQ
RQ_ASYNC = 'REDIS_URL' in app.config.keys()
RQ_TIMEOUT = app.config.get('RQ_TIMEOUT', 180)
rq = RQ(async=RQ_ASYNC, default_timeout=RQ_TIMEOUT)
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


@app.route('/test/credo')
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
