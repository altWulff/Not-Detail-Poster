from datetime import datetime
from flask_admin.babel import gettext
from wtforms.validators import DataRequired, NumberRange, InputRequired, Length
from . import ModelView


class ShopAdmin(ModelView):
    can_view_details = True
    column_searchable_list = ('place_name', 'address')
    column_labels = dict(
        place_name=gettext('Название'),
        address=gettext('Адрес'),
        timestamp=gettext('Дата создания'),
        cash=gettext('Наличка'),
        cashless=gettext('Безнал'),
        storage=gettext('Склад'),
        shop_equipment=gettext('Оборудование'),
        reports=gettext('Отчеты'),
        expenses=gettext('Расходы'),
        baristas=gettext('Баристы')
    )
    form_create_rules = ('place_name', 'address', 'timestamp', 'cash', 'cashless', 'storage', 'shop_equipment', 'baristas')
    form_edit_rules = ('place_name', 'address', 'timestamp', 'cash', 'cashless', 'storage', 'shop_equipment', 'baristas')
    form_args = dict(
        place_name=dict(
            validators=[DataRequired(), Length(max=25)]
        ),
        address=dict(
            validators=[DataRequired(), Length(max=25)]
        ),
        cash=dict(
            validators=[
                InputRequired(),
                NumberRange(
                    min=-1,
                    max=1000000000,
                    message=gettext('Сумма должна быть нулевой, либо больше нуля')
                )
            ]
        ),
        cashless=dict(
            validators=[
                InputRequired(),
                NumberRange(
                    min=-1,
                    max=1000000000,
                    message=gettext('Сумма должна быть нулевой, либо больше нуля')
                )
            ]
        ),

    )
    form_widget_args = {
        'place_name': {
            'placeholder': gettext('Название кофейни')
        },
        'address': {
            'placeholder': gettext('Адрес кофейни')
        },
        'cash': {
            'placeholder': gettext('Наличка в гривне')
        },
        'cashless': {
            'placeholder': gettext('Безнал в гривне')
        }
    }

    def create_form(self, obj=None):
        form = super(ShopAdmin, self).create_form(obj)
        form.timestamp.data = datetime.now()
        return form
