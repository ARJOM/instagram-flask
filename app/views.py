from flask import g, session, render_template, request, redirect, url_for

import hashlib

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
    if request.method == 'POST':
        # Getting form information
        name = request.form['name']
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        # Encrypting password
        hash_object = hashlib.md5(password.encode())
        password = hash_object.hexdigest()

        try:
            # Executing query
            cur = g.db.cursor(cursor_factory=psycopg2.extras.DictCursor)
            cur.execute(f"INSERT INTO users(name, username, email, password) "
                    f"VALUES ('{name}','{username}','{email}','{password}')")
            g.db.commit()
            cur.close()

            # Authenticating user
            session['username'] = username
            return redirect(url_for('feed'))
        except:
            return render_template('signup.html', error="ERRO AO CADASTRAR")

    return render_template('signup.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Getting form information
        username = request.form['username']
        password = request.form['password']

        # Encrypting password
        hash_object = hashlib.md5(password.encode())
        password = hash_object.hexdigest()

        # Executing query
        cur = g.db.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cur.execute(f"SELECT username FROM users WHERE username='{username}' AND password='{password}'")
        user = cur.fetchone()

        # Checking result
        if user is not None:
            session['username'] = user
            return redirect(url_for('feed'))
        return render_template('login.html', error='USUARIO NÂO EXISTE')
    return render_template('login.html')
