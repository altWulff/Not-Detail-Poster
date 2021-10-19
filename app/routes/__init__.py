from datetime import datetime, date
from flask import render_template, redirect, url_for, flash, Blueprint, request
from flask_security import login_required, login_user, logout_user, current_user, roles_required
from app import app, db, login
from app.forms import LoginForm, RegistrationForm, CoffeeShopForm, ExpanseForm, ByWeightForm, WriteOffForm, SupplyForm, ReportForm, TransferForm
from app.models import Barista, CoffeeShop, Warehouse, CoffeeShopEquipment, DailyReport, Expense, Supply, ByWeight, WriteOff



@app.context_processor
def inject_form():
    expense_form, by_weight_form, write_off_form = ExpanseForm(), ByWeightForm(), WriteOffForm()
    supply_form, transfer_form = SupplyForm(), TransferForm()
    coffee_shop_list = CoffeeShop.query.all()
    warehouse = Warehouse
    cs_equip = CoffeeShopEquipment
    return dict(expense_form=expense_form, by_weight_form=by_weight_form,
                write_off_form=write_off_form, supply_form=supply_form, transfer_form=transfer_form,
                coffee_shop_list=coffee_shop_list, warehouse=warehouse, cs_equip=cs_equip)



@app.route('/')
@app.route('/index', methods=["POST", "GET"])
@login_required
def home():
    return render_template('index.html')


@app.route('/statistics')
@roles_required('admin')
@login_required
def statistics():
    return render_template('statistics.html')


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
def logout():
    logout_user()
    return redirect('index')
