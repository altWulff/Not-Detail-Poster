"""
Module contains admin view for Role model
"""

from flask_admin.babel import gettext
from flask_security import current_user
from wtforms.validators import DataRequired

from . import ModelView


class RoleAdmin(ModelView):
    """Role model view"""

    can_delete = False
    can_create = False
    column_labels = dict(
        name=gettext("Название"),
        description=gettext("Описание"),
        barista=gettext("Бариста"),
    )
    column_formatters = dict(name=lambda v, c, m, p: m.name.title())
    form_args = dict(
        name=dict(validators=[DataRequired()]),
    )

    @property
    def can_edit(self):
        """Editing depends on role"""
        is_admin = current_user.has_role("admin")
        is_active = current_user.is_active and current_user.is_authenticated

        if is_active and is_admin:
            return True
        return False
