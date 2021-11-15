from statistics import median
from datetime import datetime
from sqlalchemy import func
from flask import abort, redirect, request, url_for, Markup
from flask_security import current_user
from flask_admin import AdminIndexView, expose
from flask_admin.contrib import sqla
from app.models import Shop, Report, Expense, Supply
from wtforms import RadioField, SelectField
from wtforms.validators import DataRequired, NumberRange, Required, InputRequired


class IndexAdmin(AdminIndexView):
    @expose('/', methods=('GET', 'POST'))
    def index(self):
        template = 'admin/index.html'
        _query_exp_cash = Expense.query.filter_by(type_cost='cash').all()
        _query_exp_cashless = Expense.query.filter_by(type_cost='cashless').all()
        _query_supply_cash = Supply.query.filter_by(type_cost='cash').all()
        _query_supply_cashless = Supply.query.filter_by(type_cost='cashless').all()
        _query_shop = Shop.query.all()
        kwargs = dict()
        kwargs['shop_cash'] = sum([s.cash for s in _query_shop])
        kwargs['shop_cashless'] = sum([s.cashless for s in _query_shop])
        kwargs['all_shop'] = kwargs['shop_cash'] + kwargs['shop_cashless']
        kwargs['exp_cash'] = sum([e.money for e in _query_exp_cash])
        kwargs['exp_cashless'] = sum([e.money for e in _query_exp_cashless])
        kwargs['exp_cash'] += sum([s.money for s in _query_supply_cash])
        kwargs['exp_cashless'] += sum([s.money for s in _query_supply_cashless])
        kwargs['all_exp'] = kwargs['exp_cash'] + kwargs['exp_cashless']
        return self.render(template, **kwargs)


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
        shop_equipment='Оборудование',
        reports='Отчеты',
        expenses='Расходы',
        baristas='Баристы'
    )
    form_create_rules = ('place_name', 'address', 'cash', 'cashless', 'storage', 'shop_equipment', 'baristas')
    form_edit_rules = ('place_name', 'address', 'cash', 'cashless', 'storage', 'shop_equipment', 'baristas')
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
                NumberRange(
                    min=-1,
                    message='Сумма должна быть нулевой, либо больше нуля'
                )
            ]
        ),
        cashless=dict(
            validators=[
                InputRequired(),
                NumberRange(
                    min=-1,
                    message='Сумма должна быть нулевой, либо больше нуля'
                )
            ]
        ),
        
    )
    form_widget_args = {
        'place_name': {
            'placeholder': 'Название кофейни'
        },
        'address': {
            'placeholder': 'Адрес кофейни'
        },
        'cash': {
            'placeholder': 'Наличка в гривне'
        },
        'cashless': {
            'placeholder': 'Безнал в гривне'
        }
    }


class ShopEquipmentAdmin(ModelView):
    can_view_details = True
    column_searchable_list = ('coffee_machine', )
    column_labels = dict(
        coffee_machine='Кофе Машина',
        grinder_1='Кофемолка 1',
        grinder_2='Кофемолка 2',
        shop='Кофейня'
    )
    form_args = dict(
        shop=dict(
            validators=[
                DataRequired(
                    message='Выберите кофейню')
            ]
        )
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
    form_edit_rules = (
        'coffee_arabika',
        'coffee_blend',
        'milk',
        'panini',
        'hot_dogs',
        'shop'
    )
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
    form_widget_args = {
        'coffee_arabika': {
            'placeholder': 'Введите количество арабики в кг'
        },
        'coffee_blend': {
            'placeholder': 'Введите количество купажа в кг'
        },
        'milk': {
            'placeholder': 'Введите количество молока в л'
        },
        'panini': {
            'placeholder': 'Введите количество панини'
        },
        'hot_dogs': {
            'placeholder': 'Введите количество хот-догов (комплект булка-сосиска)'
        }
    }


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
        password='Пароль',
        expenses='Расходы',
        supplies='Поступления',
        by_weights='Развес',
        write_offs='Списания'
    )
    form_columns = (
        'name',
        'phone_number',
        'email',
        'password',
        'shop',
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
        'active'
    )
    form_edit_rules = (
        'name',
        'phone_number',
        'email',
        'password',
        'shop',
        'confirmed_at',
        'active',
        'reports',
        'expenses',
        'supplies',
        'by_weights',
        'write_offs'
    )
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

    form_widget_args = {
        'name': {
            'placeholder': 'Имя сотрудника'
        },
        'phone_number': {
            'placeholder': 'Мобильный телефон'
        },
        'email': {
            'placeholder': 'Емейл'
        }
    }


