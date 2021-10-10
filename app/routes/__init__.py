from datetime import datetime
from flask import render_template, redirect, url_for, flash, Blueprint, request
from flask_security import login_required, login_user, logout_user, current_user, roles_required
from app import app, db, login
from app.forms import LoginForm, RegistrationForm, CoffeeShopForm, ExpanseForm, ByWeightForm, WriteOffForm, SupplyForm, ReportForm
from app.models import Barista, CoffeeShop, Warehouse, CoffeeShopEquipment, DailyReport, Expense, Supply, ByWeight, WriteOff


@app.context_processor
def inject_form():
    expense_form, by_weight_form, write_off_form, supply_form = ExpanseForm(), ByWeightForm(), WriteOffForm(), SupplyForm()
    coffee_shop_list = CoffeeShop.query.all()
    warehouse = Warehouse
    cs_equip = CoffeeShopEquipment
    return dict(expense_form=expense_form, by_weight_form=by_weight_form,
                write_off_form=write_off_form, supply_form=supply_form,
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
