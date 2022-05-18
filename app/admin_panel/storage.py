"""
Module contains admin view for Storage model
"""

from flask_admin.babel import gettext
from wtforms.validators import DataRequired, InputRequired, NumberRange

from app.models import Shop

from . import ModeratorView


class StorageAdmin(ModeratorView):
    """Storage model view"""

    column_labels = dict(
        place_name=gettext("Название"),
        address=gettext("Адрес"),
        coffee_arabika=gettext("Арабика"),
        coffee_blend=gettext("Бленд"),
        milk=gettext("Молоко"),
        panini=gettext("Панини"),
        sausages=gettext("Колбаски"),
        buns=gettext("Булочки"),
        shop=gettext("Кофейня"),
        supplies=gettext("Поступления"),
        by_weights=gettext("Развес"),
        write_offs=gettext("Списания"),
    )
    column_formatters = dict(
        coffee_arabika=lambda v, c, m, p: f"{m.coffee_arabika} кг",
        coffee_blend=lambda v, c, m, p: f"{m.coffee_blend} кг",
        milk=lambda v, c, m, p: f"{m.milk} л",
        panini=lambda v, c, m, p: f"{m.panini} шт.",
        sausages=lambda v, c, m, p: f"{m.sausages} шт.",
        buns=lambda v, c, m, p: f"{m.buns} шт.",
    )
    column_filters = (Shop.place_name, Shop.address)
    form_create_rules = (
        "coffee_arabika",
        "coffee_blend",
        "milk",
        "panini",
        "sausages",
        "buns",
        "shop",
    )
    form_edit_rules = (
        "coffee_arabika",
        "coffee_blend",
        "milk",
        "panini",
        "sausages",
        "buns",
        "shop",
    )
    form_args = dict(
        coffee_arabika=dict(
            validators=[
                InputRequired(),
                NumberRange(
                    min=-0.0001,
                    max=1000000000.0,
                    message=gettext(
                        "Количество арабики должно быть нулевым, либо больше нуля"
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
                        "Количество бленда должно быть нулевым, либо больше нуля"
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
                        "Количество молока должно быть нулевым, либо больше нуля"
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
                        "Количество панини должно быть нулевым, либо больше нуля"
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
                        "Количество колбасок должно быть нулевым, либо больше нуля"
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
                        "Количество булочек должно быть нулевым, либо больше нуля"
                    ),
                ),
            ]
        ),
        shop=dict(validators=[DataRequired(message=gettext("Выберите кофейню"))]),
    )
    form_widget_args = {
        "coffee_arabika": {"placeholder": gettext("Введите количество арабики в кг")},
        "coffee_blend": {"placeholder": gettext("Введите количество купажа в кг")},
        "milk": {"placeholder": gettext("Введите количество молока в л")},
        "panini": {"placeholder": gettext("Введите количество панини")},
        "sausages": {"placeholder": gettext("Введите количество колбасок")},
        "buns": {"placeholder": gettext("Введите количество булочек")},
    }

    @property
    def shop_id(self):
        return self.model.shop_id
