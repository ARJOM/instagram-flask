import base64

from datetime import date

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

# Core
# - - - - - - - - - - - - - - - - - - -

@app.route('/')
def index():
    session['username'] = None
    return render_template('home.html')


@app.route('/logout')
def logout():
    return redirect(url_for('index'))


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


# App
# - - - - - - - - - - - - - - - - - - - -

@app.route('/feed', methods=['GET'])
def feed():
    username = session['username'][0]

    cur = g.db.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute(f"SELECT * FROM photos "
                f"WHERE username IN (SELECT followed FROM followers WHERE follower='{username}') "
                f"OR username='{username}'")
    posts = cur.fetchall()

    return render_template('feed.html', username=session['username'], posts=posts)


@app.route('/post/new', methods=['GET', 'POST'])
def upload_file():
    if session['username'] is None:
        return redirect(url_for('feed'))

    if request.method == 'POST':
        now = date.today()
        cur = g.db.cursor(cursor_factory=psycopg2.extras.DictCursor)
        file = request.files['file']
        if file is None:
            return redirect('feed')
        photo = base64.b64encode(file.read()).decode('utf-8').replace('\n', '')
        username = session['username'][0]
        description = request.form['description']
        cur.execute(f"INSERT INTO photos(published_date, description, username, photo)"
                    f"VALUES ('{now}','{description}', '{username}', '{photo}')")
        g.db.commit()
        cur.close()
        return redirect(url_for('feed'))
    return render_template('form.html')


@app.route('/like/<int:pk>')
def like(pk):
    if session['username'] is not None:
        username = session['username'][0]
        try:
            cur = g.db.cursor(cursor_factory=psycopg2.extras.DictCursor)
            cur.execute(f"INSERT INTO likes(username, photo) VALUES ('{username}',{pk})")
            g.db.commit()
            cur.close()
        except:
            pass
    return redirect(url_for('feed'))


@app.route('/delete/<int:pk>')
def delete(pk):
    username = session['username'][0]

    cur = g.db.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute(f"SELECT username FROM photos "
                f"WHERE username='{username}'")
    post = cur.fetchone()

    if session['username'] is not None and session['username'][0] == post[0]:
        cur.execute(f"DELETE FROM likes WHERE photo={pk}")
        cur.execute(f"DELETE FROM photos WHERE id={pk}")
        g.db.commit()
        cur.close()

    return redirect(url_for('feed'))


@app.route('/post/<int:pk>', methods=['GET'])
def detail(pk):
    cur = g.db.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute(f"SELECT * FROM photos WHERE id={pk}")
    post = cur.fetchone()

    cur.execute(f"SELECT * FROM comments WHERE photo={pk}")
    comments = cur.fetchall()

    return render_template("detail.html", post=post, comments=comments)
