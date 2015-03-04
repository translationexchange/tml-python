# encoding: UTF-8
from tml import configure, tr, Error
from flask import Flask, render_template, request
from json import loads

app = Flask(__name__)

@app.route('/')
def index():
    """ Index page """
    return render_template('index.html')

@app.route('/translate', methods = ['POST'])
def translate():
    data = {}

    for key in ['token', 'locale', 'label', 'description', 'data']:
        data[key] = request.values.get(key)
    handle = None
    try:
        data['args'] = loads(data['data'].encode('utf-8')) if len(data['data']) else {}
        configure(token = data['token'], locale = data['locale'])
        data['result'] = tr(data['label'], data['args'], data['description'])
    except handle as e:
        data['error_class'] = e.__class__.__name__
        data['error'] = str(e)
    return render_template('index.html', **data)

if __name__ == '__main__':
    app.run(debug = True)

