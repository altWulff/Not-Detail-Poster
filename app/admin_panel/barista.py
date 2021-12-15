from datetime import datetime
from flask_admin.babel import gettext
from flask_security import current_user
from wtforms.validators import DataRequired
from app.models import Shop
from . import ModelView


class BaristaAdmin(ModelView):
    column_filters = ('name', 'phone_number', 'email', Shop.place_name, Shop.address)
    column_searchable_list = ('name', 'phone_number', 'email')
    column_exclude_list = ('password_hash', 'reports', )
    column_labels = dict(
        place_name=gettext('Назавание'),
        address=gettext('Адрес'),
        name=gettext('Имя'),
        phone_number=gettext('Тел.'),
        email=gettext('Емейл'),
        shop=gettext('Кофейня'),
        reports=gettext('Отчеты'),
        active=gettext('Активный'),
        confirmed_at=gettext('Дата найма'),
        password_hash=gettext('Пароль'),
        roles=gettext('Роли, уровень доступа'),
        expenses=gettext('Расходы'),
        supplies=gettext('Поступления'),
        by_weights=gettext('Развес'),
        write_offs=gettext('Списания')
    )
    form_columns = (
        'name',
        'phone_number',
        'email',
        'password',
        'shop',
        'roles',
        'confirmed_at',
        'active',
        'reports',
        'expenses',
        'supplies',
        'by_weights',
        'write_offs'
    )
    form_create_rules = (
        'name',
        'phone_number',
        'email',
        'password',
        'shop',
        'confirmed_at',
        'active',
        'roles'
    )
    form_edit_rules = (
        'name',
        'phone_number',
        'email',
        'password',
        'shop',
        'confirmed_at',
        'active',
        'roles',
        'reports',
        'expenses',
        'supplies',
        'by_weights',
        'write_offs'
    )
    form_args = dict(
        name=dict(
            validators=[DataRequired()]
        ),
        confirmed_at=dict(
            default=datetime.now(),
            validators=[DataRequired()],
            format='%d.%m.%Y %H:%M'
        ),
        active=dict(default=True),
        roles=dict(
            validators=[
                DataRequired(
                    message=gettext('Выберите уровень доступа сотрудника')
                )
            ]
        ),
        password=dict(
            validators=[DataRequired()]
        )
    )
    form_widget_args = {
        'name': {
            'placeholder': gettext('Имя сотрудника')
        },
        'phone_number': {
            'placeholder': gettext('Мобильный телефон')
        },
        'email': {
            'placeholder': gettext('Емейл')
        },
        'password': {
            'placeholder': gettext('Пароль для входа')
        },
        'shop': {
            'placeholder': gettext('Выберите места работы сотрудника')
        },
        'roles': {
            'placeholder': gettext('Выберите уровень доступа для сотрудника')
        },
        'confirmed_at': {
            'data-date-format': u'DD.MM.YYYY HH:mm'
        },
    }

    @property
    def can_edit(self):
        is_admin = current_user.has_role('admin')
        is_active = current_user.is_active and current_user.is_authenticated

        if is_active and is_admin:
            return True
        return False
