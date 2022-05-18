"""
Module contains admin view for ShopEquipment model
"""

from datetime import datetime

from flask_admin.babel import gettext
from wtforms.validators import DataRequired, Length

from . import ModeratorView


class ShopEquipmentAdmin(ModeratorView):
    """ShopEquipment model view"""

    can_view_details = True
    column_searchable_list = ("coffee_machine",)
    column_labels = dict(
        coffee_machine=gettext("Кофе Машина"),
        last_cleaning_coffee_machine=gettext("Последняя чистка КМ"),
        grinder_1=gettext("Кофемолка 1"),
        grinder_2=gettext("Кофемолка 2"),
        last_cleaning_grinder=gettext("Последняя чистка кофемолок"),
        shop=gettext("Кофейня"),
    )
    form_args = dict(
        coffee_machine=dict(validators=[DataRequired(), Length(max=25)]),
        grinder_1=dict(validators=[DataRequired(), Length(max=25)]),
        grinder_2=dict(validators=[Length(max=25)]),
        shop=dict(validators=[DataRequired(message=gettext("Выберите кофейню"))]),
    )

    @property
    def shop_id(self):
        return self.model.shop_id

    def create_form(self, obj=None):
        """Before create form"""
        form = super().create_form(obj)
        form.last_cleaning_coffee_machine.data = datetime.utcnow()
        form.last_cleaning_grinder.data = datetime.utcnow()
        return form
