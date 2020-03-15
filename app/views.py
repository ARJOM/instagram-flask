from flask import g, session, render_template

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
def index():
    session['username'] = None
    return render_template('home.html')


@app.route('/register', methods=['GET', 'POST'])
def sign_up():
    pass


@app.route('/login', methods=['GET', 'POST'])
def login():
    pass
