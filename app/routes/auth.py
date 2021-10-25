from datetime import datetime
from flask import render_template, redirect, url_for, flash
from flask_security import login_required, login_user, logout_user, roles_required
from app import app, db
from app.forms import LoginForm, RegistrationForm, ExpanseForm, ByWeightForm, WriteOffForm, SupplyForm, TransferForm
from app.models import Barista, CoffeeShop, Warehouse, CoffeeShopEquipment


@app.route('/')
@app.route('/index', methods=["POST", "GET"])
@login_required
def home():
    return render_template('index.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    app.logger.info(form.validate_on_submit())
    if form.validate_on_submit():
        user = Barista.query.filter_by(name=form.name.data).first()
        if user is None:
            flash('Invalid name, phone number or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        return redirect('index')
    return render_template('auth/login.html', title='Sign In', form=form)


@app.route('/new_staff', methods=['GET', 'POST'])
@login_required
def create_new_staff():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = Barista(name=form.name.data,
                       phone_number=form.phone_number.data,
                       email=form.email.data)
        user.set_password(form.password.data)
        user.confirmed_at = datetime.utcnow()
        user.active = True
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('auth/new_staff.html', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect('index')