class ReportAdmin(ModelView):
    list_template = 'admin/model/report_list.html'
    can_view_details = True
    column_default_sort = ('timestamp', True)
    column_searchable_list = ('timestamp', )
    column_exclude_list = (
        'last_edit',
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
    column_formatters = dict(timestamp=lambda v, c, m, p: m.timestamp.date().strftime("%d.%m.%Y"))
    form_create_rules = (
        'timestamp',
        'expenses',
        'cashless',
        'actual_balance',
        'coffee_arabika',
        'coffee_blend',
        'milk',
        'panini',
        'hot_dogs',
        'shop',
        'barista'
    )
    form_edit_rules = (
        'timestamp',
        'cashbox',
        'expenses',
        'remainder_of_day',
        'cashless',
        'cash_balance',
        'actual_balance',
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
        'shop',
        'barista'
    )
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
                    message='Выберите сотрудника'
                )
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
                NumberRange(
                    min=-0.0001,
                    message='Расход за день не может быть ниже нуля'
                )
            ]
        ),
        consumption_coffee_blend=dict(
            validators=[
                InputRequired(),
                NumberRange(
                    min=-0.0001,
                    message='Расход за день не может быть ниже нуля'
                )
            ]
        ),
        consumption_milk=dict(
            validators=[
                InputRequired(),
                NumberRange(
                    min=-0.0001,
                    message='Расход за день не может быть ниже нуля'
                )
            ]
        ),
        consumption_panini=dict(
            validators=[
                InputRequired(),
                NumberRange(
                    min=-1,
                    message='Расход за день не может быть ниже нуля'
                )
            ]
        ),
        consumption_hot_dogs=dict(
            validators=[
                InputRequired(),
                NumberRange(
                    min=-1,
                    message='Расход за день не может быть ниже нуля'
                )
            ]
        ),
        coffee_arabika=dict(
            validators=[
                InputRequired(),
                NumberRange(
                    min=-0.0001,
                    message='Остаток арабики должен быть нулевым, либо больше нуля'
                )
            ]
        ),
        coffee_blend=dict(
            validators=[
                InputRequired(),
                NumberRange(
                    min=-0.0001,
                    message='Остаток купажа должен быть нулевым, либо больше нуля'
                )
            ]
        ),
        milk=dict(
            validators=[
                InputRequired(),
                NumberRange(
                    min=-0.0001,
                    message='Остаток молока должен быть нулевым, либо больше нуля'
                )
            ]
        ),
        panini=dict(
            validators=[
                InputRequired(),
                NumberRange(
                    min=-1,
                    message='Остаток панини должен быть нулевым, либо больше нуля'
                )
            ]
        ),
        hot_dogs=dict(
            validators=[
                InputRequired(),
                NumberRange(
                    min=-1,
                    message='Остаток хот-догов должен быть нулевым, либо больше нуля'
                )
            ]
        ),
    )
    form_widget_args = {
        'timestamp': {
            'placeholder': 'Дата и время отправки отчета'
        },
        'cashbox': {
            'placeholder': 'Касса'
        },
        'remainder_of_day': {
            'placeholder': 'Остаток дня, сумма остатка наличности и безнала'
        },
        'cashless': {
            'placeholder': 'Безнал'
        },
        'cash_balance': {
            'placeholder': 'Разница между утренним фактическим остатком и вечерним'
        },
        'actual_balance': {
            'placeholder': 'Фактический остаток наличности вечером'
        },
        'consumption_coffee_arabika': {
            'placeholder': 'Расход арабики в кг за день'
        },
        'consumption_coffee_blend': {
            'placeholder': 'Расход купажа в кг за день'
        },
        'consumption_milk': {
            'placeholder': 'Расход молока в л за день'
        },
        'consumption_panini': {
            'placeholder': 'Расход панини за день'
        },
        'consumption_hot_dogs': {
            'placeholder': 'Расход хот-догов (комплект булка-сосиска) за день'
        },
        'coffee_arabika': {
            'placeholder': 'Количество арабики в кг, остаток на следующий день'
        },
        'coffee_blend': {
            'placeholder': 'Количество купажа в кг, остаток на следующий день'
        },
        'milk': {
            'placeholder': 'Количество молока в л, остаток на следующий день'
        },
        'panini': {
            'placeholder': 'Количество панини, остаток на следующий день'
        },
        'hot_dogs': {
            'placeholder': 'Количество хот-догов (комплект булка-сосиска), остаток на следующий день'
        }
    }

    def sum_page(self, attr: str) -> int:
        _query = self.get_model_data()
        return sum([p.__dict__[attr] for p in _query])

    def sum_total(self, attr: str) -> int:
        _query = self.session.query(func.sum(Report.__dict__[attr])).scalar()
        if not _query:
            return 0
        return _query

    def median_page(self, attr: str) -> int:
        _query = self.get_model_data()
        data = [p.__dict__[attr] for p in _query]
        if len(data) > 1:
            return median(data)
        return 0
        
    def median_total(self, attr: str) -> int:
        _query = self.session.query(func.avg(Report.__dict__[attr])).scalar()
        if not _query:
            return 0
        return _query

    def render(self, template, **kwargs):
        if template == 'admin/model/report_list.html':
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
                    'cash_balance': self.median_page('cash_balance'),
                    'remainder_of_day': self.median_page('remainder_of_day'),
                    'cashless': self.median_page('cashless'),
                    'actual_balance': self.median_page('actual_balance'),
                },
                'total': {
                    'cashbox': self.median_total('cashbox'),
                    'cash_balance': self.median_total('cash_balance'),
                    'remainder_of_day': self.median_total('remainder_of_day'),
                    'cashless': self.median_total('cashless'),
                    'actual_balance': self.median_total('actual_balance'),
                }
            }

        return super(ReportAdmin, self).render(template, **kwargs)

    def on_model_change(self, form, model, is_created):
        if is_created:
            expanses = sum([e.money for e in model.expenses if e.type_cost == 'cash'])
            cash_balance = form.actual_balance.data - model.shop.cash
            model.shop.cash += cash_balance
            model.shop.cashless += model.cashless
            model.cash_balance = cash_balance
            model.remainder_of_day = model.cashless + form.actual_balance.data
            model.cashbox = model.remainder_of_day + expanses
            print(model.shop.storage.coffee_arabika)

            model.consumption_coffee_arabika = model.shop.storage.coffee_arabika - float(form.coffee_arabika.data)
            model.consumption_coffee_blend = model.shop.storage.coffee_blend - float(form.coffee_blend.data)
            model.consumption_milk = model.shop.storage.milk - float(form.milk.data)
            model.consumption_panini = model.shop.storage.panini - model.panini
            model.consumption_hot_dogs = model.shop.storage.hot_dogs - model.hot_dogs
            model.shop.storage.coffee_arabika -= model.consumption_coffee_arabika
            model.shop.storage.coffee_blend -= model.consumption_coffee_blend
            model.shop.storage.milk -= model.consumption_milk
            model.shop.storage.panini -= model.consumption_panini
            model.shop.storage.hot_dogs -= model.consumption_hot_dogs
        else:
            # TODO update model ReportAdmin
            pass

    def on_model_delete(self, model):
        model.shop.cash -= model.cash_balance
        model.shop.cashless -= model.cashless
        model.shop.storage.coffee_arabika += model.consumption_coffee_arabika
        model.shop.storage.coffee_blend += model.consumption_coffee_blend
        model.shop.storage.milk += model.consumption_milk
        model.shop.storage.panini += model.consumption_panini
        model.shop.storage.hot_dogs += model.consumption_hot_dogs


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
        'timestamp',
        'is_global',
        'type_cost',
        'money',
        'categories',
        'shop'
    )
    form_edit_rules = (
        'timestamp',
        'is_global',
        'type_cost',
        'money',
        'categories',
        'shop'
    )
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
        is_global=lambda v, c, m, p: 'Да' if m.is_global else 'Нет',
        money=_list_money
    )
    form_extra_fields = {
        'type_cost': RadioField(
            'Тип траты',
            choices=[
                ('cash', 'Наличка'),
                ('cashless', 'Безнал')
            ],
            validators=[Required()], default='cash'
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
        shop=dict(
            validators=[
                DataRequired(
                    message="Выберите кофейню"
                )
            ]
        )
    )

    def sum_page(self, attr: str) -> int:
        _query = self.get_model_data()
        return sum([p.__dict__[attr] for p in _query])

    def sum_total(self, attr: str) -> int:
        return self.session.query(func.sum(ExpenseAdmin.__dict__[attr])).scalar()

    def median_page(self, attr: str) -> int:
        _query = self.get_model_data()
        data = [p.__dict__[attr] for p in _query]
        if len(data) > 1:
            return median(data)
        return 0

    def median_total(self, attr: str) -> int:
        _query = self.session.query(func.avg(ExpenseAdmin.__dict__[attr])).scalar()
        return round(_query)

    def render(self, template, **kwargs):
        if template == 'admin/model/expense_list.html':
            # append a summary_data dictionary into kwargs
            _current_page = kwargs['page']
            kwargs['column_labels'] = self.column_labels
            kwargs['summary_data'] = {
                'on_page': {
                    'money': self.sum_page('money')
                },
                # TODO fix bug, key error 'money'
                'total': {
                    'money': 0
                }
            }
            kwargs['median_data'] = {
                'money': {
                    'money': self.median_page('money')
                },
                # TODO fix bug, key error 'money'
                'total': {
                    'money': 0
                }
            }

        return super(ExpenseAdmin, self).render(template, **kwargs)


    def on_form_prefill(self, form, id):
        pass

    def on_model_change(self, form, model, is_created):
        money = model.money
        if is_created == False:
            expense = Expense.query.filter_by(id=model.id).first()
            print('Prev money', expense.money, model.money)
            
        if model.type_cost == 'cash':
            model.shop.cash -= money
        else:
            model.shop.cashless -= money

    def on_model_delete(self, model):
        if model.type_cost and model.money and model.shop:
            if model.type_cost == 'cash':
                model.shop.cash += model.money
            else:
                model.shop.cashless += model.money


class SupplyAdmin(ModelView):
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

    def _list_money(view, context, model, name):
        if not model.money:
            return ''
        type_cost = '' if model.type_cost == 'cash' else ' (Безнал)'
        formatter = f'{model.money} грн.{type_cost}'
        return Markup(f'{formatter}')

    can_set_page_size = True
    column_list = ('timestamp', 'product_name', 'amount', 'money', 'storage')
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
        type_cost=lambda v, c, m, p: 'Наличка' if m.type_cost == 'cash' else 'Безнал',
        money=_list_money,
        amount=_list_amount
    )
    form_args = dict(
        timestamp=dict(
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
            validators=[
                DataRequired(
                    message="Выберите склад"
                )
            ]
        )
    )
    form_extra_fields = dict(
        type_cost=RadioField(
            'Тип траты',
            choices=[
                ('cash', 'Наличка'),
                ('cashless', 'Безнал')
            ],
            validators=[Required()],
            default='cash'
        ),
        product_name=SelectField(
            'Название товара',
            choices=[
                ('coffee_arabika', 'Арабика'),
                ('coffee_blend', 'Купаж'),
                ('milk', 'Молоко'),
                ('panini', 'Панини'),
                ('hot_dogs', 'Хот-доги')
            ],
            validators=[Required()],
        )
    )
    form_widget_args = {
        'money': {
            'placeholder': 'В гривнях'
        },
        'type_cost': {
            'class': 'form-check'
        },
        'amount': {
            'placeholder': 'Количество в кг, л, и поштучно'
        }
    }

    def on_model_change(self, form, model, is_created):
        if is_created:
            if form.product_name.data == 'coffee_blend':
                model.storage.coffee_blend += float(form.amount.data)
            elif form.product_name.data == 'coffee_arabika':
                model.storage.coffee_arabika += float(form.amount.data)
            elif form.product_name.data == 'milk':
                model.storage.milk += float(form.amount.data)
            elif form.product_name.data == 'panini':
                model.storage.panini += int(form.amount.data)
            else:
                model.storage.hot_dogs += int(form.amount.data)

            if form.type_cost.data == 'cash':
                model.storage.shop.cash -= form.money.data
            else:
                model.storage.shop.cashless -= form.money.data
        else:
            # TODO update model SupplyAdmin
            pass

    def on_model_delete(self, model):
        if model.product_name == 'coffee_blend':
            model.storage.coffee_blend -= model.amount
        elif model.product_name == 'coffee_arabika':
            model.storage.coffee_arabika -= model.amount
        elif model.product_name == 'milk':
            model.storage.milk -= model.amount
        elif model.product_name == 'panini':
            model.storage.panini -= model.amount
        else:
            model.storage.hot_dogs -= model.amount

        if model.type_cost == 'cash':
            model.storage.shop.cash += model.money
        else:
            model.storage.shop.cashless += model.money


