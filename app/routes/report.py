from sqlalchemy import func
from datetime import datetime, date
from flask import render_template, redirect, url_for, flash, Blueprint, request
from flask_security import login_required, current_user
from app import db, app
from app.forms import ReportForm
from app.models import Shop, Report, Storage, Expense, Supply
from app.business_logic import transaction_count, date_today

report = Blueprint('reports', __name__, url_prefix='/report')



@report.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    form = ReportForm()
    form.shop.choices = [(g.id, g.place_name + '/' + g.address) for g in Shop.query.order_by('place_name')]
  
    if form.validate_on_submit():
        shop = Shop.query.filter_by(id=form.shop.data).first_or_404()
        storage = Storage.query.filter_by(shop_id=shop.id).first_or_404()

        if transaction_count(shop.id) >= app.config['REPORTS_PER_DAY']:
            flash("Сегодняшний отчет уже был отправлен!")
            return redirect(url_for('home'))

        cash_balance = form.actual_balance.data - shop.cash
        shop.cash += cash_balance
        shop.cashless += form.cashless.data
        remainder_of_day = form.cashless.data + cash_balance
        report = Report(
            cash_balance=cash_balance,
            cashless=form.cashless.data,
            actual_balance=form.actual_balance.data,
            remainder_of_day=remainder_of_day,
            barista=current_user,
            shop=shop
        )
        for expense_dict in form.expanses.data:
            expense = Expense(type_cost=expense_dict['type_cost'],
                              money=expense_dict['money'], shop=shop)
            report.expenses.append(expense)
        expanses = sum([exp['money'] for exp in form.expanses.data])
        report.cashbox = remainder_of_day + expanses
        # consumption
        report.consumption_coffee_arabika = storage.coffee_arabika - form.arabica.data
        report.coffee_arabika = form.arabica.data
        storage.coffee_arabika -= report.consumption_coffee_arabika

        report.consumption_coffee_blend = storage.coffee_blend - form.blend.data
        report.coffee_blend = form.blend.data
        storage.coffee_blend -= report.consumption_coffee_blend

        report.consumption_milk = storage.milk - form.milk.data
        report.milk = form.milk.data
        storage.milk -= report.consumption_milk

        report.consumption_panini = storage.panini - form.panini.data
        report.panini = form.panini.data
        storage.panini -= report.consumption_panini

        report.consumption_hot_dogs = storage.hot_dogs - form.hot_dogs.data
        report.hot_dogs = form.hot_dogs.data
        storage.hot_dogs -= report.consumption_hot_dogs
        report.timestamp = datetime.utcnow()
        db.session.add(report)
        db.session.commit()
        flash('Your daily report is now live!')
        return redirect(url_for('home'))
    return render_template('report/create_report.html', title='Create daily report', form=form)


@report.route('/<shop_address>')
@login_required
def on_address(shop_address):
    shop = Shop.query.filter_by(address=shop_address).first_or_404()
    storage = Storage.query.filter_by(shop_id=shop.id).first_or_404()
    reports = Report.query.filter_by(shop_id=shop.id).order_by(Report.timestamp.desc())
    if not (current_user.has_role('admin') or current_user.has_role('moderator')):
        reports = reports.limit(app.config['REPORTS_USER_VIEW']).from_self()
        
    global_expense = Expense.get_global(shop.id, True)
    local_expense = Expense.get_local(shop.id, True)
    day_supply = Supply.query.filter(Supply.timestamp >= date_today).filter_by(storage_id=storage.id)
    page = request.args.get('page', 1, type=int)
    reports = reports.paginate(
        page, app.config['REPORTS_PER_PAGE'], False)
    next_url = url_for('reports.on_address', shop_address=shop.address, page=reports.next_num) \
        if reports.has_next else None
    prev_url = url_for('reports.on_address', shop_address=shop.address, page=reports.prev_num) \
        if reports.has_prev else None
    return render_template(
        "report/reports.html",
        daily_reports=reports.items,
        global_expense=global_expense,
        local_expense=local_expense,
        day_supply=day_supply,
        next_url=next_url,
        prev_url=prev_url
    )
