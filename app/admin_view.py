from statistics import median
from datetime import datetime, date
from sqlalchemy import func
from flask import abort, redirect, request, url_for
from flask_security import current_user
from flask_admin.contrib import sqla
from flask_admin.base import expose
from app.models import Report
from wtforms import RadioField, PasswordField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo, NumberRange, Required, InputRequired
from flask_wtf import FlaskForm
from wtforms import StringField
from app.forms import MyFloatField


class ModelView(sqla.ModelView):
    @property
    def can_delete(self):
        is_admin = current_user.has_role('admin')
        is_active = current_user.is_active and current_user.is_authenticated
        
        if is_active and is_admin:
            return True
        return False

    @property
    def can_create(self):
        is_admin = current_user.has_role('admin')
        is_active = current_user.is_active and current_user.is_authenticated
        
        if is_active and is_admin:
            return True
        return False

    def is_accessible(self):
        is_active = current_user.is_active and current_user.is_authenticated
        is_admin = current_user.has_role('admin')
        is_moderator = current_user.has_role('moderator')
        
        return is_active and is_admin or is_moderator

    def _handle_view(self, name, **kwargs):
        """
        Override builtin _handle_view in order to redirect users when a view is not accessible.
        """
        if not self.is_accessible():
            if current_user.is_authenticated:
                # permission denied
                abort(403)
            else:
                # login
                return redirect(url_for('login', next=request.url))

    def get_model_data(self):
        view_args = self._get_list_extra_args()
        sort_column = self._get_column_by_idx(view_args.sort)
        if sort_column is not None:
            sort_column = sort_column[0]
            
        count, data = self.get_list(
            view_args.page,
            sort_column,
            view_args.sort_desc,
            view_args.search,
            view_args.filters,
            page_size=self.page_size
        )
        return data


class ShopAdmin(ModelView):
    can_view_details = True
    column_searchable_list = ('place_name', 'address')
    column_labels = dict(
        place_name='Название',
        address='Адрес',
        cash='Наличка',
        cashless='Безнал',
        storage='Склад',
        shop_equipments='Оборудование',
        reports='Отчеты',
        expenses='Расходы',
        baristas='Баристы'
    )
    form_create_rules = ('place_name', 'address', 'cash', 'cashless', 'storage', 'shop_equipments', 'baristas')
    form_edit_rules = ('place_name', 'address', 'cash', 'cashless', 'storage', 'shop_equipments', 'baristas')
    form_args = dict(
        place_name=dict(
            validators=[DataRequired()]
        ),
        address=dict(
            validators=[DataRequired()]
        ),
        cash=dict(
            validators=[
                InputRequired(),
                NumberRange(min=-1, message='Сумма должна быть нулевой, либо больше нуля')
            ]
        ),
        cashless=dict(
            validators=[
                InputRequired(),
                NumberRange(min=-1, message='Сумма должна быть нулевой, либо больше нуля')
            ]
        ),
        
    )


class ShopEquipmentAdmin(ModelView):
    column_searchable_list = ('coffee_machine', )
    column_labels = dict(
        coffee_machine='Кофе Машина',
        grinder_1='Кофемолка 1',
        grinder_2='Кофемолка 2',
        shop='Кофейня'
    )


class StorageAdmin(ModelView):
    column_labels = dict(
        coffee_arabika='Арабика',
        coffee_blend='Бленд',
        milk='Молоко',
        panini='Панини',
        hot_dogs='Хот-доги',
        shop='Кофейня',
        supplies='Поступления',
        by_weights='Развес',
        write_offs='Списания'
    )
    column_formatters = dict(
        coffee_arabika=lambda v, c, m, p: f'{m.coffee_arabika} кг',
        coffee_blend=lambda v, c, m, p: f'{m.coffee_blend} кг',
        milk=lambda v, c, m, p: f'{m.milk} л',
        panini=lambda v, c, m, p: f'{m.panini} шт.',
        hot_dogs=lambda v, c, m, p: f'{m.hot_dogs} шт.',
    )
    column_filters = ('shop', )
    form_create_rules = ('coffee_arabika', 'coffee_blend', 'milk', 'panini', 'hot_dogs', 'shop')
    form_edit_rules = ('coffee_arabika', 'coffee_blend', 'milk', 'panini', 'hot_dogs', 'shop', 'supplies', 'by_weights', 'write_offs')
    form_args = dict(
        coffee_arabika=dict(
            validators=[
                InputRequired(),
                NumberRange(
                    min=-0.0001, 
                    message='Количество арабики должно быть нулевым, либо больше нуля')
                ]
        ),
        coffee_blend=dict(
            validators=[
                InputRequired(),
                NumberRange(
                    min=-0.0001, 
                    message='Количество бленда должно быть нулевым, либо больше нуля'
                )
            ]
        ),
        milk=dict(
            validators=[
                InputRequired(),
                NumberRange(
                    min=-0.0001, 
                    message='Количество молока должно быть нулевым, либо больше нуля'
                )
            ]
        ),
        panini=dict(
            validators=[
                InputRequired(),
                NumberRange(
                    min=-1, 
                    message='Количество панини должно быть нулевым, либо больше нуля'
                )
            ]
        ),
        hot_dogs=dict(
            validators=[
                InputRequired(),
                NumberRange(
                    min=-1, 
                    message='Количество хот-догов должно быть нулевым, либо больше нуля'
                )
            ]
        ),
        shop=dict(
            validators=[
                DataRequired(
                    message='Выберите кофейню')
            ]
        )
    )


