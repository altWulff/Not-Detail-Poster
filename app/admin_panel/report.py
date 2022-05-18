"""
Module contains admin view for Report model
"""


from datetime import datetime
from statistics import median, StatisticsError

from flask import flash
from flask_admin.babel import gettext
from flask_security import current_user
from sqlalchemy import func
from wtforms import BooleanField
from wtforms.validators import DataRequired, InputRequired, NumberRange

from app.models import Barista, ByWeight, Report, Shop

from . import ModeratorView, log
from .exceptions import FailedUpdateException, QueryException


class ReportAdmin(ModeratorView):
    """Report model view"""

    list_template = "admin/model/report_list.html"
    can_view_details = True
    can_set_page_size = True
    column_default_sort = ("timestamp", True)
    column_formatters = dict(
        expenses=lambda v, c, m, p: sum(
            [e.money for e in m.expenses if e.type_cost == "cash"]
        )
    )
    column_searchable_list = (Report.timestamp,)
    column_exclude_list = (
        "backdating",
        "last_edit",
        "consumption_coffee_arabika",
        "consumption_coffee_blend",
        "consumption_milk",
        "consumption_panini",
        "consumption_sausages",
        "consumption_buns",
        "coffee_arabika",
        "coffee_blend",
        "milk",
        "panini",
        "sausages",
        "buns",
    )
    column_list = (
        "timestamp",
        "cashbox",
        "expenses",
        "remainder_of_day",
        "cashless",
        "cash_balance",
        "actual_balance",
        "shop",
        "barista",
    )
    column_filters = (Report.timestamp, Barista.name, Shop.place_name, Shop.address)
    column_labels = dict(
        place_name=gettext("Название"),
        address=gettext("Адрес"),
        name=gettext("Имя"),
        shop=gettext("Кофейня"),
        barista=gettext("Бариста"),
        timestamp=gettext("Дата"),
        last_edit=gettext("Последнее изменение"),
        backdating=gettext("Обработка задним числом"),
        cashbox=gettext("Касса"),
        remainder_of_day=gettext("Остаток дня"),
        cashless=gettext("Б.Н"),
        cash_balance=gettext("Остаток наличности"),
        actual_balance=gettext("Фактический остаток"),
        consumption_coffee_arabika=gettext("Арабика/день"),
        consumption_coffee_blend=gettext("Бленд/день"),
        consumption_milk=gettext("Молоко/день"),
        consumption_panini=gettext("Панини/день"),
        consumption_sausages=gettext("Колбаски/день"),
        consumption_buns=gettext("Булочки/день"),
        coffee_arabika=gettext("Арабика/ост."),
        coffee_blend=gettext("Бленд/ост."),
        milk=gettext("Молоко/ост."),
        panini=gettext("Панини/ост."),
        sausages=gettext("Колбаски/ост."),
        buns=gettext("Булочки/ост."),
        expenses=gettext("Расходы"),
    )
    form_extra_fields = {"backdating": BooleanField(gettext("Обработка задним числом"))}
    form_create_rules = (
        "backdating",
        "timestamp",
        "expenses",
        "cashless",
        "actual_balance",
        "coffee_arabika",
        "coffee_blend",
        "milk",
        "panini",
        "sausages",
        "buns",
        "shop",
        "barista",
    )
    form_edit_rules = (
        "backdating",
        "timestamp",
        "expenses",
        "cashbox",
        "remainder_of_day",
        "cashless",
        "cash_balance",
        "actual_balance",
        "consumption_coffee_arabika",
        "consumption_coffee_blend",
        "consumption_milk",
        "consumption_panini",
        "consumption_sausages",
        "consumption_buns",
        "coffee_arabika",
        "coffee_blend",
        "milk",
        "panini",
        "sausages",
        "buns",
        "shop",
        "barista",
    )
    form_args = dict(
        timestamp=dict(validators=[DataRequired()], format="%d.%m.%Y %H:%M"),
        last_edit=dict(validators=[DataRequired()], format="%d.%m.%Y %H:%M"),
        shop=dict(validators=[DataRequired(message=gettext("Выберите кофейню"))]),
        barista=dict(validators=[DataRequired(message=gettext("Выберите сотрудника"))]),
        cashbox=dict(
            validators=[
                InputRequired(),
                NumberRange(
                    min=0,
                    max=1000000000,
                    message=gettext("Сумма не может быть нулевой, либо ниже нуля"),
                ),
            ]
        ),
        remainder_of_day=dict(
            validators=[
                InputRequired(),
                NumberRange(
                    min=0,
                    max=1000000000,
                    message=gettext("Сумма не может быть нулевой, либо ниже нуля"),
                ),
            ]
        ),
        cashless=dict(
            validators=[
                InputRequired(),
                NumberRange(
                    min=0,
                    max=1000000000,
                    message=gettext("Сумма не может быть нулевой, либо ниже нуля"),
                ),
            ]
        ),
        cash_balance=dict(
            validators=[
                InputRequired(),
                NumberRange(
                    min=0,
                    max=1000000000,
                    message=gettext("Сумма не может быть нулевой, либо ниже нуля"),
                ),
            ]
        ),
        actual_balance=dict(
            validators=[
                InputRequired(),
                NumberRange(
                    min=0,
                    max=1000000000,
                    message=gettext("Сумма не может быть нулевой, либо ниже нуля"),
                ),
            ]
        ),
        consumption_coffee_arabika=dict(
            default=0.0,
            validators=[
                InputRequired(),
                NumberRange(
                    min=-0.0001,
                    max=1000000000.0,
                    message=gettext("Расход за день не может быть ниже нуля"),
                ),
            ],
        ),
        consumption_coffee_blend=dict(
            default=0.0,
            validators=[
                InputRequired(),
                NumberRange(
                    min=-0.0001,
                    max=1000000000.0,
                    message=gettext("Расход за день не может быть ниже нуля"),
                ),
            ],
        ),
        consumption_milk=dict(
            default=0.0,
            validators=[
                InputRequired(),
                NumberRange(
                    min=-0.0001,
                    max=1000000000.0,
                    message=gettext("Расход за день не может быть ниже нуля"),
                ),
            ],
        ),
        consumption_panini=dict(
            default=0,
            validators=[
                InputRequired(),
                NumberRange(
                    min=-1,
                    max=1000000000,
                    message=gettext("Расход за день не может быть ниже нуля"),
                ),
            ],
        ),
        consumption_sausages=dict(
            default=0,
            validators=[
                InputRequired(),
                NumberRange(
                    min=-1,
                    max=1000000000,
                    message=gettext("Расход за день не может быть ниже нуля"),
                ),
            ],
        ),
        consumption_buns=dict(
            default=0,
            validators=[
                InputRequired(),
                NumberRange(
                    min=-1,
                    max=1000000000,
                    message=gettext("Расход за день не может быть ниже нуля"),
                ),
            ],
        ),
        coffee_arabika=dict(
            validators=[
                InputRequired(),
                NumberRange(
                    min=-0.0001,
                    max=1000000000.0,
                    message=gettext(
                        "Остаток арабики должен быть нулевым, либо больше нуля"
                    ),
                ),
            ]
        ),
        coffee_blend=dict(
            validators=[
                InputRequired(),
                NumberRange(
                    min=-0.0001,
                    max=1000000000.0,
                    message=gettext(
                        "Остаток купажа должен быть нулевым, либо больше нуля"
                    ),
                ),
            ]
        ),
        milk=dict(
            validators=[
                InputRequired(),
                NumberRange(
                    min=-0.0001,
                    max=1000000000.0,
                    message=gettext(
                        "Остаток молока должен быть нулевым, либо больше нуля"
                    ),
                ),
            ]
        ),
        panini=dict(
            validators=[
                InputRequired(),
                NumberRange(
                    min=-1,
                    max=1000000000,
                    message=gettext(
                        "Остаток панини должен быть нулевым, либо больше нуля"
                    ),
                ),
            ]
        ),
        sausages=dict(
            validators=[
                InputRequired(),
                NumberRange(
                    min=-1,
                    max=1000000000,
                    message=gettext(
                        "Остаток колбасок должен быть нулевым, либо больше нуля"
                    ),
                ),
            ]
        ),
        buns=dict(
            validators=[
                InputRequired(),
                NumberRange(
                    min=-1,
                    max=1000000000,
                    message=gettext(
                        "Остаток булочек должен быть нулевым, либо больше нуля"
                    ),
                ),
            ]
        ),
    )
    form_widget_args = {
        "timestamp": {
            "placeholder": gettext("Дата и время отправки отчета"),
            "data-date-format": "DD.MM.YYYY HH:mm",
        },
        "last_edit": {"data-date-format": "DD.MM.YYYY HH:mm"},
        "expenses": {"placeholder": gettext("Расходы за день")},
        "cashbox": {"placeholder": gettext("Касса")},
        "remainder_of_day": {
            "placeholder": gettext("Остаток дня, сумма остатка наличности и безнала")
        },
        "cashless": {"placeholder": gettext("Безнал")},
        "cash_balance": {
            "placeholder": gettext(
                "Разница между утренним фактическим остатком и вечерним"
            )
        },
        "actual_balance": {
            "placeholder": gettext("Фактический остаток наличности вечером")
        },
        "consumption_coffee_arabika": {
            "placeholder": gettext("Расход арабики в кг за день")
        },
        "consumption_coffee_blend": {
            "placeholder": gettext("Расход купажа в кг за день")
        },
        "consumption_milk": {"placeholder": gettext("Расход молока в л за день")},
        "consumption_panini": {"placeholder": gettext("Расход панини за день")},
        "consumption_sausages": {"placeholder": gettext("Расход колбасок за день")},
        "consumption_buns": {"placeholder": gettext("Расход булочек за день")},
        "coffee_arabika": {
            "placeholder": gettext("Количество арабики в кг, остаток на следующий день")
        },
        "coffee_blend": {
            "placeholder": gettext("Количество купажа в кг, остаток на следующий день")
        },
        "milk": {
            "placeholder": gettext("Количество молока в л, остаток на следующий день")
        },
        "panini": {
            "placeholder": gettext("Количество панини, остаток на следующий день")
        },
        "sausages": {
            "placeholder": gettext("Количество колбасок, остаток на следующий день")
        },
        "buns": {"placeholder": gettext("Количество булок, остаток на следующий день")},
    }

    products = ("coffee_arabika", "coffee_blend", "milk", "panini", "sausages", "buns")

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
        _query = self.session.query(func.sum(Report.__dict__[attr])).scalar()
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
        _query = self.session.query(func.avg(Report.__dict__[attr])).scalar()
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
        render_fields = (
            "cashbox",
            "cash_balance",
            "remainder_of_day",
            "cashless",
            "actual_balance",
        )
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
            new_remainder_of_day, old_remainder_of_day = (
                form.remainder_of_day.data,
                model.remainder_of_day,
            )
            new_cash_balance, old_cash_balance = (
                form.cash_balance.data,
                model.cash_balance,
            )
            new_cashless, old_cashless = form.cashless.data, model.cashless
            new_actual_balance, old_actual_balance = (
                form.actual_balance.data,
                model.actual_balance,
            )
            new_expenses = sum(
                [e.money for e in form.expenses.data if e.type_cost == "cash"]
            )
            expenses_data = form.expenses.data
            old_expenses = sum(
                [e.money for e in model.expenses if e.type_cost == "cash"]
            )

            new_consumption_coffee_arabika = form.consumption_coffee_arabika.data
            old_consumption_coffee_arabika = model.consumption_coffee_arabika

            new_consumption_coffee_blend = form.consumption_coffee_blend.data
            old_consumption_coffee_blend = model.consumption_coffee_blend

            new_consumption_milk = form.consumption_milk.data
            old_consumption_milk = model.consumption_milk

            new_consumption_panini = form.consumption_panini.data
            old_consumption_panini = model.consumption_panini

            new_consumption_sausages = form.consumption_sausages.data
            old_consumption_sausages = model.consumption_sausages

            new_consumption_buns = form.consumption_buns.data
            old_consumption_buns = model.consumption_buns

            new_coffee_arabika = form.coffee_arabika.data
            old_coffee_arabika = model.coffee_arabika

            new_coffee_blend = form.coffee_blend.data
            old_coffee_blend = model.coffee_blend

            new_milk = form.milk.data
            old_milk = model.milk

            new_panini = form.panini.data
            old_panini = model.panini

            new_sausages = form.sausages.data
            old_sausages = model.sausages

            new_buns = form.buns.data
            old_buns = model.buns

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
            if new_remainder_of_day != old_remainder_of_day:
                form.remainder_of_day.data = old_remainder_of_day

            if new_cash_balance != old_cash_balance:
                form.cash_balance.data = old_cash_balance

            if new_cashless != old_cashless:
                form.cashless.data = old_cashless

            if new_expenses != old_expenses:
                form.expenses.data = expenses_data

            if new_actual_balance != old_actual_balance:
                form.actual_balance.data = old_actual_balance

            if new_consumption_coffee_arabika != old_consumption_coffee_arabika:
                form.consumption_coffee_arabika.data = old_consumption_coffee_arabika

            if new_consumption_coffee_blend != old_consumption_coffee_blend:
                form.consumption_coffee_blend.data = old_consumption_coffee_blend

            if new_consumption_milk != old_consumption_milk:
                form.consumption_milk.data = old_consumption_milk

            if new_consumption_panini != old_consumption_panini:
                form.consumption_panini.data = old_consumption_panini

            if new_consumption_sausages != old_consumption_sausages:
                form.consumption_sausages.data = old_consumption_sausages

            if new_consumption_buns != old_consumption_buns:
                form.consumption_buns.data = old_consumption_buns

            if new_coffee_arabika != old_coffee_arabika:
                form.coffee_arabika.data = old_coffee_arabika

            if new_coffee_blend != old_coffee_blend:
                form.coffee_blend.data = old_coffee_blend

            if new_milk != old_milk:
                form.milk.data = old_milk

            if new_panini != old_panini:
                form.panini.data = old_panini

            if new_sausages != old_sausages:
                form.sausages.data = old_sausages

            if new_buns != old_buns:
                form.buns.data = old_buns
            self.after_model_change(form, model, False)
        return True

    @staticmethod
    def weight_count(model, get_sum=False):
        """Weight counts by product_name, or return weight sum"""
        day_by_weight = ByWeight.get_local_by_shop(model.shop.id)
        by_weight = sum([e.money for e in day_by_weight if e.type_cost == "cash"])

        def weight_amount(product_name):
            weight = [w.amount for w in day_by_weight if w.product_name == product_name]
            return sum(weight)

        if get_sum:
            return by_weight
        return weight_amount

    def on_model_change(self, form, model, is_created):
        """Work with model after create"""
        expanses = form.expenses.data
        expanses = sum([e.money for e in expanses if e.type_cost == "cash"])
        by_weight = self.weight_count(model, get_sum=True)
        last_actual_balance = model.shop.cash + expanses - by_weight
        model.cash_balance = form.actual_balance.data - last_actual_balance
        model.remainder_of_day = model.cash_balance + form.cashless.data
        model.cashbox = model.remainder_of_day + expanses

        if form.backdating.data:
            model.backdating = form.backdating.data
            return
        model.shop.cash += model.cash_balance + expanses - by_weight
        model.shop.cashless += model.cashless
        weight_amount = self.weight_count(model)
        for product in ReportAdmin.products:
            if product in ["panini", "sausages", "buns"]:
                consumption_value = (
                    getattr(model.shop.storage, product)
                    - int(getattr(form, product).data)
                    + weight_amount(product)
                )
            else:
                consumption_value = (
                    getattr(model.shop.storage, product)
                    - float(getattr(form, product).data)
                    + weight_amount(product)
                )
            setattr(model, f"consumption_{product}", consumption_value)
            consumption_to_storage = getattr(model.shop.storage, product) - getattr(
                model, f"consumption_{product}"
            )
            setattr(model.shop.storage, product, consumption_to_storage)

    def after_model_change(self, form, model, is_created):
        """Work with model after change"""
        if form.backdating.data:
            return
        if not is_created:
            model.last_edit = datetime.utcnow()
            expanses = model.expenses
            expanses = sum([e.money for e in expanses if e.type_cost == "cash"])
            diff_actual_balance = model.actual_balance - form.actual_balance.data
            model.cash_balance = form.cash_balance.data + diff_actual_balance
            model.remainder_of_day = model.cash_balance + model.cashless
            model.cashbox = model.remainder_of_day + expanses
            model.shop.cashless -= form.cashless.data

            if float(form.consumption_coffee_arabika.data):
                model.consumption_coffee_arabika += float(
                    form.consumption_coffee_arabika.data
                )
            if float(form.consumption_coffee_blend.data):
                model.consumption_coffee_blend += float(
                    form.consumption_coffee_blend.data
                )
            if int(form.consumption_milk.data):
                model.consumption_milk += int(form.consumption_milk.data)
            if int(form.consumption_panini.data):
                model.consumption_panini += int(form.consumption_panini.data)
            if int(form.consumption_sausages.data):
                model.consumption_sausages += int(form.consumption_sausages.data)
            if int(form.consumption_buns.data):
                model.consumption_buns += int(form.consumption_buns.data)
            self.session.commit()

    def on_model_delete(self, model):
        """Work with model after delete"""
        if model.backdating:
            return
        if model.shop:
            by_weight = self.weight_count(model, get_sum=True)
            model.shop.cash -= model.cash_balance - by_weight
            model.shop.cashless -= model.cashless

            for product in ReportAdmin.products:
                consumption_to_storage = getattr(model.shop.storage, product) + getattr(
                    model, f"consumption_{product}"
                )
                setattr(model.shop.storage, product, consumption_to_storage)
