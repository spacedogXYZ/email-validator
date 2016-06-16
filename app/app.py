from flask import Flask, make_response, render_template, jsonify, request
from views import address
from mxcache import MxCache
from metrics import Metrics

app = Flask(__name__)
app.config.from_object('app.config')
app.register_blueprint(address)
mxcache = MxCache(app)
metrics = Metrics(app)


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
    seconds = request.values.get('seconds', 60*5)  # default to last 5 minutes of stats
    data = metrics.get(seconds=int(seconds))
    return jsonify(data)


@app.route('/metrics')
def metrics_graph():
    return render_template('metrics.html')
