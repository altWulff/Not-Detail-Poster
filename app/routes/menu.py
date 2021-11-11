from datetime import datetime
from flask import render_template, redirect, url_for, flash, Blueprint, request
from flask_security import current_user, login_required
from app import app, db
from app.forms import ExpanseForm, ByWeightForm, WriteOffForm, SupplyForm, CoffeeShopForm, TransferForm
from app.models import Shop, Storage, ShopEquipment, Expense, Supply, ByWeight, WriteOff, Category
from app.business_logic import transaction_count


menu = Blueprint('menu', __name__, url_prefix='/menu')

    
@menu.route('/expense', methods=['POST'])
@login_required
def expense():
    form = ExpanseForm()
    if form.validate_on_submit():
        shop = Shop.query.filter_by(id=form.coffee_shop.data).first_or_404()
        if transaction_count(shop.id) >= app.config['REPORTS_PER_DAY']:
            flash("Сегодняшний отчет уже был отправлен!")
            return redirect(url_for('home'))
        type_cost = form.type_cost.data
        money = form.money.data
        expense = Expense(type_cost=type_cost, money=money, is_global=form.is_global.data)
        expense.timestamp = datetime.now()
        if form.type_cost.data == 'cash':
            shop.cash -= form.money.data
        else:
            shop.cashless -= form.money.data
        flash(form.categories.data)
        for c_id in form.categories.data:
            category = Category.query.filter_by(id=c_id).first_or_404()
            expense.categories.append(category)
        shop.expenses.append(expense)
        db.session.add(expense)
        db.session.commit()
        flash('New expense')
        return redirect(url_for("home"))
    flash(form.data)
    flash(form.validate())
    return render_template("index.html")


@menu.route('/by_weight', methods=['POST'])
@login_required
def by_weight():
    form = ByWeightForm(request.form)
    if form.validate_on_submit():
        shop = Shop.query.filter_by(id=form.coffee_shop.data).first_or_404()
        storage = Storage.query.filter_by(shop_id=shop.id).first_or_404()
        if transaction_count(shop.id) >= app.config['REPORTS_PER_DAY']:
            flash("Сегодняшний отчет уже был отправлен!")
            return redirect(url_for('home'))
        if form.by_weight_choice.data == 'blend':
            storage.coffee_blend -= form.amount.data
        else:
            storage.coffee_arabika -= form.amount.data

        if form.cash_type.data == 'cash':
            shop.cash += form.money.data
        else:
            shop.cashless += form.money.data
        by_weight = ByWeight(storage=storage, amount=form.amount.data, product_name=form.by_weight_choice.data,
                             type_cost=form.cash_type.data, money=form.money.data)
        by_weight.timestamp = datetime.now()
        db.session.add(by_weight)
        db.session.commit()
        flash(f'New trade by weight {form.by_weight_choice.data} on amount {form.amount.data} kg')
        return redirect(url_for("home"))
    return render_template("index.html")


@menu.route('/write_off', methods=['POST'])
@login_required
def write_off():
    form = WriteOffForm(request.form)
    if form.validate_on_submit():
        shop = Shop.query.filter_by(id=form.coffee_shop.data).first_or_404()
        storage = Storage.query.filter_by(shop_id=shop.id).first_or_404()
        if transaction_count(shop.id) >= app.config['REPORTS_PER_DAY']:
            flash("Сегодняшний отчет уже был отправлен!")
            return redirect(url_for('home'))
        if form.write_off_choice.data == 'blend':
            storage.coffee_blend -= form.amount.data
        elif form.write_off_choice.data == 'arabica':
            storage.coffee_arabika -= form.amount.data
        elif form.write_off_choice.data == 'milk':
            storage.milk -= form.amount.data
        elif form.write_off_choice.data == 'panini':
            storage.panini -= int(form.amount.data)
        else:
            storage.hot_dogs -= int(form.amount.data)
        write_off = WriteOff(storage=storage, amount=form.amount.data, product_name=form.write_off_choice.data)
        write_off.timestamp = datetime.now()
        db.session.add(write_off)
        db.session.commit()
        flash(f'New write off {form.write_off_choice.data} on amount {form.amount.data}')
        return redirect(url_for("home"))
    return render_template("index.html")


@menu.route('/supply', methods=['POST'])
@login_required
def supply():
    form = SupplyForm(request.form)
    if form.validate_on_submit():
        shop = Shop.query.filter_by(id=form.coffee_shop.data).first_or_404()
        storage = Storage.query.filter_by(shop_id=shop.id).first_or_404()
        if transaction_count(shop.id) >= app.config['REPORTS_PER_DAY']:
            flash("Сегодняшний отчет уже был отправлен!")
            return redirect(url_for('home'))
        if form.supply_choice.data == 'blend':
            storage.coffee_blend += form.amount.data
        elif form.supply_choice.data == 'arabica':
            storage.coffee_arabika += form.amount.data
        elif form.supply_choice.data == 'milk':
            storage.milk += form.amount.data
        elif form.supply_choice.data == 'panini':
            storage.panini += int(form.amount.data)
        else:
            storage.hot_dogs += int(form.amount.data)

        if form.cash_type.data == 'cash':
            shop.cash -= form.money.data
        else:
            shop.cashless -= form.money.data

        supply = Supply(storage=storage, product_name=form.supply_choice.data,
                        amount=form.amount.data, type_cost=form.cash_type.data, money=form.money.data)
        supply.timestamp = datetime.now()
        db.session.add(supply)
        db.session.commit()
        flash(f'New Supply {form.supply_choice.data} on amount {form.amount.data}')
        return redirect(url_for("home"))
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
