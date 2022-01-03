from statistics import median
from datetime import datetime
from sqlalchemy import func
from flask import flash, Markup
from flask_admin.babel import gettext
from flask_security import current_user
from wtforms import SelectField, BooleanField, RadioField
from wtforms.validators import DataRequired, Required, NumberRange, InputRequired
from app.models import Barista, ByWeight
from . import StorageModeratorView, log


class ByWeightAdmin(StorageModeratorView):
    def _list_amount(view, context, model, name):
        if not model.amount:
            return ''
        if model.product_name == 'milk':
            r = f'{model.amount} л'
        elif model.product_name == 'coffee_arabika' or model.product_name == 'coffee_blend':
            r = f'{model.amount} кг'
        else:
            r = f'{model.amount} шт.'
        return Markup(f'{r}')

    def _list_money(view, context, model, name):
        if not model.money:
            return ''
        type_cost = '' if model.type_cost == 'cash' else ' (Безнал)'
        formatter = f'{model.money} грн.{type_cost}'
        return Markup(f'{formatter}')

    def _list_product_name(view, context, model, name):
        prettified = dict(
            coffee_arabika=gettext('арабика'),
            coffee_blend=gettext('купаж'),
            milk=gettext('молоко'),
            panini=gettext('панини'),
            sausages=gettext('колбаски'),
            buns=gettext('булочки')
        )
        return Markup(f'{prettified[model.product_name]}')

    list_template = 'admin/model/by_weight_list.html'
    can_view_details = True
    can_set_page_size = True
    column_list = ('timestamp', 'product_name', 'amount', 'money', 'storage')
    column_labels = dict(
        timestamp=gettext('Дата'),
        last_edit=gettext('Последнее изменение'),
        backdating=gettext('Обработка задним числом'),
        product_name=gettext('Название товара'),
        amount=gettext('Количество'),
        type_cost=gettext('Тип траты'),
        money=gettext('Сумма'),
        storage=gettext('Склад'),
        barista=gettext('Бариста')
    )
    column_searchable_list = (ByWeight.timestamp, )
    column_filters = ('timestamp', 'type_cost', 'product_name', Barista.name)
    column_formatters = dict(
        type_cost=lambda v, c, m, p: 'Наличка' if m.type_cost == 'cash' else 'Безнал',
        product_name=_list_product_name,
        money=_list_money,
        amount=_list_amount
    )
    form_create_rules = (
        'backdating',
        'timestamp',
        'product_name',
        'amount',
        'type_cost',
        'money',
        'storage',
        'barista'
    )
    form_edit_rules = (
        'backdating',
        'timestamp',
        'product_name',
        'amount',
        'type_cost',
        'money',
        'storage',
        'barista'
    )
    form_args = dict(
        timestamp=dict(
            validators=[DataRequired()],
            format='%d.%m.%Y %H:%M'
        ),
        amount=dict(
            validators=[
                DataRequired(),
                NumberRange(
                    min=0.0001,
                    max=1000000000.0,
                    message=gettext('Количество не может быть нулевым, либо ниже нуля')
                )
            ]
        ),
        money=dict(
            validators=[
                InputRequired(),
                NumberRange(
                    min=-1,
                    max=1000000000,
                    message=gettext('Сумма не может быть нулевой, либо ниже нуля')
                )
            ]
        ),
        storage=dict(
            validators=[DataRequired(message=gettext('Выберите склад'))]
        )
    )
    form_extra_fields = dict(
        backdating=BooleanField(gettext('Обработка задним числом')),
        type_cost=RadioField(
            gettext('Тип траты'),
            choices=[
                ('cash', gettext('Наличка')),
                ('cashless', gettext('Безнал'))
            ],
            validators=[Required()],
            default='cash'
        ),
        product_name=SelectField(
            gettext('Название товара'),
            choices=[
                ('coffee_arabika', gettext('Арабика')),
                ('coffee_blend', gettext('Купаж'))
            ],
            validators=[Required()],
        )
    )
    form_widget_args = {
        'timestamp': {
            'data-date-format': u'DD.MM.YYYY HH:mm'
        },
        'money': {
            'placeholder': gettext('В гривнях')
        },
        'type_cost': {
            'class': 'form-check'
        },
        'amount': {
            'placeholder': gettext('Количество в кг, л, и поштучно')
        }
    }

    def sum_page(self, attr: str) -> int:
        _query = self.get_model_data()
        try:
            return sum([p.__dict__[attr] for p in _query if p])
        except:
            return 0

    def sum_total(self, attr: str) -> int:
        _query = self.session.query(func.sum(ByWeight.__dict__[attr])).scalar()
        try:
            return _query
        except:
            return 0

    def median_page(self, attr: str) -> int:
        _query = self.get_model_data()
        data = [p.__dict__[attr] for p in _query if p]
        try:
            return median(data)
        except:
            return 0

    def median_total(self, attr: str) -> int:
        _query = self.session.query(func.avg(ByWeight.__dict__[attr])).scalar()
        try:
            return round(_query)
        except:
            return 0

    def render(self, template, **kwargs):
        _current_page = kwargs['page']
        kwargs['column_labels'] = self.column_labels
        kwargs['summary_data'] = {'on_page': {}, 'total': {}}
        kwargs['median_data'] = {'on_page': {}, 'total': {}}
        render_fields = ('amount', 'money')
        for field in render_fields:
            kwargs['summary_data']['on_page'][field] = self.sum_page(field)
            kwargs['summary_data']['total'][field] = self.sum_total(field)
            kwargs['median_data']['on_page'][field] = self.median_page(field)
            kwargs['median_data']['total'][field] = self.median_total(field)
        return super(ByWeightAdmin, self).render(template, **kwargs)

    def create_form(self, obj=None):
        form = super(ByWeightAdmin, self).create_form(obj)
        form.timestamp.data = datetime.utcnow()
        form.barista.data = current_user
        return form

    def update_model(self, form, model):
        try:
            new_money = form.money.data
            old_money = model.money

            new_amount = form.amount.data
            old_amount = model.amount

            new_product_name = form.product_name.data
            old_product_name = model.product_name

            form.populate_obj(model)
            self._on_model_change(form, model, False)
            self.session.commit()
        except Exception as ex:
            if not self.handle_view_exception(ex):
                flash(gettext('Failed to update record. %(error)s', error=str(ex)), 'error')
                log.exception('Failed to update record.')

            self.session.rollback()

            return False
        else:
            if new_money != old_money:
                form.money.data = old_money
            if new_amount != old_amount:
                form.amount.data = old_amount
            if new_product_name != old_product_name:
                form.product_name.data = old_product_name
            self.after_model_change(form, model, False)
        return True

    def on_model_change(self, form, model, is_created):
        if form.backdating.data:
            model.backdating = form.backdating.data
            return

        if form.product_name.data == 'coffee_blend':
            model.storage.coffee_blend -= float(form.amount.data)
        else:
            model.storage.coffee_arabika -= float(form.amount.data)

        if form.type_cost.data == 'cash':
            model.storage.shop.cash += form.money.data
        else:
            model.storage.shop.cashless += form.money.data

    def after_model_change(self, form, model, is_created):
        if form.backdating.data:
            return
        if not is_created:
            model.last_edit = datetime.utcnow()
            if form.type_cost.data == 'cash':
                model.storage.shop.cash -= form.money.data
            else:
                model.storage.shop.cashless -= form.money.data

            if form.product_name.data == 'coffee_blend':
                model.storage.coffee_blend += float(form.amount.data)
            else:
                model.storage.coffee_arabika += float(form.amount.data)
            self.session.commit()

    def on_model_delete(self, model):
        if model.backdating:
            return
        if model.product_name == 'coffee_blend':
            model.storage.coffee_blend += float(model.amount)
        else:
            model.storage.coffee_arabika += float(model.amount)

        if model.type_cost == 'cash':
            model.storage.shop.cash -= model.money
        else:
            model.storage.shop.cashless -= model.money
