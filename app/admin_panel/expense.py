from statistics import median
from datetime import datetime
from sqlalchemy import func
from flask import flash, Markup
from flask_admin.babel import gettext
from flask_security import current_user
from wtforms import BooleanField, RadioField
from wtforms.validators import DataRequired, Required, NumberRange, InputRequired
from app.models import Shop, Barista, Expense
from . import ModeratorView, log


class ExpenseAdmin(ModeratorView):
    def _list_money(view, context, model, name):
        if not model.money:
            return ''
        type_cost = '' if model.type_cost == 'cash' else ' (Безнал)'
        formatter = f'{model.money} грн.{type_cost}'
        return Markup(f'{formatter}')

    list_template = 'admin/model/expense_list.html'
    can_set_page_size = True
    column_list = ('timestamp', 'money', 'is_global', 'categories', 'shop')
    form_create_rules = (
        'backdating',
        'timestamp',
        'is_global',
        'type_cost',
        'money',
        'categories',
        'shop',
        'barista'
    )
    form_edit_rules = (
        'backdating',
        'timestamp',
        'is_global',
        'type_cost',
        'money',
        'categories',
        'shop'
    )
    column_filters = (
        'timestamp',
        'is_global',
        'type_cost',
        'categories',
        Shop.place_name,
        Shop.address,
        Barista.name
    )
    column_searchable_list = (Expense.timestamp, )
    column_labels = dict(
        category=gettext('Категория'),
        timestamp=gettext('Дата'),
        last_edit=gettext('Последнее изменение'),
        is_global=gettext('Глобальная?'),
        type_cost=gettext('Тип траты'),
        money=gettext('Сумма траты'),
        categories=gettext('Категории'),
        shop=gettext('Кофейня'),
        barista=gettext('Бариста')
    )
    can_view_details = True
    column_default_sort = ('timestamp', True)
    column_formatters = dict(
        type_cost=lambda v, c, m, p: 'Наличка' if m.type_cost == 'cash' else 'Безнал',
        is_global=lambda v, c, m, p: 'Да' if m.is_global else 'Нет',
        money=_list_money
    )
    form_extra_fields = {
        'backdating': BooleanField('Обработка задним числом'),
        'type_cost': RadioField(
            gettext('Тип траты'),
            default='cash',
            choices=[
                ('cash', gettext('Наличка')),
                ('cashless', gettext('Безнал'))
            ],
            validators=[Required()]
        )
    }
    form_widget_args = {
        'timestamp': {
            'data-date-format': u'DD.MM.YYYY HH:mm'
        },
        'money': {
            'placeholder': gettext('В гривнях')
        },
        'type_cost': {
            'class': 'form-check'
        }
    }
    form_ajax_refs = {
        'categories': {
            'fields': ('name',),
            'placeholder': gettext('Добавить категорию'),
            'page_size': 10,
            'minimum_input_length': 0,
        },
        'shop': {
            'fields': ('place_name', 'address'),
            'placeholder': gettext('Кофейня'),
            'page_size': 10,
            'minimum_input_length': 0,
        }
    }
    form_args = dict(
        timestamp=dict(
            validators=[DataRequired()],
            format='%d.%m.%Y %H:%M'
        ),
        money=dict(
            validators=[
                InputRequired(),
                NumberRange(
                    min=0,
                    max=1000000000,
                    message=gettext('Сумма не может быть нулевой, либо ниже нуля')
                )
            ]
        ),
        shop=dict(
            validators=[
                DataRequired(
                    message=gettext('Выберите кофейню')
                )
            ]
        )
    )
    
    @property 
    def shop_id(self):
        return self.model.shop_id

    def sum_page(self, attr: str) -> int:
        _query = self.get_model_data()
        try:
            return sum([p.__dict__[attr] for p in _query if p])
        except:
            return 0

    def sum_total(self, attr: str) -> int:
        _query = self.session.query(func.sum(Expense.__dict__[attr])).scalar()
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
        _query = self.session.query(func.avg(Expense.__dict__[attr])).scalar()
        try:
            return round(_query)
        except:
            return 0

    def render(self, template, **kwargs):
        if template == 'admin/model/expense_list.html':
            _current_page = kwargs['page']
            kwargs['column_labels'] = self.column_labels
            kwargs['summary_data'] = {
                'on_page': {
                    'money': self.sum_page('money')
                },
                'total': {
                    'money': self.sum_total('money')
                }
            }
            kwargs['median_data'] = {
                'on_page': {
                    'money': self.median_page('money')
                },
                'total': {
                    'money': self.median_total('money')
                }
            }

        return super(ExpenseAdmin, self).render(template, **kwargs)

    def create_form(self, obj=None):
        form = super(ExpenseAdmin, self).create_form(obj)
        form.timestamp.data = datetime.now()
        form.barista.data = current_user
        return form

    def update_model(self, form, model):
        try:
            new_money, old_money = form.money.data, model.money
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
            self.after_model_change(form, model, False)
        return True

    def on_model_change(self, form, model, is_created):
        if form.backdating.data:
            model.backdating = form.backdating.data
            return
        money = model.money
        if model.type_cost == 'cash':
            model.shop.cash -= money
        else:
            model.shop.cashless -= money

    def after_model_change(self, form, model, is_created):
        if form.backdating.data:
            return
        if not is_created:
            model.last_edit = datetime.now()
            if form.type_cost.data == 'cash':
                model.shop.cash += form.money.data
            else:
                model.shop.cashless += form.money.data
            self.session.commit()

    def on_model_delete(self, model):
        if model.backdating:
            return
        if model.type_cost and model.money and model.shop:
            if model.type_cost == 'cash':
                model.shop.cash += model.money
            else:
                model.shop.cashless += model.money