class BaristaAdmin(ModelView):
    column_filters = ('name', 'phone_number', 'email', 'shop')
    column_searchable_list = ('name', 'phone_number', 'email')
    column_exclude_list = ('password_hash', 'roles', 'reports', 'salary_rate')
    column_labels = dict(
        name='Имя',
        phone_number='Тел.',
        email='Емейл',
        shop='Кофейня',
        reports='Отчеты',
        roles='Доступ',
        active='Активный',
        confirmed_at='Дата найма',
        password='Пароль'
    )
    form_columns = ('name','phone_number', 'email', 'password', 'shop', 'confirmed_at', 'active', 'reports')
    form_create_rules = ('name', 'phone_number', 'email', 'password', 'shop', 'confirmed_at', 'active')
    form_edit_rules = ('name', 'phone_number', 'email', 'password', 'shop', 'confirmed_at', 'active', 'reports')
    column_formatters = dict(confirmed_at=lambda v, c, m, p: m.confirmed_at.date().strftime("%d.%m.%Y"))
    form_args = dict(
        name=dict(
            validators=[DataRequired()]
        ),
        confirmed_at=dict(
            default=datetime.now(),
            validators=[DataRequired()]
        ),
        active=dict(default=True),
        shop=dict(
            validators=[
                DataRequired(
                    message='Выберите место работы сотрудника'
                )
            ]
        ),
        roles=dict(
            validators=[
                DataRequired(
                    message='Выберите уровень доступа сотрудника'
                )
            ]
        ),
        password=dict(
            validators=[DataRequired()]
        )
    )
    
    @property
    def can_edit(self):
        is_admin = current_user.has_role('admin')
        is_active = current_user.is_active and current_user.is_authenticated
        
        if is_active and is_admin:
            return True
        return False


