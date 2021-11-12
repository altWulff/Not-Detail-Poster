from datetime import datetime
from flask import render_template, redirect, url_for, flash, Blueprint, request
from flask_security import current_user, login_required
from app import app, db
from app.forms import ExpanseForm, ByWeightForm, WriteOffForm, SupplyForm, CoffeeShopForm, TransferForm
from app.models import Shop, Storage, ShopEquipment, Expense, Supply, ByWeight, WriteOff, Category
from app.business_logic import transaction_count, TransactionHandler


menu = Blueprint('menu', __name__, url_prefix='/menu')

    
@menu.route('/expense', methods=['POST'])
@login_required
def expense():
    form = ExpanseForm()
    transaction = TransactionHandler(form.coffee_shop.data)
    if form.validate_on_submit():
        transaction.create_expense(form)
        flash(transaction.COMMIT_MESSAGE)
        return redirect(url_for("home"))
    else:
        flash(transaction.NON_VALID_MESSAGE)
    return render_template("index.html")


@menu.route('/by_weight', methods=['POST'])
@login_required
def by_weight():
    form = ByWeightForm(request.form)
    transaction = TransactionHandler(form.coffee_shop.data)
    if form.validate_on_submit():
        transaction.crete_by_weight(form)
        flash(transaction.COMMIT_MESSAGE)
        return redirect(url_for("home"))
    else:
        flash(transaction.NON_VALID_MESSAGE)
    return render_template("index.html")


@menu.route('/write_off', methods=['POST'])
@login_required
def write_off():
    form = WriteOffForm(request.form)
    transaction = TransactionHandler(form.coffee_shop.data)
    if form.validate_on_submit():
        transaction.create_write_off(form)
        flash(transaction.COMMIT_MESSAGE)
        return redirect(url_for("home"))
    else:
        flash(transaction.NON_VALID_MESSAGE)
    return render_template("index.html")


@menu.route('/supply', methods=['POST'])
@login_required
def supply():
    form = SupplyForm(request.form)
    transaction = TransactionHandler(form.coffee_shop.data)
    if form.validate_on_submit():
        transaction.create_supply(form)
        flash(transaction.COMMIT_MESSAGE)
        return redirect(url_for("home"))
    else:
        flash(transaction.NON_VALID_MESSAGE)
    return render_template("index.html")


#TODO доделать перемещение
@menu.route('/transfer', methods=['POST'])
@login_required
def transfer():
    form = TransferForm(request.form)
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
        shop = Shop(
            place_name=form.place_name.data,
            address=form.address.data,
            cash=form.cash.data,
            cashless=form.cashless.data
        )
        storage = Storage(
            coffee_arabika=form.arabica.data,
            coffee_blend=form.blend.data,
            milk=form.milk.data,
            panini=form.panini.data,
            hot_dogs=form.hot_dogs.data
        )
        equipments = ShopEquipment(
            coffee_machine=form.coffee_machine.data,
            grinder_1=form.grinder_1.data,
            grinder_2=form.grinder_2.data
        )
        shop.shop_equipments.append(equipments)
        shop.storage.append(storage)
        db.session.add(shop)
        db.session.add(storage)
        db.session.commit()
        flash('Создана новая кофейня!')
        return redirect(url_for('home'))
    return render_template('menu/new_coffee_shop.html', form=form)
