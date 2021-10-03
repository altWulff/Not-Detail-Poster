from datetime import datetime
from flask import render_template, redirect, url_for, abort, request, flash, g, json
from flask_security import login_required, login_user, logout_user, current_user, roles_required
from app import app, db
from app.forms import LoginForm, ReportForm, EditProfileForm, RegistrationForm, ExpanseForm, ByWeightForm, WriteOffForm, SupplyForm, CoffeeShopForm
from app.models import Barista, CoffeeShop, DailyReport, Warehouse, CoffeeShopEquipment, Expense


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


@app.route('/reports')
@login_required
def reports():
    daily_reports = CoffeeShop.query.first().daily_reports
    return render_template('reports.html', daily_reports=daily_reports)


@app.route('/user/<user_name>')
@login_required
def user_profile(user_name):
    user = Barista.query.filter_by(name=user_name).first_or_404()
    return render_template('user.html', user=user)


@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm()
    if form.validate_on_submit():
        current_user.name = form.name.data
        current_user.phone_number = form.phone_number.data
        current_user.email = form.email.data
        db.session.commit()
        flash('Your changes have been saved.')
        return redirect(url_for('user_profile', user_name=current_user.name))
    elif request.method == 'GET':
        form.name.data = current_user.name
        form.phone_number.data = current_user.phone_number
        form.email.data = current_user.email
    return render_template('user_edit.html', user=current_user,
                           form=form)


@app.route('/create_report', methods=['GET', 'POST'])
@login_required
def create_report():
    form = ReportForm()
    form.coffee_shop.choices = [(g.id, g.place_name + '/' + g.address) for g in CoffeeShop.query.order_by('place_name')]
    if form.validate_on_submit():
        coffee_shop = CoffeeShop.query.filter_by(id=form.coffee_shop.data).first_or_404()
        warehouse = Warehouse.query.filter_by(coffee_shop_id=coffee_shop.id).first_or_404()
        cash_balance = form.actual_balance.data - coffee_shop.cash
        coffee_shop.cash += cash_balance
        coffee_shop.cashless += form.cashless.data
        remainder_of_day = form.cashless.data + cash_balance
        daily_report = DailyReport(cash_balance=cash_balance, cashless=form.cashless.data,
                                   actual_balance=form.actual_balance.data,
                                   remainder_of_day=remainder_of_day,
                                   barista=current_user, coffee_shop=coffee_shop)
        for expense_dict in form.expanses.data:
            expense = Expense(category=expense_dict['category'], type_cost=expense_dict['type_cost'], money=expense_dict['money'])
            daily_report.expenses.append(expense)
        expanses = sum([exp['money'] for exp in form.expanses.data])
        daily_report.cashbox = remainder_of_day + expanses
        # consumption
        daily_report.consumption_coffee_arabika = warehouse.coffee_arabika - form.arabica.data
        daily_report.coffee_arabika = form.arabica.data
        warehouse.coffee_arabika -= daily_report.consumption_coffee_arabika
        
        daily_report.consumption_coffee_blend = warehouse.coffee_blend - form.blend.data
        daily_report.coffee_blend = form.blend.data
        warehouse.coffee_blend -= daily_report.consumption_coffee_blend

        daily_report.consumption_milk = warehouse.milk - form.milk.data
        daily_report.milk = form.milk.data
        warehouse.milk -= daily_report.consumption_milk
        
        daily_report.consumption_panini = warehouse.panini - form.panini.data
        daily_report.panini = form.panini.data
        warehouse.panini -= daily_report.consumption_panini
        
        daily_report.consumption_hot_dogs = warehouse.hot_dogs - form.hot_dogs.data
        daily_report.hot_dogs = form.hot_dogs.data
        warehouse.hot_dogs -= daily_report.consumption_hot_dogs
        
        db.session.add(daily_report)
        db.session.commit()
        flash('Your daily report is now live!')
        return redirect(url_for('home'))
    return render_template('create_report.html', title='Create daily report', form=form)


@app.route('/reports/<coffee_shop_address>')
@login_required
def reports_on_address(coffee_shop_address):
    daily_reports = CoffeeShop.query.filter_by(address=coffee_shop_address).first_or_404().daily_reports
    return render_template('reports.html', daily_reports=daily_reports)


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
    return render_template('login.html', title='Sign In', form=form)


@app.route('/new_staff', methods=['GET', 'POST'])
def create_new_staff():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = Barista(name=form.name.data,
                       phone_number=form.phone_number.data,
                       email=form.email.data)
        user.set_password(form.password.data)
        user.confirmed_at = datetime.utcnow()
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('new_staff.html', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect('index')


@app.route('/expense', methods=['POST'])
def new_expense():
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


@app.route('/by_weight', methods=['POST'])
def by_weight():
    form = ByWeightForm()
    if request.method == "POST":
        # db.session.add()
        # db.session.commit()
        flash('New trade by weight')
        return redirect(url_for("home"))
    return render_template("index.html")


@app.route('/write_off', methods=['POST'])
def write_off():
    form = WriteOffForm()
    if request.method == "POST":
        # db.session.add()
        # db.session.commit()
        flash('New write off')
        return redirect(url_for("home"))
    return render_template("index.html")


@app.route('/supply', methods=['POST'])
def supply():
    form = SupplyForm()
    if request.method == "POST":
        # db.session.add()
        # db.session.commit()
        flash('New Supply')
        return redirect(url_for("home"))
    return render_template("index.html")


@app.route('/new_coffee_shop', methods=['GET', 'POST'])
def new_coffee_shop():
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
        db.session.commit()
        flash('Congratulations, you are create a new coffee shop!')
        return redirect(url_for('home'))
    return render_template('new_coffee_shop.html', form=form)