class ReportAdmin(ModelView):
    can_view_details = True
    column_default_sort = ('timestamp', True)
    column_searchable_list = ('timestamp', )
    column_exclude_list = (
        'consumption_coffee_arabika',
        'consumption_coffee_blend',
        'consumption_milk',
        'consumption_panini',
        'consumption_hot_dogs',
        'coffee_arabika',
        'coffee_blend',
        'milk',
        'panini',
        'hot_dogs',
    )
    column_filters = ('timestamp', 'barista', 'shop')
    column_labels = dict(
        shop='Кофейня',
        barista='Бариста',
        timestamp='Дата',
        cashbox='Касса',
        remainder_of_day='Остаток дня',
        cashless='Б.Н',
        cash_balance='Остаток наличности',
        actual_balance='Фактический остаток',
        consumption_coffee_arabika='Арабика/день',
        consumption_coffee_blend='Бленд/день',
        consumption_milk='Молоко/день',
        consumption_panini='Панини/день',
        consumption_hot_dogs='Хот-доги/день',
        coffee_arabika='Арабика/ост.',
        coffee_blend='Бленд/ост.',
        milk='Молоко/ост.',
        panini='Панини/ост.',
        hot_dogs='Хот-доги/ост.',
        expenses='Расходы'
    )
    # form_create_rules = (
    #     'timestamp', 'shop', 'barista', 'expenses',
    #     'cashless', 'actual_balance', 'coffee_arabika',
    #     'coffee_blend', 'milk', 'panini', 'hot_dogs'
    # )
    form_args = dict(
        timestamp=dict(
            validators=[DataRequired()]
        ),
        shop=dict(
            validators=[
                DataRequired(
                    message='Выберите кофейню')
            ]
        ),
        barista=dict(
            validators=[
                DataRequired(
                    message='Выберите сотрудника')
                ]
        ),
 
        cashbox=dict(
            validators=[
                InputRequired(),
                NumberRange(
                    min=0,
                    message='Сумма не может быть нулевой, либо ниже нуля'
                )
            ]
        ),
        remainder_of_day=dict(
            validators=[
                InputRequired(),
                NumberRange(
                    min=0,
                    message='Сумма не может быть нулевой, либо ниже нуля'
                )
            ]
        ),
        cashless=dict(
            validators=[
                InputRequired(),
                NumberRange(
                    min=0,
                    message='Сумма не может быть нулевой, либо ниже нуля'
                )
            ]
        ),
        cash_balance=dict(
            validators=[
                InputRequired(),
                NumberRange(
                    min=0,
                    message='Сумма не может быть нулевой, либо ниже нуля'
                )
            ]
        ),
        actual_balance=dict(
            validators=[
                InputRequired(),
                NumberRange(
                    min=0,
                    message='Сумма не может быть нулевой, либо ниже нуля'
                )
            ]
        ),
        consumption_coffee_arabika=dict(
            validators=[
                InputRequired(),
                NumberRange(min=-0.0001, message='Расход за день не может быть ниже нуля')
                ]
        ),
        consumption_coffee_blend=dict(
            validators=[
                InputRequired(),
                NumberRange(min=-0.0001, message='Расход за день не может быть ниже нуля')
                ]
        ),
        consumption_milk=dict(
            validators=[
                InputRequired(),
                NumberRange(min=-0.0001, message='Расход за день не может быть ниже нуля')
                ]
        ),
        consumption_panini=dict(
            validators=[
                InputRequired(),
                NumberRange(min=-1, message='Расход за день не может быть ниже нуля')
                ]
        ),
        consumption_hot_dogs=dict(
            validators=[
                InputRequired(),
                NumberRange(min=-1, message='Расход за день не может быть ниже нуля')
                ]
        ),
        coffee_arabika=dict(
            validators=[
                InputRequired(),
                NumberRange(min=-0.0001, message='Остаток арабики должен быть нулевым, либо больше нуля')
                ]
        ),
        coffee_blend=dict(
            validators=[
                InputRequired(),
                NumberRange(min=-0.0001, message='Остаток купажа должен быть нулевым, либо больше нуля')
                ]
        ),
        milk=dict(
            validators=[
                InputRequired(),
                NumberRange(min=-0.0001, message='Остаток молока должен быть нулевым, либо больше нуля')
                ]
        ),
        panini=dict(
            validators=[
                InputRequired(),
                NumberRange(min=-1, message='Остаток панини должен быть нулевым, либо больше нуля')
                ]
        ),
        hot_dogs=dict(
            validators=[
                InputRequired(),
                NumberRange(min=-1, message='Остаток хот-догов должен быть нулевым, либо больше нуля')
                ]
        ),
    )
    #form_overrides = dict(milk=MyFloatField('Количество', default=0.0))
    column_formatters = dict(timestamp=lambda v, c, m, p: m.timestamp.date().strftime("%d.%m.%Y"))
    list_template = 'admin/model/custom_list.html'
    
    def sum_page(self, attr: str) -> int:
        _query = self.get_model_data()
        return sum([p.__dict__[attr] for p in _query])

    def sum_total(self, attr: str) -> int:
        return self.session.query(func.sum(Report.__dict__[attr])).scalar()

    def median_page(self, attr: str) -> int:
        _query = self.get_model_data()
        data = [p.__dict__[attr] for p in _query]
        if len(data) > 1:
            return median(data)
        return 0
        
    def median_total(self, attr: str) -> int:
        _query = self.session.query(func.avg(Report.__dict__[attr])).scalar()
        return round(_query)

    def render(self, template, **kwargs):
        # we are only interested in the list page
        if template == 'admin/model/custom_list.html':
            # append a summary_data dictionary into kwargs
            _current_page = kwargs['page']
            kwargs['column_labels'] = self.column_labels
            kwargs['summary_data'] = {
                'on_page': {
                    'cashbox': self.sum_page('cashbox'),
                    'cash_balance': self.sum_page('cash_balance'),
                    'remainder_of_day': self.sum_page('remainder_of_day'),
                    'cashless': self.sum_page('cashless'),
                    'actual_balance': self.sum_page('actual_balance'),
                },
                'total': {
                    'cashbox': self.sum_total('cashbox'),
                    'cash_balance': self.sum_total('cash_balance'),
                    'remainder_of_day': self.sum_total('remainder_of_day'),
                    'cashless': self.sum_total('cashless'),
                    'actual_balance': self.sum_total('actual_balance'),
                }
            }
            kwargs['median_data'] = {
                'on_page': {
                    'cashbox': self.median_page('cashbox'),
                },
                'total': {
                    'cashbox': self.median_total('cashbox'),
                }
            }

        return super(ReportAdmin, self).render(template, **kwargs)


