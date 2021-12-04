from datetime import datetime
from flask import render_template, redirect, url_for, flash
from flask_security import login_required, roles_accepted, login_user, logout_user
from flask_modals import render_template_modal
from flask_babelex import _
from app import app, db
from app.forms import LoginForm, RegistrationForm
from app.models import Barista


@app.route('/')
@app.route('/index', methods=("POST", "GET"))
@login_required
def home():
    return render_template_modal('index.html', modal='modal-form')


@app.route('/login', methods=('GET', 'POST'))
def login():
    form = LoginForm()
    app.logger.info(form.validate_on_submit())
    if form.validate_on_submit():
        user = Barista.query.filter_by(name=form.name.data).first()
        if user is None:
            flash(_('Неправильное имя либо пароль'))
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        return redirect(url_for('home'))
    return render_template('auth/login.html', title='Sign In', form=form)


@app.route('/new_staff', methods=('GET', 'POST'))
@login_required
@roles_accepted('admin', 'moderator')
def create_new_staff():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = Barista(
            name=form.name.data,
            phone_number=form.phone_number.data,
            email=form.email.data,
            password=form.password.data,
            confirmed_at=datetime.now(),
            active=True
        )
        db.session.add(user)
        db.session.commit()
        flash(_('Вы добавили нового ссотрудника!'))
        return redirect(url_for('home'))
    return render_template('auth/new_staff.html', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))
