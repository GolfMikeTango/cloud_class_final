from flask import Flask, Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_user, login_required, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
from .db_models import User
from . import db

auth = Blueprint('auth', __name__)

@auth.route('/login')
def login():
    return render_template('login.html')

@auth.route('/login', methods=['POST'])
def login_post():
    username = request.form.get('username')
    email = request.form.get('email')
    password = request.form.get('password')
    remember = True if request.form.get('remember') else False

    #get user and check PW hashses. if either fail, kick em back to login screen, otherwise log them in and go to profile
    user = User.query.filter_by(username=username).first()
    if not user or not check_password_hash(user.password, password):
        flash("Wrong username or password, check credentials and try again")
        return redirect(url_for('auth.login'))

    login_user(user, remember=remember)
    return redirect(url_for('flaskapp.profile'))

@auth.route('/signup')
def signup():
    return render_template('signup.html')

@auth.route('/signup', methods=['POST'])
def signup_post():
    #gets user fields from form
    username = request.form.get('username')
    email = request.form.get('email')
    first_name = request.form.get('first_name')
    last_name = request.form.get('last_name')
    password = request.form.get('password')

    #query DB for a user and return to signup page if exists
    user = User.query.filter_by(username=username).first()

    if user:
        flash('User already exists!')
        return redirect(url_for('auth.signup'))

    #Create a new user instance of user db model
    new_user = User(username=username, email=email, first_name=first_name, last_name=last_name, password=generate_password_hash(password, method='sha256'))

    #write to db
    db.session.add(new_user)
    db.session.commit()

    #redirect to login
    return redirect(url_for('auth.login'))

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('flaskapp.index'))