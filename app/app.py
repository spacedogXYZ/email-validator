from flask import Flask, make_response, render_template
from views import address

app = Flask(__name__)
app.config.from_object('app.config')
app.register_blueprint(address)


@app.route('/')
def index():
    return make_response('ok')


@app.route('/test')
def test_form():
    return render_template('form.html')
