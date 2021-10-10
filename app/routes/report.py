from . import datetime
from . import render_template, redirect, url_for, flash, Blueprint
from . import login_required, login_user, logout_user, current_user, roles_required
from . import db
from . import ReportForm
from . import Barista, CoffeeShop, DailyReport, Warehouse, CoffeeShopEquipment, Expense


report = Blueprint('report', __name__, url_prefix='/report')


@report.route('/create', methods=['GET', 'POST'])
@login_required
def create():
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
            expense = Expense(category=expense_dict['category'], type_cost=expense_dict['type_cost'],
                              money=expense_dict['money'])
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
    return render_template('report/create_report.html', title='Create daily report', form=form)


@report.route('/<coffee_shop_address>')
@login_required
def on_address(coffee_shop_address):
    coffee_shop = CoffeeShop.query.filter_by(address=coffee_shop_address).first_or_404()
    daily_reports = DailyReport.query.filter_by(coffee_shop_id=coffee_shop.id).order_by(DailyReport.timestamp.desc())
    return render_template('report/reports.html', daily_reports=daily_reports)
