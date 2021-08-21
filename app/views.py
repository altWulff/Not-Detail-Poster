from flask import render_template, redirect, url_for, abort, request, flash, g
from flask_login import login_required, login_user, current_user
from app import app
from app.forms import LoginForm
from app.models import Barista, CoffeeShop, DailyReport


@app.route('/')
@app.route('/index')
# @login_required
def home():
    return render_template('index.html')


@app.route('/reports')
def reports():
    daily_reports = CoffeeShop.query.first().daily_reports
    return render_template('reports.html', daily_reports=daily_reports)


@app.route('/reports/<coffee_shop_address>')
def reports_on_address(coffee_shop_address):
    daily_reports = CoffeeShop.query.filter_by(address=coffee_shop_address).first_or_404().daily_reports
    return render_template('reports.html', daily_reports=daily_reports)


@app.route('/statistics')
# @login_required
def statistics():
    return render_template('statistics.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    app.logger.info('Login form')
    form = LoginForm()
    if form.validate_on_submit():
        app.logger.info('Submit')
        user = Barista.query.filter_by(name=form.name.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        return redirect(url_for('index'))
    return render_template('login.html', title='Sign In', form=form)
