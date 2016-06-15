from flask import Flask, make_response, render_template
from views import address
from cache import config_cache
from metrics import Metrics

app = Flask(__name__)
app.config.from_object('app.config')
app.register_blueprint(address)
app.cache = config_cache(app)
metrics = Metrics(app)


@app.route('/')
def index():
    return make_response('ok')


@app.route('/test')
def test_form():
    return render_template('form.html')


@app.route('/metrics')
def graph_metrics():
    data = metrics.get()
    print data
    return render_template('graph_metrics.html', data=data)
