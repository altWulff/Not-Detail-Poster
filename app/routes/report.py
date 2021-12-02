from flask import render_template, redirect, url_for, flash, Blueprint, request
from flask_security import login_required, current_user
from flask_babelex import _
from app import db, app
from app.forms import ReportForm
from app.models import Shop, Report, Storage, Expense, Supply, baristas, Barista
from app.business_logic import TransactionHandler


report = Blueprint('reports', __name__, url_prefix='/report')


@report.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    form = ReportForm(request.form)
    if form.validate_on_submit():
        transaction = TransactionHandler(form.shop.data)
        if transaction.is_report_send(form.shop.data):
            flash(_('Сегодняшний отчет уже был отправлен!'))
        else:
            transaction.create_report(form)
            flash(_('Отчет за день отправлен!'))
        return redirect(url_for('home'))
    return render_template('report/create_report.html', title='Создание отчёта', form=form)


@report.route('/<shop_address>')
@login_required
def on_address(shop_address):
    shop = Shop.query.filter_by(address=shop_address).first_or_404()
    storage = Storage.query.filter_by(shop_id=shop.id).first_or_404()
    reports = Report.query.filter_by(shop_id=shop.id).order_by(Report.timestamp.desc())
    if not (current_user.has_role('admin') or current_user.has_role('moderator')):
        reports = reports.limit(app.config['REPORTS_USER_VIEW']).from_self()
        
    global_expense = Expense.get_global(shop.id)
    local_expense = Expense.get_local(shop.id)
    supply = Supply.get_local(storage.id)
    page = request.args.get('page', 1, type=int)
    reports = reports.paginate(
        page,
        app.config['REPORTS_PER_PAGE'],
        False
    )
    next_url = url_for(
        'reports.on_address',
        shop_address=shop.address,
        page=reports.next_num
    ) if reports.has_next else None
    prev_url = url_for(
        'reports.on_address',
        shop_address=shop.address,
        page=reports.prev_num
    ) if reports.has_prev else None
    return render_template(
        "report/reports.html",
        daily_reports=reports.items,
        global_expense=global_expense,
        local_expense=local_expense,
        supply=supply,
        next_url=next_url,
        prev_url=prev_url
    )
