from __future__ import absolute_import
# encoding: UTF-8
from tml import configure, tr, Error
from flask import Flask, render_template, request, make_response
from json import loads, dumps
import re
DEBUG = True

IS_JSON = re.compile('application/json')
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

    data['args'] = loads(data['data'].encode('utf-8')) if len(data['data']) else {}
    configure(token = data['token'], locale = data['locale'])
    data['result'] = tr(data['label'], data['args'], data['description'])

    if IS_JSON.match(request.headers['Accept']):
        if 'result' in data:
            return make_response(dumps({'result': data['result']}))

    return render_template('index.html', **data)

if __name__ == '__main__':
    app.run(debug = True)

