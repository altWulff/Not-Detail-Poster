from datetime import datetime
from flask import render_template, redirect, url_for, flash, Blueprint, request
from flask_security import login_required
from app import db
from app.forms import ExpanseForm, ByWeightForm, WriteOffForm, SupplyForm, CoffeeShopForm, TransferForm
from app.models import Barista, CoffeeShop, DailyReport, Warehouse, CoffeeShopEquipment, Expense, Supply, ByWeight, WriteOff


menu = Blueprint('menu', __name__, url_prefix='/menu')


@menu.route('/expense', methods=['POST'])
@login_required
def expense():
    form = ExpanseForm()
    if request.method == "POST":
        category = form.category.data
        type_cost = form.type_cost.data
        money = form.money.data
        expense = Expense(category=category, type_cost=type_cost, money=money)
        expense.timestamp = datetime.utcnow()
        coffee_shop = CoffeeShop.query.filter_by(place_name=form.coffee_shop.data).first_or_404()
        if form.type_cost.data == 'cash':
            coffee_shop.cash -= form.money.data
        else:
            coffee_shop.cashless -= form.money.data
        coffee_shop.expenses.append(expense)
        db.session.add(expense)
        db.session.commit()
        flash('New expense')
        return redirect(url_for("home"))

    return render_template("index.html")


@menu.route('/by_weight', methods=['POST'])
@login_required
def by_weight():
    form = ByWeightForm()
    if request.method == "POST":
        coffee_shop = CoffeeShop.query.filter_by(place_name=form.coffee_shop.data).first_or_404()
        warehouse = Warehouse.query.filter_by(coffee_shop_id=coffee_shop.id).first_or_404()
        if form.by_weight_choice.data == 'blend':
            warehouse.coffee_blend -= form.amount.data
        else:
            warehouse.coffee_arabika -= form.amount.data

        if form.cash_type.data == 'cash':
            coffee_shop.cash += form.money.data
        else:
            coffee_shop.cashless += form.money.data
        by_weight = ByWeight(coffee_shop=coffee_shop, amount=form.amount.data, product_name=form.by_weight_choice.data,
                             type_cost=form.cash_type.data, money=form.money.data)
        by_weight.timestamp = datetime.utcnow()
        db.session.add(by_weight)
        db.session.commit()
        flash(f'New trade by weight {form.by_weight_choice.data} on amount {form.amount.data} kg')
        return redirect(url_for("home"))
    return render_template("index.html")


@menu.route('/write_off', methods=['POST'])
@login_required
def write_off():
    form = WriteOffForm()
    if request.method == "POST":
        coffee_shop = CoffeeShop.query.filter_by(place_name=form.coffee_shop.data).first_or_404()
        warehouse = Warehouse.query.filter_by(coffee_shop_id=coffee_shop.id).first_or_404()
        if form.write_off_choice.data == 'blend':
            warehouse.coffee_blend -= form.amount.data
        elif form.write_off_choice.data == 'arabica':
            warehouse.coffee_arabika -= form.amount.data
        elif form.write_off_choice.data == 'milk':
            warehouse.milk -= form.amount.data
        elif form.write_off_choice.data == 'panini':
            warehouse.panini -= int(form.amount.data)
        else:
            warehouse.hot_dogs -= int(form.amount.data)
        write_off = WriteOff(coffee_shop=coffee_shop, amount=form.amount.data, product_name=form.write_off_choice.data)
        write_off.timestamp = datetime.utcnow()
        db.session.add(write_off)
        db.session.commit()
        flash(f'New write off {form.write_off_choice.data} on amount {form.amount.data}')
        return redirect(url_for("home"))
    return render_template("index.html")


@menu.route('/supply', methods=['POST'])
@login_required
def supply():
    form = SupplyForm()
    if request.method == "POST":
        coffee_shop = CoffeeShop.query.filter_by(place_name=form.coffee_shop.data).first_or_404()
        warehouse = Warehouse.query.filter_by(coffee_shop_id=coffee_shop.id).first_or_404()
        if form.supply_choice.data == 'blend':
            warehouse.coffee_blend += form.amount.data
        elif form.supply_choice.data == 'arabica':
            warehouse.coffee_arabika += form.amount.data
        elif form.supply_choice.data == 'milk':
            warehouse.milk += form.amount.data
        elif form.supply_choice.data == 'panini':
            warehouse.panini += int(form.amount.data)
        else:
            warehouse.hot_dogs += int(form.amount.data)

        if form.cash_type.data == 'cash':
            coffee_shop.cash -= form.money.data
        else:
            coffee_shop.cashless -= form.money.data

        supply = Supply(coffee_shop=coffee_shop, product_name=form.supply_choice.data,
                        amount=form.amount.data, type_cost=form.cash_type.data, money=form.money.data)
        supply.timestamp = datetime.utcnow()
        db.session.add(supply)
        db.session.commit()
        flash(f'New Supply {form.supply_choice.data} on amount {form.amount.data}')
        return redirect(url_for("home"))
    return render_template("index.html")


@menu.route('/transfer', methods=['POST'])
@login_required
def transfer():
    form = TransferForm(data=request.form)
    if request.method == "POST":
        # db.session.add()
        # db.session.commit()
        flash(f'Transfer {form.where_choice} to {form.from_choice}')
        return redirect(url_for("home"))
    else:
        flash(f'Errr... ')
    return render_template("index.html")


@menu.route('/create_coffee_shop', methods=['GET', 'POST'])
@login_required
def create_coffee_shop():
    form = CoffeeShopForm()
    if form.validate_on_submit():
        coffee_shop = CoffeeShop(place_name=form.place_name.data, address=form.address.data, cash=form.cash.data,
                                 cashless=form.cashless.data)
        warehouse = Warehouse(coffee_arabika=form.arabica.data, coffee_blend=form.blend.data, milk=form.milk.data,
                              panini=form.panini.data, hot_dogs=form.hot_dogs.data)
        equipments = CoffeeShopEquipment(coffee_machine=form.coffee_machine.data, grinder_1=form.grinder_1.data,
                                         grinder_2=form.grinder_2.data)
        coffee_shop.coffee_shop_equipments.append(equipments)
        coffee_shop.warehouse.append(warehouse)
        db.session.add(coffee_shop)
        db.session.add(warehouse)
        db.session.commit()
        flash('Congratulations, you are create a new coffee shop!')
        return redirect(url_for('home'))
    return render_template('menu/new_coffee_shop.html', form=form)