class ByWeightAdmin(ModelView):
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

    can_set_page_size = True
    column_list = ('timestamp', 'product_name', 'amount', 'money', 'storage')
    column_labels = dict(
        timestamp='Дата',
        product_name='Название товара',
        amount='Количество',
        type_cost='Тип траты',
        money='Сумма',
        storage='Склад'
    )
    column_filters = ('timestamp', 'product_name', 'type_cost')
    column_formatters = dict(
        timestamp=lambda v, c, m, p: m.timestamp.date().strftime("%d.%m.%Y"),
        type_cost=lambda v, c, m, p: 'Наличка' if m.type_cost == 'cash' else 'Безнал',
        money=_list_money,
        amount=_list_amount
    )
    form_create_rules = ('timestamp', 'product_name', 'amount', 'type_cost', 'money', 'storage')
    form_edit_rules = ('timestamp', 'product_name', 'amount', 'type_cost', 'money', 'storage')
    form_args = dict(
        timestamp=dict(
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
    form_extra_fields = dict(
        type_cost=RadioField(
            'Тип траты',
            choices=[
                ('cash', 'Наличка'),
                ('cashless', 'Безнал')
            ],
            validators=[Required()],
            default='cash'
        ),
        product_name=SelectField(
            'Название товара',
            choices=[
                ('coffee_arabika', 'Арабика'),
                ('coffee_blend', 'Купаж'),
                ('milk', 'Молоко'),
                ('panini', 'Панини'),
                ('hot_dogs', 'Хот-доги')
            ],
            validators=[Required()],
        )
    )
    form_widget_args = {
        'money': {
            'placeholder': 'В гривнях'
        },
        'type_cost': {
            'class': 'form-check'
        },
        'amount': {
            'placeholder': 'Количество в кг, л, и поштучно'
        }
    }

    def on_model_change(self, form, model, is_created):
        if is_created:
            if form.product_name.data == 'coffee_blend':
                model.storage.coffee_blend -= float(form.amount.data)
            else:
                model.storage.coffee_arabika -= float(form.amount.data)

            if form.type_cost.data == 'cash':
                model.storage.shop.cash += form.money.data
            else:
                model.storage.shop.cashless += form.money.data
        else:
            # TODO update model ByWeightAdmin
            pass

    def on_model_delete(self, model):
        if model.product_name == 'coffee_blend':
            model.storage.coffee_blend += float(model.amount)
        else:
            model.storage.coffee_arabika += float(model.amount)

        if model.type_cost == 'cash':
            model.storage.shop.cash -= model.money
        else:
            model.storage.shop.cashless -= model.money


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

    can_set_page_size = True
    column_list = ('timestamp', 'product_name', 'amount', 'storage')
    column_labels = dict(
        timestamp='Дата',
        product_name='Название товара',
        amount='Количество',
        storage='Склад'
    )
    column_filters = ('timestamp', 'product_name')
    column_formatters = dict(
        timestamp=lambda v, c, m, p: m.timestamp.date().strftime("%d.%m.%Y"),
        amount=_list_amount
    )
    form_create_rules = ('timestamp', 'product_name', 'amount', 'storage')
    form_edit_rules = ('timestamp', 'product_name', 'amount', 'storage')
    form_args = dict(
        timestamp=dict(
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
    form_extra_fields = dict(
        product_name=SelectField(
            'Название товара',
            choices=[
                ('coffee_arabika', 'Арабика'),
                ('coffee_blend', 'Купаж'),
                ('milk', 'Молоко'),
                ('panini', 'Панини'),
                ('hot_dogs', 'Хот-доги')
            ],
            validators=[Required()],
        )
    )
    form_widget_args = {
        'amount': {
            'placeholder': 'Количество в кг, л, и поштучно'
        }
    }

    def on_model_change(self, form, model, is_created):
        if is_created:
            if form.product_name.data == 'coffee_blend':
                model.storage.coffee_blend -= float(form.amount.data)
            elif form.product_name.data == 'coffee_arabika':
                model.storage.coffee_arabika -= float(form.amount.data)
            elif form.product_name.data == 'milk':
                model.storage.milk -= float(form.amount.data)
            elif form.product_name.data == 'panini':
                model.storage.panini -= int(form.amount.data)
            else:
                model.storage.hot_dogs -= int(form.amount.data)
        else:
            # TODO update model WriteOffAdmin
            pass

    def on_model_delete(self, model):
        if model.product_name == 'coffee_blend':
            model.storage.coffee_blend += model.amount
        elif model.product_name == 'coffee_arabika':
            model.storage.coffee_arabika += model.amount
        elif model.product_name == 'milk':
            model.storage.milk += model.amount
        elif model.product_name == 'panini':
            model.storage.panini += model.amount
        else:
            model.storage.hot_dogs += model.amount


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
    form_widget_args = {
        'name': {
            'placeholder': 'Название для расходов'
        }
    }
    