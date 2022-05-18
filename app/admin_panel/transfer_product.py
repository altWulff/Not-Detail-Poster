"""
Module contains admin view for TransferProduct model
"""


from datetime import datetime

from flask import Markup, flash
from flask_admin.babel import gettext
from flask_security import current_user
from sqlalchemy import or_
from wtforms import SelectField
from wtforms.validators import DataRequired, Required

from app.models import Barista, Shop

from . import ModelView, log
from .exceptions import FailedUpdateException


class TransferProductAdmin(ModelView):
    """TransferProduct model view"""

    @staticmethod
    def _list_product_name(context, model, name):
        del context, name
        prettified = dict(
            coffee_arabika=gettext("арабика"),
            coffee_blend=gettext("купаж"),
            milk=gettext("молоко"),
            panini=gettext("панини"),
            sausages=gettext("колбаски"),
            buns=gettext("булочки"),
        )
        return Markup(f"{prettified[model.product_name]}")

    @staticmethod
    def _list_amount(context, model, name):
        del context, name
        if not model.amount:
            return ""
        if model.product_name == "milk":
            formatter = f"{model.amount} л"
        elif model.product_name in ("coffee_arabika", "coffee_blend"):
            formatter = f"{model.amount} кг"
        else:
            formatter = f"{model.amount} шт."
        return Markup(f"{formatter}")

    can_edit = False
    can_view_details = True
    can_set_page_size = True
    column_list = (
        "timestamp",
        "where_shop",
        "to_shop",
        "product_name",
        "amount",
        "barista",
    )
    column_filters = ("timestamp", "where_shop", "to_shop", Barista.name)
    column_formatters = dict(
        product_name=_list_product_name,
        amount=_list_amount,
        where_shop=lambda v, c, m, p: Shop.query.filter_by(id=m.where_shop).first(),
        to_shop=lambda v, c, m, p: Shop.query.filter_by(id=m.to_shop).first(),
    )
    column_labels = dict(
        timestamp=gettext("Дата"),
        last_edit=gettext("Последнее изменение"),
        where_shop=gettext("Место откуда перемещено"),
        to_shop=gettext("Место куда перемещено"),
        backdating=gettext("Обработка задним числом"),
        product_name=gettext("Название товара"),
        amount=gettext("Количество"),
        barista=gettext("Бариста"),
    )

    form_create_rules = (
        "backdating",
        "timestamp",
        "where_shop",
        "to_shop",
        "product_name",
        "amount",
        "barista",
    )
    form_edit_rules = (
        "backdating",
        "timestamp",
        "where_shop",
        "to_shop",
        "product_name",
        "amount",
        "barista",
    )
    form_widget_args = {
        "timestamp": {"data-date-format": "DD.MM.YYYY HH:mm"},
        "last_edit": {"data-date-format": "DD.MM.YYYY HH:mm"},
    }
    form_args = dict(
        product_name=dict(validators=[Required()]),
        amount=dict(validators=[Required()]),
        timestamp=dict(validators=[DataRequired()], format="%d.%m.%Y %H:%M"),
        last_edit=dict(validators=[DataRequired()], format="%d.%m.%Y %H:%M"),
    )
    form_extra_fields = {
        "where_shop": SelectField(
            gettext("Место откуда перемещено"), validators=[Required()]
        ),
        "to_shop": SelectField(
            gettext("Место куда перемещено"), validators=[Required()]
        ),
        "product_name": SelectField(
            gettext("Название товара"), validators=[Required()]
        ),
    }

    @staticmethod
    def staff_shops_id():
        """Get shop list by current_user"""
        shop_ids = (str(shop.id) for shop in current_user.shop)
        return shop_ids

    def get_query(self):
        """Query for the model"""
        where_shop_id = self.model.where_shop
        to_shop_id = self.model.to_shop
        _query = super().get_query()
        if not current_user.has_role("admin"):
            _query = _query.filter(
                or_(
                    where_shop_id.in_(self.staff_shops_id()),
                    to_shop_id.in_(self.staff_shops_id()),
                )
            )
        return _query

    def get_count_query(self):
        """Count query for the model"""
        where_shop_id = self.model.where_shop
        to_shop_id = self.model.to_shop
        _query = super().get_count_query()
        if not current_user.has_role("admin"):
            _query = _query.filter(
                or_(
                    where_shop_id.in_(self.staff_shops_id()),
                    to_shop_id.in_(self.staff_shops_id()),
                )
            )
        return _query

    def create_form(self, obj=None):
        """Before create form"""
        form = super().create_form(obj)
        form.timestamp.data = datetime.utcnow()
        form.barista.data = current_user
        form.where_shop.choices = [(c.id, c) for c in Shop.query.all()]
        form.to_shop.choices = [(c.id, c) for c in Shop.query.all()]
        form.product_name.choices = [
            ("coffee_arabika", gettext("Арабика")),
            ("coffee_blend", gettext("Купаж")),
            ("milk", gettext("Молоко")),
            ("panini", gettext("Панини")),
            ("sausages", gettext("Колбаски")),
            ("buns", gettext("Булочки")),
        ]
        return form

    def update_model(self, form, model):
        """Update model with save previous state"""
        try:
            new_where_shop, old_where_shop = form.where_shop.data, model.where_shop
            new_to_shop, old_to_shop = form.to_shop.data, model.to_shop
            new_product_name, old_product_name = (
                form.product_name.data,
                model.product_name,
            )
            new_amount, old_amount = form.amount.data, model.amount
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
            if new_where_shop != old_where_shop:
                form.where_shop.data = old_where_shop
            if new_to_shop != old_to_shop:
                form.to_shop.data = old_to_shop
            if new_product_name != old_product_name:
                form.product_name.data = old_product_name
            if new_amount != old_amount:
                form.amount.data = old_amount

            self.after_model_change(form, model, False)
        return True

    def on_model_change(self, form, model, is_created):
        """Work with model after create"""
        if form.backdating.data:
            model.backdating = form.backdating.data
            return
        where_shop = Shop.query.filter_by(id=form.where_shop.data).first()
        to_shop = Shop.query.filter_by(id=form.to_shop.data).first()

        if form.product_name.data == "coffee_blend":
            where_shop.storage.coffee_blend -= float(form.amount.data)
        elif form.product_name.data == "coffee_arabika":
            where_shop.storage.coffee_arabika -= float(form.amount.data)
        elif form.product_name.data == "milk":
            where_shop.storage.milk -= float(form.amount.data)
        elif form.product_name.data == "panini":
            where_shop.storage.panini -= int(form.amount.data)
        elif form.product_name.data == "sausages":
            where_shop.storage.sausages -= int(form.amount.data)
        else:
            where_shop.storage.buns -= int(form.amount.data)

        if form.product_name.data == "coffee_blend":
            to_shop.storage.coffee_blend += float(form.amount.data)
        elif form.product_name.data == "coffee_arabika":
            to_shop.storage.coffee_arabika += float(form.amount.data)
        elif form.product_name.data == "milk":
            to_shop.storage.milk += float(form.amount.data)
        elif form.product_name.data == "panini":
            to_shop.storage.panini += int(form.amount.data)
        elif form.product_name.data == "sausages":
            to_shop.storage.sausages += int(form.amount.data)
        else:
            to_shop.storage.buns += int(form.amount.data)

    def after_model_change(self, form, model, is_created):
        """Work with model after change"""
        if form.backdating.data:
            return

    def on_model_delete(self, model):
        """Work with model after delete"""
        if model.backdating:
            return
        where_shop = Shop.query.filter_by(id=model.where_shop).first()
        to_shop = Shop.query.filter_by(id=model.to_shop).first()
        if where_shop:
            if model.product_name == "coffee_blend":
                where_shop.storage.coffee_blend += float(model.amount)
            elif model.product_name == "coffee_arabika":
                where_shop.storage.coffee_arabika += float(model.amount)
            elif model.product_name == "milk":
                where_shop.storage.milk += float(model.amount)
            elif model.product_name == "panini":
                where_shop.storage.panini += int(model.amount)
            elif model.product_name == "sausages":
                where_shop.storage.sausages += int(model.amount)
            else:
                where_shop.storage.buns += int(model.amount)
        if to_shop:
            if model.product_name == "coffee_blend":
                to_shop.storage.coffee_blend -= float(model.amount)
            elif model.product_name == "coffee_arabika":
                to_shop.storage.coffee_arabika -= float(model.amount)
            elif model.product_name == "milk":
                to_shop.storage.milk -= float(model.amount)
            elif model.product_name == "panini":
                to_shop.storage.panini -= int(model.amount)
            elif model.product_name == "sausages":
                to_shop.storage.sausages -= int(model.amount)
            else:
                to_shop.storage.buns -= int(model.amount)
