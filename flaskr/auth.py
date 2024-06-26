import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash

from flaskr.db import get_db

bp = Blueprint('auth', __name__, url_prefix='/auth')

@bp.route('/register', methods=('GET', 'POST'))
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        verif_password = request.form['verif_password']
        
        
        db = get_db()
        error = None

        if not username:
            error = 'el usuario no coinciden..'    
        elif not password:
            error = 'la contraseña no coinciden.'
        elif  verif_password != password:
            error = 'Las contraseñas no coinciden.'   
        elif not email:
            error = 'error de mail'
        
        if error is None:
            try:
                db.execute(
                    "INSERT INTO user (username,email, password, verif_password) VALUES (?, ?, ?,?)",
                    (username , email, generate_password_hash(password), verif_password),
                )
                db.commit()
            except db.IntegrityError:
                error = f"User {username} is already registered."
            else:
                return redirect(url_for("auth.login"))

        flash(error)

    return render_template('auth/register.html')


@bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None
        user = db.execute(
            'SELECT * FROM user WHERE username = ?', (username,)
        ).fetchone()

        if user is None:
            error = 'Incorrect username.'
        elif not check_password_hash(user['password'], password):
            error = 'Incorrect password.'

        if error is None:
            session.clear()
            session['user_id'] = user['id']
            return redirect(url_for('index'))

        flash(error)

    return render_template('auth/login.html')


@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        g.user = get_db().execute(
            'SELECT * FROM user WHERE id = ?', (user_id,)
        ).fetchone()

@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))

        return view(**kwargs)

    return wrapped_view        
@bp.route('/updateemail', methods=('GET', 'POST'))
def updateemail():
    if request.method == 'POST':
        email = request.form['new_email']
        error = None
        db = get_db()
        if not email:
            error = 'Email is required.'

        if error is None:            
            db.execute(
                'UPDATE user SET email = ? WHERE id = ?',
                (email, g.user['id'])
            )
            db.commit()
            return redirect(url_for('index'))
        else:
            flash(error)

    return render_template('auth/updateemail.html')

@bp.route('/deleteUser', methods=('GET', 'POST'))
def deleteUser():
    if request.method == 'POST':
        error = None
        db = get_db()
        
        if error is None:            
            db.execute(
                'DELETE FROM user  WHERE id = ?',
                (g.user['id'],)
            )
            db.commit()
            return redirect(url_for('index'))
        else:
             flash(error)

    return render_template('auth/updateemail.html')