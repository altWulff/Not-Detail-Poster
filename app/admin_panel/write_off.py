from statistics import median
from datetime import datetime
from sqlalchemy import func
from flask import flash, Markup
from flask_admin.babel import gettext
from flask_security import current_user
from wtforms import SelectField, BooleanField
from wtforms.validators import DataRequired, Required, NumberRange
from app.models import Barista, WriteOff
from . import ModelView, log


class WriteOffAdmin(ModelView):
    def _list_amount(view, context, model, name):
        if not model.amount:
            return ''
        if model.product_name == 'milk':
            formatter = f'{model.amount} л'
        elif model.product_name == 'coffee_arabika' or model.product_name == 'coffee_blend':
            formatter = f'{model.amount} кг'
        else:
            formatter = f'{model.amount} шт.'
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

    list_template = 'admin/model/write_off_list.html'
    can_view_details = True
    can_set_page_size = True
    column_list = ('timestamp', 'product_name', 'amount', 'storage')
    column_labels = dict(
        timestamp=gettext('Дата'),
        last_edit=gettext('Последнее изменение'),
        backdating=gettext('Обработка задним числом'),
        product_name=gettext('Название товара'),
        amount=gettext('Количество'),
        storage=gettext('Склад'),
        barista=gettext('Бариста')
    )
    column_searchable_list = (WriteOff.timestamp, )
    column_filters = ('timestamp', 'product_name', Barista.name)
    column_formatters = dict(
        timestamp=lambda v, c, m, p: m.timestamp.date().strftime("%d.%m.%Y"),
        product_name=_list_product_name,
        amount=_list_amount
    )
    form_create_rules = ('backdating', 'timestamp', 'product_name', 'amount', 'storage', 'barista')
    form_edit_rules = ('backdating', 'timestamp', 'product_name', 'amount', 'storage', 'barista')
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
                    max=1000000000,
                    message=gettext('Количество не может быть нулевым, либо ниже нуля')
                )
            ]
        ),
        storage=dict(
            validators=[DataRequired(message=gettext('Выберите склад'))]
        )
    )
    form_extra_fields = dict(
        backdating=BooleanField(gettext('Обработка задним числом')),
        product_name=SelectField(
            gettext('Название товара'),
            choices=[
                ('coffee_arabika', gettext('Арабика')),
                ('coffee_blend', gettext('Купаж')),
                ('milk', gettext('Молоко')),
                ('panini', gettext('Панини')),
                ('sausages', gettext('Колбаски')),
                ('buns', gettext('Булочки'))
            ],
            validators=[Required()],
        )
    )
    form_widget_args = {
        'timestamp': {
            'data-date-format': u'DD.MM.YYYY HH:mm'
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
        _query = self.session.query(func.sum(WriteOff.__dict__[attr])).scalar()
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
        _query = self.session.query(func.avg(WriteOff.__dict__[attr])).scalar()
        try:
            return round(_query)
        except:
            return 0

    def render(self, template, **kwargs):
        if template == 'admin/model/write_off_list.html':
            _current_page = kwargs['page']
            kwargs['column_labels'] = self.column_labels
            kwargs['summary_data'] = {
                'on_page': {
                    'amount': self.sum_page('amount')
                },
                'total': {
                    'amount': self.sum_total('amount')

                }
            }
            kwargs['median_data'] = {
                'on_page': {
                    'amount': self.median_page('amount')
                },
                'total': {
                    'amount': self.median_total('amount')
                }
            }

        return super(WriteOffAdmin, self).render(template, **kwargs)

    def create_form(self, obj=None):
        form = super(WriteOffAdmin, self).create_form(obj)
        form.timestamp.data = datetime.utcnow()
        form.barista.data = current_user
        return form

    def update_model(self, form, model):
        try:
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
        elif form.product_name.data == 'coffee_arabika':
            model.storage.coffee_arabika -= float(form.amount.data)
        elif form.product_name.data == 'milk':
            model.storage.milk -= float(form.amount.data)
        elif form.product_name.data == 'panini':
            model.storage.panini -= int(form.amount.data)
        elif form.product_name.data == 'sausages':
            model.storage.sausages -= int(form.amount.data)
        else:
            model.storage.buns -= int(form.amount.data)

    def after_model_change(self, form, model, is_created):
        if form.backdating.data:
            return
        if not is_created:
            model.last_edit = datetime.utcnow()
            if form.product_name.data == 'coffee_blend':
                model.storage.coffee_blend += float(form.amount.data)
            elif form.product_name.data == 'coffee_arabika':
                model.storage.coffee_arabika += float(form.amount.data)
            elif form.product_name.data == 'milk':
                model.storage.milk += float(form.amount.data)
            elif form.product_name.data == 'panini':
                model.storage.panini += int(form.amount.data)
            elif form.product_name.data == 'sausages':
                model.storage.sausages += int(form.amount.data)
            else:
                model.storage.buns += int(form.amount.data)
            self.session.commit()

    def on_model_delete(self, model):
        if model.backdating:
            return
        if model.product_name == 'coffee_blend':
            model.storage.coffee_blend += model.amount
        elif model.product_name == 'coffee_arabika':
            model.storage.coffee_arabika += model.amount
        elif model.product_name == 'milk':
            model.storage.milk += model.amount
        elif model.product_name == 'panini':
            model.storage.panini += model.amount
        elif model.product_name == 'sausages':
            model.storage.sausages += model.amount
        else:
            model.storage.buns += model.amount
