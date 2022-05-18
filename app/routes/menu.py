"""
Module for transaction menu
"""

from datetime import datetime

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_babelex import _
from flask_modals import render_template_modal
from flask_security import login_required, roles_accepted

from app import db
from app.business_logic import TransactionHandler
from app.forms import (ByWeightForm, CoffeeShopForm, ExpanseForm, SupplyForm,
                       WriteOffForm)
from app.models import Barista, Shop, ShopEquipment, Storage

menu = Blueprint("menu", __name__, url_prefix="/menu")


@menu.route("/expense", methods=("POST",))
@login_required
def expense():
    """Expanse transaction form"""
    form = ExpanseForm()
    transaction = TransactionHandler(form.coffee_shop.data)
    if form.validate_on_submit():
        if transaction.is_report_send(form.coffee_shop.data):
            flash(_("Сегодняшний отчет уже был отправлен!"))
        else:
            transaction.create_expense(form)
            flash(_("Транзакция принята!"))
        return redirect(url_for("home"))
    flash(_("Транзакция не принята!  Попробуйте заново, с коректными значениями."))
    return render_template_modal("index.html", modal="modal-form")


@menu.route(
    "/by_weight",
    methods=[
        "POST",
    ],
)
@login_required
def by_weight():
    """By weight transaction form"""
    form = ByWeightForm(request.form)
    transaction = TransactionHandler(form.coffee_shop.data)
    if form.validate_on_submit():
        if transaction.is_report_send(form.coffee_shop.data):
            flash(_("Сегодняшний отчет уже был отправлен!"))
        else:
            transaction.crete_by_weight(form)
            flash(_("Транзакция принята!"))
        return redirect(url_for("home"))
    flash(_("Транзакция не принята!  Попробуйте заново, с коректными значениями."))
    return render_template_modal("index.html", modal="modal-form")


@menu.route("/write_off", methods=("POST",))
@login_required
def write_off():
    """Write off transaction form"""
    form = WriteOffForm(request.form)
    transaction = TransactionHandler(form.coffee_shop.data)
    if form.validate_on_submit():
        if transaction.is_report_send(form.coffee_shop.data):
            flash(_("Сегодняшний отчет уже был отправлен!"))
        else:
            transaction.create_write_off(form)
            flash(_("Транзакция принята!"))
        return redirect(url_for("home"))
    flash(_("Транзакция не принята!  Попробуйте заново, с коректными значениями."))
    return render_template_modal("index.html", modal="modal-form")


@menu.route("/supply", methods=("POST",))
@login_required
def supply():
    """Supply off transaction form"""
    form = SupplyForm(request.form)
    transaction = TransactionHandler(form.coffee_shop.data)
    if form.validate_on_submit():
        if transaction.is_report_send(form.coffee_shop.data):
            flash(_("Сегодняшний отчет уже был отправлен!"))
        else:
            transaction.create_supply(form)
            flash(_("Транзакция принята!"))
        return redirect(url_for("home"))
    flash(_("Транзакция не принята!  Попробуйте заново, с коректными значениями."))
    return render_template_modal("index.html", modal="modal-form")


@menu.route("/create_coffee_shop", methods=("GET", "POST"))
@login_required
@roles_accepted("admin", "moderator")
def create_coffee_shop():
    """Create coffee shop form"""
    form = CoffeeShopForm()
    if form.validate_on_submit():
        shop = Shop(
            place_name=form.place_name.data,
            address=form.address.data,
            timestamp=datetime.utcnow(),
            cash=form.cash.data,
            cashless=form.cashless.data,
        )
        storage = Storage(
            coffee_arabika=form.coffee_arabika.data,
            coffee_blend=form.coffee_blend.data,
            milk=form.milk.data,
            panini=form.panini.data,
            sausages=form.sausages.data,
            buns=form.buns.data,
        )
        equipment = ShopEquipment(
            coffee_machine=form.coffee_machine.data,
            grinder_1=form.grinder_1.data,
            grinder_2=form.grinder_2.data,
        )
        shop.shop_equipment = equipment
        shop.storage = storage
        for staff_id in form.staff_list.data:
            staff = Barista.query.filter_by(id=staff_id).first_or_404()
            shop.baristas.append(staff)
        db.session.add(storage)
        db.session.add(equipment)
        db.session.add(shop)
        db.session.commit()
        flash(_("Создана новая кофейня!"))
        return redirect(url_for("home"))
    return render_template("menu/new_coffee_shop.html", form=form)