class RoleAdmin(ModelView):
    can_delete = False
    can_create = False
    column_labels = dict(
        name='Название',
        description='Описание',
        barista='Бариста'
    )
    column_formatters = dict(name=lambda v, c, m, p: m.name.title())
    form_args = dict(
        name=dict(
            validators=[DataRequired()]
        ),
    )
    
    @property
    def can_edit(self):
        is_admin = current_user.has_role('admin')
        is_active = current_user.is_active and current_user.is_authenticated
        
        if is_active and is_admin:
            return True
        return False


class ExpenseAdmin(ModelView):
    can_set_page_size = True
    column_list = ('timestamp', 'money', 'type_cost', 'is_global', 'categories', 'shop')
    form_create_rules = ('timestamp',
                         'type_cost', 'money', 'is_global', 'categories', 'shop')
    form_edit_rules = ('timestamp', 'type_cost', 'money', 'is_global', 'categories', 'shop')
    column_filters = ('timestamp', 'is_global', 'type_cost', 'categories', 'shop')
    column_searchable_list = ('timestamp',)
    column_labels = dict(
        timestamp='Дата',
        is_global='Глобальная?',
        type_cost='Тип траты',
        money='Сумма траты',
        categories='Категории',
        shop='Кофейня'
    )
    can_view_details = True
    column_default_sort = ('timestamp', True)
    column_formatters = dict(
        timestamp=lambda v, c, m, p: m.timestamp.date().strftime("%d.%m.%Y"),
        type_cost=lambda v, c, m, p: 'Наличка' if m.type_cost == 'cash' else 'Безнал',
        is_global=lambda v, c, m, p: 'Да' if m.is_global else 'Нет'
    )
    form_extra_fields = {
        'type_cost': RadioField('Тип траты', choices=[('cash', 'Наличка'), ('cashless', 'Безнал')],
                                validators=[Required()], default='cash')
    }
    form_widget_args = {
        'money': {
            'placeholder': 'В гривнях'
        },
        'type_cost': {
            'class': 'form-check'
        }
    }
    form_ajax_refs = {
        'categories': {
            'fields': ('name',),
            'placeholder': 'Добавить категорию',
            'page_size': 10,
            'minimum_input_length': 0,
        },
        'shop': {
            'fields': ('place_name', 'address'),
            'placeholder': 'Кофейня',
            'page_size': 10,
            'minimum_input_length': 0,
        }
    }
    form_args = dict(
        timestamp=dict(
            validators=[DataRequired()]
        ),
        money=dict(
            validators=[
                InputRequired(),
                NumberRange(
                    min=0,
                    message='Сумма не может быть нулевой, либо ниже нуля'
                )
            ]
        ),
        categories=dict(
            validators=[
                DataRequired(
                    message="Добавьте минимум одну категорию"
                )
            ]
        ),
        shop=dict(
            validators=[DataRequired(message="Выберите кофейню")]
        )
    )


