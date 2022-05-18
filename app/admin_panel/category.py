"""
Module contains admin view for Category model
"""


from flask_admin.babel import gettext
from wtforms.validators import DataRequired

from . import ModelView


class CategoryAdmin(ModelView):
    """Category model view"""

    can_view_details = True
    can_set_page_size = True
    column_labels = dict(name=gettext("Название категории"), expense=gettext("Расходы"))
    form_create_rules = ("name",)
    form_args = dict(name=dict(validators=[DataRequired()]))
    column_editable_list = ("name",)
    form_widget_args = {"name": {"placeholder": gettext("Название для расходов")}}
