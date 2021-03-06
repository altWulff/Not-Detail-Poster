"""
Module contains admin view for Expense model
"""

from datetime import datetime
from statistics import median, StatisticsError

from flask import Markup, flash
from flask_admin.babel import gettext
from flask_security import current_user
from sqlalchemy import func
from wtforms import BooleanField, RadioField
from wtforms.validators import (DataRequired, InputRequired, NumberRange,
                                Required)

from app.models import Barista, Expense, Shop

from . import ModeratorView, log
from .exceptions import FailedUpdateException, QueryException


class ExpenseAdmin(ModeratorView):
    """Expense model view"""

    @staticmethod
    def _list_money(context, model, name):
        del context, name
        if not model.money:
            return ""
        type_cost = "" if model.type_cost == "cash" else " (Безнал)"
        formatter = f"{model.money} грн.{type_cost}"
        return Markup(f"{formatter}")

    list_template = "admin/model/expense_list.html"
    can_set_page_size = True
    column_list = ("timestamp", "money", "is_global", "categories", "shop")
    form_create_rules = (
        "backdating",
        "timestamp",
        "is_global",
        "type_cost",
        "money",
        "categories",
        "shop",
        "barista",
    )
    form_edit_rules = (
        "backdating",
        "timestamp",
        "is_global",
        "type_cost",
        "money",
        "categories",
        "shop",
        "barista",
    )
    column_filters = (
        "timestamp",
        "is_global",
        "type_cost",
        "categories",
        Shop.place_name,
        Shop.address,
        Barista.name,
    )
    column_searchable_list = (Expense.timestamp,)
    column_labels = dict(
        category=gettext("Категория"),
        timestamp=gettext("Дата"),
        last_edit=gettext("Последнее изменение"),
        backdating=gettext("Обработка задним числом"),
        is_global=gettext("Глобальная?"),
        type_cost=gettext("Тип траты"),
        money=gettext("Сумма траты"),
        categories=gettext("Категории"),
        shop=gettext("Кофейня"),
        barista=gettext("Бариста"),
    )
    can_view_details = True
    column_default_sort = ("timestamp", True)
    column_formatters = dict(
        type_cost=lambda v, c, m, p: "Наличка" if m.type_cost == "cash" else "Безнал",
        is_global=lambda v, c, m, p: "Да" if m.is_global else "Нет",
        money=_list_money,
    )
    form_extra_fields = {
        "backdating": BooleanField("Обработка задним числом"),
        "type_cost": RadioField(
            gettext("Тип траты"),
            default="cash",
            choices=[("cash", gettext("Наличка")), ("cashless", gettext("Безнал"))],
            validators=[Required()],
        ),
    }
    form_widget_args = {
        "timestamp": {"data-date-format": "DD.MM.YYYY HH:mm"},
        "money": {"placeholder": gettext("В гривнях")},
        "type_cost": {"class": "form-check"},
    }
    form_ajax_refs = {
        "categories": {
            "fields": ("name",),
            "placeholder": gettext("Добавить категорию"),
            "page_size": 10,
            "minimum_input_length": 0,
        },
        "shop": {
            "fields": ("place_name", "address"),
            "placeholder": gettext("Кофейня"),
            "page_size": 10,
            "minimum_input_length": 0,
        },
    }
    form_args = dict(
        timestamp=dict(validators=[DataRequired()], format="%d.%m.%Y %H:%M"),
        money=dict(
            validators=[
                InputRequired(),
                NumberRange(
                    min=0,
                    max=1000000000,
                    message=gettext("Сумма не может быть нулевой, либо ниже нуля"),
                ),
            ]
        ),
        shop=dict(validators=[DataRequired(message=gettext("Выберите кофейню"))]),
    )

    @property
    def shop_id(self):
        return self.model.shop_id

    def sum_page(self, attr: str) -> int:
        """Query sum on page"""
        _query = self.get_model_data()
        try:
            return sum([p.__dict__[attr] for p in _query if p])
        except (Exception, QueryException):
            return 0

    def sum_total(self, attr: str) -> int:
        """Query total sum"""
        _query = self.session.query(func.sum(Expense.__dict__[attr])).scalar()
        try:
            return _query
        except (Exception, QueryException):
            return 0

    def median_page(self, attr: str) -> int:
        """Query median on page"""
        _query = self.get_model_data()
        data = [p.__dict__[attr] for p in _query if p]
        try:
            return median(data)
        except StatisticsError:
            return 0

    def median_total(self, attr: str) -> int:
        """Query total median"""
        _query = self.session.query(func.avg(Expense.__dict__[attr])).scalar()
        try:
            return round(_query)
        except TypeError:
            return 0

    def render(self, template, **kwargs):
        """Render template"""
        _current_page = kwargs
        kwargs["column_labels"] = self.column_labels
        kwargs["summary_data"] = {"on_page": {}, "total": {}}
        kwargs["median_data"] = {"on_page": {}, "total": {}}
        render_fields = ("money",)
        for field in render_fields:
            kwargs["summary_data"]["on_page"][field] = self.sum_page(field)
            kwargs["summary_data"]["total"][field] = self.sum_total(field)
            kwargs["median_data"]["on_page"][field] = self.median_page(field)
            kwargs["median_data"]["total"][field] = self.median_total(field)
        return super().render(template, **kwargs)

    def create_form(self, obj=None):
        """Before create form"""
        form = super().create_form(obj)
        form.timestamp.data = datetime.utcnow()
        form.barista.data = current_user
        return form

    def update_model(self, form, model):
        """Update model with save previous state"""
        try:
            new_money, old_money = form.money.data, model.money
            form.populate_obj(model)
            self._on_model_change(form, model, False)
            self.session.commit()
        except FailedUpdateException as ex:
            if not self.handle_view_exception(ex):
                flash(
                    gettext("Failed to update record. %(error)s", error=str(ex)),
                    "error",
                )
                log.exception("Failed to update record.")
            self.session.rollback()
            return False
        else:
            if new_money != old_money:
                form.money.data = old_money
            self.after_model_change(form, model, False)
        return True

    def on_model_change(self, form, model, is_created):
        """Work with model after create"""
        if form.backdating.data:
            model.backdating = form.backdating.data
            return
        money = model.money
        if model.type_cost == "cash":
            model.shop.cash -= money
        else:
            model.shop.cashless -= money

    def after_model_change(self, form, model, is_created):
        """Work with model after change"""
        if form.backdating.data:
            return
        if not is_created:
            model.last_edit = datetime.utcnow()
            if form.type_cost.data == "cash":
                model.shop.cash += form.money.data
            else:
                model.shop.cashless += form.money.data
            self.session.commit()

    def on_model_delete(self, model):
        """Work with model after delete"""
        if model.backdating:
            return
        if model.type_cost and model.money and model.shop:
            if model.type_cost == "cash":
                model.shop.cash += model.money
            else:
                model.shop.cashless += model.money