class SupplyAdmin(ModelView):
    can_set_page_size = True
    column_list = ('timestamp', 'product_name', 'amount', 'type_cost', 'money', 'storage')
    column_labels = dict(
        timestamp='Дата',
        product_name='Название товара',
        amount='Количество',
        type_cost='Тип траты',
        money='Сумма',
        storage='Склад'
    )
    column_filters = ('timestamp', 'type_cost', 'storage')
    column_searchable_list = ('timestamp', )
    form_create_rules = ('timestamp', 'product_name', 'amount', 'type_cost', 'money', 'storage')
    form_edit_rules = ('timestamp', 'product_name', 'amount', 'type_cost', 'money', 'storage')
    column_formatters = dict(
        timestamp=lambda v, c, m, p: m.timestamp.date().strftime("%d.%m.%Y"),
        type_cost=lambda v, c, m, p: 'Наличка' if m.type_cost == 'cash' else 'Безнал'
    )
    form_extra_fields = {
        'type_cost':  RadioField(
            'Тип траты',
            choices=[('cash', 'Наличка'), ('cashless', 'Безнал')],
            validators=[Required()],
            default='cash'
        )
    }
    form_widget_args = {
        'money': {
            'placeholder': 'В гривнях'
        },
        'type_cost': {
            'class': 'form-check'
        }
    }
    form_args = dict(
        timestamp=dict(
            validators=[DataRequired()]
        ),
        product_name=dict(
            validators=[DataRequired()]
        ),
        amount=dict(
            validators=[
                DataRequired(),
                NumberRange(
                    min=0.0001,
                    message='Количество не может быть нулевым, либо ниже нуля'
                )
            ]
        ),
        money=dict(
            validators=[
                InputRequired(),
                NumberRange(
                    min=-1,
                    message='Сумма не может быть нулевой, либо ниже нуля'
                )
            ]
        ),
        storage=dict(
            validators=[DataRequired(message="Выберите склад")]
        )
    )


class ByWeightAdmin(ModelView):
    can_set_page_size = True
    column_list = ('timestamp', 'product_name', 'amount', 'type_cost', 'money', 'storage')
    column_labels = dict(
        timestamp='Дата',
        product_name='Название товара',
        amount='Количество',
        type_cost='Тип траты',
        money='Сумма',
        storage='Склад'
    )
    column_filters = ('timestamp', 'product_name')
    column_formatters = dict(
        timestamp=lambda v, c, m, p: m.timestamp.date().strftime("%d.%m.%Y"),
        type_cost=lambda v, c, m, p: 'Наличка' if m.type_cost == 'cash' else 'Безнал'
    )
    form_create_rules = ('timestamp', 'product_name', 'amount', 'type_cost', 'money', 'storage')
    form_edit_rules = ('timestamp', 'product_name', 'amount', 'type_cost', 'money', 'storage')
    form_extra_fields = {
        'type_cost':  RadioField(
            'Тип траты',
            choices=[('cash', 'Наличка'), ('cashless', 'Безнал')],
            validators=[Required()],
            default='cash'
        )
    }
    form_widget_args = {
        'money': {
            'placeholder': 'В гривнях'
        },
        'type_cost': {
            'class': 'form-check'
        }
    }
    form_args = dict(
        timestamp=dict(
            validators=[DataRequired()]
        ),
        product_name=dict(
            validators=[DataRequired()]
        ),
        amount=dict(
            validators=[
                DataRequired(),
                NumberRange(
                    min=0.0001,
                    message='Количество не может быть нулевым, либо ниже нуля'
                )
            ]
        ),
        money=dict(
            validators=[
                InputRequired(),
                NumberRange(
                    min=-1,
                    message='Сумма не может быть нулевой, либо ниже нуля'
                )
            ]
        ),
        storage=dict(
            validators=[DataRequired(message="Выберите склад")]
        )
    )


class WriteOffAdmin(ModelView):
    can_set_page_size = True
    column_labels = dict(
        timestamp='Дата',
        product_name='Название товара',
        amount='Количество',
        storage='Склад'
    )
    column_filters = ('timestamp', 'product_name')
    column_formatters = dict(timestamp=lambda v, c, m, p: m.timestamp.date().strftime("%d.%m.%Y"))
    form_args = dict(
        timestamp=dict(
            validators=[DataRequired()]
        ),
        product_name=dict(
            validators=[DataRequired()]
        ),
        amount=dict(
            validators=[
                DataRequired(),
                NumberRange(
                    min=0.0001,
                    message='Количество не может быть нулевым, либо ниже нуля'
                )
            ]
        ),
        storage=dict(
            validators=[DataRequired(message="Выберите склад")]
        )
    )


class CategoryAdmin(ModelView):
    can_view_details = True
    column_labels = dict(
        name='Название категории',
        expense='Расходы'
    )
    form_create_rules = ('name', )
    form_args = dict(
        name=dict(
            validators=[DataRequired()]
        )
    )
    column_editable_list = ('name', )
    