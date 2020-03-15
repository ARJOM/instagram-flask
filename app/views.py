from flask import g

import psycopg2.extras

from app import app


# ~~~~
@app.before_request
def before_request():
    g.db = psycopg2.connect('dbname=instagram user=flask password=flask host=127.0.0.1')


@app.teardown_request
def teardown_request(exception):
    g.db.close()


# ~~~~

@app.route('/')
def hello_world():
    return 'Hello World!'
