from flask import render_template, redirect, url_for, abort, request, flash, g
from flask_login import login_required, login_user, logout_user, current_user
from app import app, db
from app.forms import LoginForm, ReportForm, EditProfileForm
from app.models import Barista, CoffeeShop, DailyReport


@app.route('/')
@app.route('/index')
@login_required
def home():
    coffee_shop_list = CoffeeShop.query.all()
    return render_template('index.html', coffee_shop_list=coffee_shop_list)


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
    if form.validate_on_submit():
        daily_report = DailyReport(cashbox=form.cashbox.data, cash_balance=form.cash_balance.data,
                                   cashless=form.cashless.data, remainder_of_day=form.remainder_of_day.data,
                                   barista=current_user)
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
@login_required
def statistics():
    return render_template('statistics.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    app.logger.info(form.validate_on_submit())
    if form.validate_on_submit():
        user = Barista.query.filter_by(name=form.name.data).first()
        # if user is None or not user.check_phone_number(form.phone_number.data) or not user.check_password(form.password.data):
        #     flash('Invalid name, phone number or password')
        #     return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        return redirect('index')
    return render_template('login.html', title='Sign In', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect('index')
