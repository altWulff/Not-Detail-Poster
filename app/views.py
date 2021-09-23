from datetime import datetime
from flask import render_template, redirect, url_for, abort, request, flash, g, json
from flask_security import login_required,  login_user, logout_user, current_user, roles_required
from app import app, db
from app.forms import LoginForm, ReportForm, EditProfileForm, RegistrationForm, ExpanceForm
from app.models import Barista, CoffeeShop, DailyReport, Warehouse, CoffeeShopEquipment, Expense

@app.context_processor
def inject_form():
    expance_form = ExpanceForm()
    return dict(expance_form=expance_form)

@app.route('/')
@app.route('/index', methods=["POST","GET"])
@login_required
def home():
    warehouse= Warehouse
    cs_equip = CoffeeShopEquipment
    coffee_shop_list = CoffeeShop.query.all()
    return render_template('index.html', coffee_shop_list=coffee_shop_list, warehouse=warehouse,cs_equip=cs_equip)


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
    #form = ReportForm()
    #coffee_shop_list = enumerate(CoffeeShop.query.all())
    form = ReportForm()
    form.coffee_shop.choices = [(g.id, g.place_name +'/'+ g.address ) for g in CoffeeShop.query.order_by('place_name')]
    if form.validate_on_submit():
        coffee_shop = CoffeeShop.query.filter_by(id=form.coffee_shop.data).first_or_404()
        daily_report = DailyReport(cashbox=form.cashbox.data, cash_balance=form.cash_balance.data,
                                   cashless=form.cashless.data, remainder_of_day=form.remainder_of_day.data,
                                   barista=current_user, coffee_shop=coffee_shop)
        db.session.add(daily_report)
        db.session.commit()
        flash('Your daily report is now live!')
        return redirect(url_for('home'))
    return render_template('create_report.html', title='Create daily report', form=form)


@app.route('/reports/<coffee_shop_address>')
@login_required
def reports_on_address(coffee_shop_address):
    daily_reports = CoffeeShop.query.filter_by(address=coffee_shop_address).first_or_404().daily_reports
    g.current_coffee_shop = CoffeeShop.query.filter_by(address=coffee_shop_address).first()
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
    #if current_user.is_authenticated:
        #return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = Barista(name=form.name.data,
        phone_number=form.phone_number.data, email=form.email.data)
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


@app.route('/expance', methods=['POST'])
def new_expance():
    form = ExpanceForm()
    if request.method == "POST":
        category = form.category.data
        type_cost = form.type_cost.data
        money=form.money.data
        expance = Expense(category=category, type_cost=type_cost, money=money)
        expance.timestamp = datetime.utcnow()
        db.session.add(expance)
        db.session.commit()
        flash(form.data)
        return redirect(url_for("home"))

    return render_template("index.html")