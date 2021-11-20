from flask import Blueprint, render_template, redirect, url_for, request, flash
from werkzeug.security import check_password_hash, generate_password_hash

from . import db
from flask_login import login_user, logout_user, login_required
from .models import User

auth = Blueprint('auth', __name__)


@auth.route('/login')
def login():
    return render_template('login.html')


@auth.route('/signup')
def signup():
    return render_template('signup.html')


@auth.route('/login', methods=['POST'])
def login_post():
    email = request.form.get('email')
    password = request.form.get('password')
    remember = True if request.form.get('remember') else False

    user = User.query.filter_by(email=email).first()

    if not user or not check_password_hash(user.password, password):
        flash('Please check your login details and try again.')
        return redirect(url_for('auth.login'))
    login_user(user, remember=remember)
    return redirect(url_for('main.index'))


@auth.route('/signup', methods=['POST'])
def signup_post():
    email = request.form.get('email')
    name = request.form.get('name')
    password = request.form.get('password')
    phone = request.form.get('phone')

    user = User.query.filter_by(
        email=email).first()

    valid = validate_user(password, phone, user)

    if not valid:
        return redirect(url_for('auth.signup'))

    new_user = User(email=email, name=name, phone=phone,
                    password=generate_password_hash(password, method='sha256'))

    db.session.add(new_user)
    db.session.commit()

    return redirect(url_for('auth.login'))


def validate_user(password, phone, user):
    valid = True

    if len(phone) != 10:
        flash('Phone number must be ten characters')
        valid = False

    if not phone.isdigit():
        flash('Phone number must only be digits')
        valid = False

    if user:
        flash('Email address already exists')
        valid = False
    # User must provide a password with
    # - a minimum length of 8
    if len(password) < 8:
        flash('Password must be at least eight characters')
        valid = False
    # - contain
    #   - at least one capital letter,
    for c in password:
        if c.isupper():
            break
    else:
        flash("Password must contain at least one capital letter")
        valid = False
    #   - one special character,
    for c in password:
        if not c.isalnum():
            break
    else:
        flash("Password must contain at least one special character")
        valid = False
    #   - number,
    for c in password:
        if c.isdigit():
            break
    else:
        flash("Password must contain at least one digit")
        valid = False
    #   - and lowercase letter to register.
    for c in password:
        if c.islower():
            break
    else:
        flash("Password must contain at least one lowercase letter")
        valid = False
    return valid


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))
