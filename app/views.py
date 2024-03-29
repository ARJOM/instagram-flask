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

        cur.close()
        # Checking result
        if user is not None:
            session['username'] = user
            return redirect(url_for('feed'))
        return render_template('login.html', error='USUARIO NÂO EXISTE')
    return render_template('login.html')


# Photos
# - - - - - - - - - - - - - - - - - - - -

@app.route('/feed', methods=['GET'])
def feed():
    username = session['username'][0]

    cur = g.db.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute(f"SELECT * FROM photoinfo "
                f"WHERE username IN (SELECT followed FROM followers WHERE follower='{username}') "
                f"OR username='{username}'")
    posts = cur.fetchall()
    cur.close()

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

        cur = g.db.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cur.execute(f"SELECT * FROM likes WHERE username='{username}' AND photo={pk}")
        like = cur.fetchone()

        if like is None:
            cur.execute(f"INSERT INTO likes(username, photo) VALUES ('{username}',{pk})")
            g.db.commit()
        else:
            cur.execute(f"DELETE FROM likes WHERE username='{username}' AND photo={pk}")
            g.db.commit()

        cur.close()

    return redirect(url_for('feed'))


@app.route('/delete/<int:pk>')
def delete(pk):
    if session['username'] is not None:
        username = session['username'][0]

        cur = g.db.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cur.execute(f"SELECT username FROM photos "
                    f"WHERE id={pk} AND username='{username}'")
        post = cur.fetchone()

        if post is not None:
            cur.execute(f"DELETE FROM likes WHERE photo={pk}")
            cur.execute(f"DELETE FROM photos WHERE id={pk}")
            g.db.commit()

        cur.close()

    return redirect(url_for('feed'))


@app.route('/post/<int:pk>', methods=['GET'])
def detail(pk):
    cur = g.db.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute(f"SELECT * FROM photoinfo WHERE id={pk}")
    post = cur.fetchone()

    cur.execute(f"SELECT * FROM comments WHERE photo={pk}")
    comments = cur.fetchall()

    cur.close()

    return render_template("detail.html", post=post, comments=comments)


# Users
# - - - - - - - - - - - - - - - - - - - -

def is_followed(followed):
    cur = g.db.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute(f"SELECT * FROM followers WHERE followed='{followed}' AND follower='{session['username'][0]}'")
    f = cur.fetchone()
    if f is None:
        return False
    return True


@app.route('/profile/<string:username>', methods=['GET'])
def profile(username):
    if session['username'] is None:
        return redirect(url_for('index'))
    elif username == "":
        username = session['username']

    cur = g.db.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute(f"SELECT username, name FROM users WHERE username='{username}'")
    user = cur.fetchone()
    if user is not None:
        cur.execute(f"SELECT count(*) as value FROM followers WHERE followed='{username}'")
        followers = cur.fetchone()
        cur.execute(f"SELECT count(*) as value FROM followers WHERE follower='{username}'")
        following = cur.fetchone()

        cur.execute(f"SELECT * FROM photoinfo WHERE username='{username}'")
        posts = cur.fetchall()

        f = is_followed(username)

        cur.close()

        return render_template("profile.html", user=user, followers=followers, following=following, posts=posts, follow=f)
    return render_template("profile.html", error="Usuário não cadastrado")


@app.route('/follow/<string:username>', methods=['GET'])
def follow(username):
    follower = session['username'][0]
    if not is_followed(username):
        cur = g.db.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cur.execute(f"INSERT INTO followers(follower, followed) VALUES ('{follower}','{username}')")
        g.db.commit()
        cur.close()
    return redirect(url_for('profile', username=username))


@app.route('/unfollow/<string:username>', methods=['GET'])
def unfollow(username):
    follower = session['username'][0]
    if is_followed(username):
        cur = g.db.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cur.execute(f"DELETE FROM followers WHERE follower='{follower}' AND followed='{username}'")
        g.db.commit()
        cur.close()
    return redirect(url_for('profile', username=username))
