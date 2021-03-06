"""
Module for report form
"""

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_babelex import _
from flask_security import current_user, login_required

from app import app, date_today
from app.business_logic import TransactionHandler
from app.forms import ReportForm
from app.models import (ByWeight, Category, CollectionFund, DepositFund,
                        Expense, Report, Shop, Storage, Supply,
                        TransferProduct)

report = Blueprint("reports", __name__, url_prefix="/report")


@report.route("/create", methods=["GET", "POST"])
@login_required
def create():
    """Create report form"""
    form = ReportForm(request.form)
    find_salary_exp = Expense.query.select_from(Category)
    find_salary_exp = find_salary_exp.filter(Category.name == "Зарплата")
    find_salary_exp = find_salary_exp.filter(Expense.timestamp >= date_today).first()
    if not find_salary_exp:
        flash(_("Возьмите зарплату за сегодняшний день!"))
    if form.validate_on_submit():
        transaction = TransactionHandler(form.shop.data)

        if transaction.is_report_send(form.shop.data):
            flash(_("Сегодняшний отчет уже был отправлен!"))
        else:
            transaction.create_report(form)
            flash(_("Отчет за день отправлен!"))
        return redirect(url_for("home"))
    return render_template(
        "report/create_report.html", title="Создание отчёта", form=form
    )


@report.route("/<shop_address>")
@login_required
def on_address(shop_address):
    """Render all reports with pagination"""
    shop = Shop.query.filter_by(address=shop_address).first_or_404()
    storage = Storage.query.filter_by(shop_id=shop.id).first_or_404()
    reports = Report.query.filter_by(shop_id=shop.id).order_by(Report.timestamp.desc())
    if not (current_user.has_role("admin") or current_user.has_role("moderator")):
        reports = reports.limit(app.config["REPORTS_USER_VIEW"]).from_self()

    global_expense = Expense.get_global(shop.id)
    local_expense = Expense.get_local(shop.id)
    supply = Supply.get_local(storage.id, False)
    by_weight = ByWeight.get_local(storage.id, False)
    deposit_fund = DepositFund.get_local_by_shop(shop.id, False)
    collection_fund = CollectionFund.get_local_by_shop(shop.id, False)
    transfer = TransferProduct
    page = request.args.get("page", 1, type=int)
    reports = reports.paginate(page, app.config["REPORTS_PER_PAGE"], False)
    next_url = (
        url_for("reports.on_address", shop_address=shop.address, page=reports.next_num)
        if reports.has_next
        else None
    )
    prev_url = (
        url_for("reports.on_address", shop_address=shop.address, page=reports.prev_num)
        if reports.has_prev
        else None
    )
    return render_template(
        "report/reports.html",
        daily_reports=reports.items,
        global_expense=global_expense,
        local_expense=local_expense,
        deposit_fund=deposit_fund,
        collection_fund=collection_fund,
        transfer=transfer,
        supply=supply,
        by_weight=by_weight,
        next_url=next_url,
        prev_url=prev_url,
    )
