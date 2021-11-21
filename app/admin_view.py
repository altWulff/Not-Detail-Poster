from statistics import median
from datetime import datetime, date
from sqlalchemy import func
from flask import abort, redirect, request, url_for, Markup
from flask_security import current_user
from flask_admin import AdminIndexView, expose
from flask_admin.contrib import sqla
from flask_admin.model import typefmt
from app.models import Shop, Report, Expense, Supply
from wtforms import RadioField, SelectField, BooleanField
from wtforms.validators import DataRequired, NumberRange, Required, InputRequired
import logging
from flask import flash
from flask_admin.babel import gettext

log = logging.getLogger("flask-admin.sqla")


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
    column_type_formatters = dict(typefmt.BASE_FORMATTERS)
    column_type_formatters.update({
        date: lambda view, value: value.strftime('%d.%m.%Y')
    })

    @property
    def can_delete(self):
        try:
            is_admin = current_user.has_role('admin')
            is_active = current_user.is_active and current_user.is_authenticated
            return is_active and is_admin
        except:
            pass
        return False

    @property
    def can_create(self):
        try:
            is_admin = current_user.has_role('admin')
            is_active = current_user.is_active and current_user.is_authenticated
            return is_active and is_admin
        except:
            pass
        return False

    def is_accessible(self):
        try:
            is_active = current_user.is_active and current_user.is_authenticated
            
            is_admin = current_user.has_administrative_rights
            is_moderator = current_user.has_moderator_rights
    
            return is_active and is_admin or is_moderator
        except:
            return False

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
        place_name=gettext('Название'),
        address=gettext('Адрес'),
        cash=gettext('Наличка'),
        cashless=gettext('Безнал'),
        storage=gettext('Склад'),
        shop_equipment=gettext('Оборудование'),
        reports=gettext('Отчеты'),
        expenses=gettext('Расходы'),
        baristas=gettext('Баристы')
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
                    message=gettext('Сумма должна быть нулевой, либо больше нуля')
                )
            ]
        ),
        cashless=dict(
            validators=[
                InputRequired(),
                NumberRange(
                    min=-1,
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


class ShopEquipmentAdmin(ModelView):
    can_view_details = True
    column_searchable_list = ('coffee_machine',)
    column_labels = dict(
        coffee_machine=gettext('Кофе Машина'),
        grinder_1=gettext('Кофемолка 1'),
        grinder_2=gettext('Кофемолка 2'),
        shop=gettext('Кофейня')
    )
    form_args = dict(
        shop=dict(
            validators=[
                DataRequired(
                    message=gettext('Выберите кофейню')
                )
            ]
        )
    )


class StorageAdmin(ModelView):
    column_labels = dict(
        coffee_arabika=gettext('Арабика'),
        coffee_blend=gettext('Бленд'),
        milk=gettext('Молоко'),
        panini=gettext('Панини'),
        hot_dogs=gettext('Хот-доги'),
        shop=gettext('Кофейня'),
        supplies=gettext('Поступления'),
        by_weights=gettext('Развес'),
        write_offs=gettext('Списания')
    )
    column_formatters = dict(
        coffee_arabika=lambda v, c, m, p: f'{m.coffee_arabika} кг',
        coffee_blend=lambda v, c, m, p: f'{m.coffee_blend} кг',
        milk=lambda v, c, m, p: f'{m.milk} л',
        panini=lambda v, c, m, p: f'{m.panini} шт.',
        hot_dogs=lambda v, c, m, p: f'{m.hot_dogs} шт.',
    )
    column_filters = ('shop',)
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
                    message=gettext('Количество арабики должно быть нулевым, либо больше нуля'))
            ]
        ),
        coffee_blend=dict(
            validators=[
                InputRequired(),
                NumberRange(
                    min=-0.0001,
                    message=gettext('Количество бленда должно быть нулевым, либо больше нуля')
                )
            ]
        ),
        milk=dict(
            validators=[
                InputRequired(),
                NumberRange(
                    min=-0.0001,
                    message=gettext('Количество молока должно быть нулевым, либо больше нуля')
                )
            ]
        ),
        panini=dict(
            validators=[
                InputRequired(),
                NumberRange(
                    min=-1,
                    message=gettext('Количество панини должно быть нулевым, либо больше нуля')
                )
            ]
        ),
        hot_dogs=dict(
            validators=[
                InputRequired(),
                NumberRange(
                    min=-1,
                    message=gettext('Количество хот-догов должно быть нулевым, либо больше нуля')
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
    form_widget_args = {
        'coffee_arabika': {
            'placeholder': gettext('Введите количество арабики в кг')
        },
        'coffee_blend': {
            'placeholder': gettext('Введите количество купажа в кг')
        },
        'milk': {
            'placeholder': gettext('Введите количество молока в л')
        },
        'panini': {
            'placeholder': gettext('Введите количество панини')
        },
        'hot_dogs': {
            'placeholder': gettext('Введите количество хот-догов (комплект булка-сосиска)')
        }
    }


class BaristaAdmin(ModelView):
    column_filters = ('name', 'phone_number', 'email', 'shop')
    column_searchable_list = ('name', 'phone_number', 'email')
    column_exclude_list = ('password_hash', 'roles', 'reports', 'salary_rate')
    column_labels = dict(
        name=gettext('Имя'),
        phone_number=gettext('Тел.'),
        email=gettext('Емейл'),
        shop=gettext('Кофейня'),
        reports=gettext('Отчеты'),
        roles=gettext('Доступ'),
        active=gettext('Активный'),
        confirmed_at=gettext('Дата найма'),
        password=gettext('Пароль'),
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


class ReportAdmin(ModelView):
    list_template = 'admin/model/report_list.html'
    can_view_details = True
    column_default_sort = ('timestamp', True)
    column_searchable_list = ('timestamp',)
    column_exclude_list = (
        'backdating',
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
        shop=gettext('Кофейня'),
        barista=gettext('Бариста'),
        timestamp=gettext('Дата'),
        cashbox=gettext('Касса'),
        remainder_of_day=gettext('Остаток дня'),
        cashless=gettext('Б.Н'),
        cash_balance=gettext('Остаток наличности'),
        actual_balance=gettext('Фактический остаток'),
        consumption_coffee_arabika=gettext('Арабика/день'),
        consumption_coffee_blend=gettext('Бленд/день'),
        consumption_milk=gettext('Молоко/день'),
        consumption_panini=gettext('Панини/день'),
        consumption_hot_dogs=gettext('Хот-доги/день'),
        coffee_arabika=gettext('Арабика/ост.'),
        coffee_blend=gettext('Бленд/ост.'),
        milk=gettext('Молоко/ост.'),
        panini=gettext('Панини/ост.'),
        hot_dogs=gettext('Хот-доги/ост.'),
        expenses=gettext('Расходы')
    )
    form_extra_fields = {
        'backdating': BooleanField(gettext('Обработка задним числом'))
    }
    form_create_rules = (
        'backdating',
        'timestamp',
        'expenses',
        'cashless',
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
    form_edit_rules = (
        'backdating',
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
            validators=[DataRequired()],
            format='%d.%m.%Y %H:%M'
        ),
        shop=dict(
            validators=[
                DataRequired(
                    message=gettext('Выберите кофейню')
                )
            ]
        ),
        barista=dict(
            validators=[
                DataRequired(
                    message=gettext('Выберите сотрудника')
                )
            ]
        ),

        cashbox=dict(
            validators=[
                InputRequired(),
                NumberRange(
                    min=0,
                    message=gettext('Сумма не может быть нулевой, либо ниже нуля')
                )
            ]
        ),
        remainder_of_day=dict(
            validators=[
                InputRequired(),
                NumberRange(
                    min=0,
                    message=gettext('Сумма не может быть нулевой, либо ниже нуля')
                )
            ]
        ),
        cashless=dict(
            validators=[
                InputRequired(),
                NumberRange(
                    min=0,
                    message=gettext('Сумма не может быть нулевой, либо ниже нуля')
                )
            ]
        ),
        cash_balance=dict(
            validators=[
                InputRequired(),
                NumberRange(
                    min=0,
                    message=gettext('Сумма не может быть нулевой, либо ниже нуля')
                )
            ]
        ),
        actual_balance=dict(
            validators=[
                InputRequired(),
                NumberRange(
                    min=0,
                    message=gettext('Сумма не может быть нулевой, либо ниже нуля')
                )
            ]
        ),
        consumption_coffee_arabika=dict(
            default=0.0,
            validators=[
                InputRequired(),
                NumberRange(
                    min=-0.0001,
                    message=gettext('Расход за день не может быть ниже нуля')
                )
            ]
        ),
        consumption_coffee_blend=dict(
            default=0.0,
            validators=[
                InputRequired(),
                NumberRange(
                    min=-0.0001,
                    message=gettext('Расход за день не может быть ниже нуля')
                )
            ]
        ),
        consumption_milk=dict(
            default=0.0,
            validators=[
                InputRequired(),
                NumberRange(
                    min=-0.0001,
                    message=gettext('Расход за день не может быть ниже нуля')
                )
            ]
        ),
        consumption_panini=dict(
            default=0,
            validators=[
                InputRequired(),
                NumberRange(
                    min=-1,
                    message=gettext('Расход за день не может быть ниже нуля')
                )
            ]
        ),
        consumption_hot_dogs=dict(
            default=0,
            validators=[
                InputRequired(),
                NumberRange(
                    min=-1,
                    message=gettext('Расход за день не может быть ниже нуля')
                )
            ]
        ),
        coffee_arabika=dict(
            validators=[
                InputRequired(),
                NumberRange(
                    min=-0.0001,
                    message=gettext('Остаток арабики должен быть нулевым, либо больше нуля')
                )
            ]
        ),
        coffee_blend=dict(
            validators=[
                InputRequired(),
                NumberRange(
                    min=-0.0001,
                    message=gettext('Остаток купажа должен быть нулевым, либо больше нуля')
                )
            ]
        ),
        milk=dict(
            validators=[
                InputRequired(),
                NumberRange(
                    min=-0.0001,
                    message=gettext('Остаток молока должен быть нулевым, либо больше нуля')
                )
            ]
        ),
        panini=dict(
            validators=[
                InputRequired(),
                NumberRange(
                    min=-1,
                    message=gettext('Остаток панини должен быть нулевым, либо больше нуля')
                )
            ]
        ),
        hot_dogs=dict(
            validators=[
                InputRequired(),
                NumberRange(
                    min=-1,
                    message=gettext('Остаток хот-догов должен быть нулевым, либо больше нуля')
                )
            ]
        ),
    )
    form_widget_args = {
        'timestamp': {
            'placeholder': gettext('Дата и время отправки отчета'),
            'data-date-format': u'DD.MM.YYYY HH:mm'
        },
        'cashbox': {
            'placeholder': gettext('Касса')
        },
        'remainder_of_day': {
            'placeholder': gettext('Остаток дня, сумма остатка наличности и безнала')
        },
        'cashless': {
            'placeholder': gettext('Безнал')
        },
        'cash_balance': {
            'placeholder': gettext('Разница между утренним фактическим остатком и вечерним')
        },
        'actual_balance': {
            'placeholder': gettext('Фактический остаток наличности вечером')
        },
        'consumption_coffee_arabika': {
            'placeholder': gettext('Расход арабики в кг за день')
        },
        'consumption_coffee_blend': {
            'placeholder': gettext('Расход купажа в кг за день')
        },
        'consumption_milk': {
            'placeholder': gettext('Расход молока в л за день')
        },
        'consumption_panini': {
            'placeholder': gettext('Расход панини за день')
        },
        'consumption_hot_dogs': {
            'placeholder': gettext('Расход хот-догов (комплект булка-сосиска) за день')
        },
        'coffee_arabika': {
            'placeholder': gettext('Количество арабики в кг, остаток на следующий день')
        },
        'coffee_blend': {
            'placeholder': gettext('Количество купажа в кг, остаток на следующий день')
        },
        'milk': {
            'placeholder': gettext('Количество молока в л, остаток на следующий день')
        },
        'panini': {
            'placeholder': gettext('Количество панини, остаток на следующий день')
        },
        'hot_dogs': {
            'placeholder': gettext('Количество хот-догов (комплект булка-сосиска), остаток на следующий день')
        }
    }

    def sum_page(self, attr: str) -> int:
        _query = self.get_model_data()
        try:
            return sum([p.__dict__[attr] for p in _query if p])
        except:
            return 0

    def sum_total(self, attr: str) -> int:
        _query = self.session.query(func.sum(Report.__dict__[attr])).scalar()
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
        _query = self.session.query(func.avg(Report.__dict__[attr])).scalar()
        try:
            return round(_query)
        except:
            return 0

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

    def update_model(self, form, model):
        try:
            new_cash_balance, old_cash_balance = form.cash_balance.data, model.cash_balance
            new_cashless, old_cashless = form.cashless.data, model.cashless
            new_actual_balance, old_actual_balance = form.actual_balance.data, model.actual_balance
            new_expenses = sum([e.money for e in form.expenses.data if e.type_cost == 'cash'])
            expenses_data = form.expenses.data
            old_expenses = sum([e.money for e in model.expenses if e.type_cost == 'cash'])

            new_consumption_coffee_arabika = form.consumption_coffee_arabika.data
            old_consumption_coffee_arabika = model.consumption_coffee_arabika

            new_consumption_coffee_blend = form.consumption_coffee_blend.data
            old_consumption_coffee_blend = model.consumption_coffee_blend

            new_consumption_milk = form.consumption_milk.data
            old_consumption_milk = model.consumption_milk

            new_consumption_panini = form.consumption_panini.data
            old_consumption_panini = model.consumption_panini

            new_consumption_hot_dogs = form.consumption_hot_dogs.data
            old_consumption_hot_dogs = model.consumption_hot_dogs

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
            if new_cash_balance != old_cash_balance:
                form.cash_balance.data = old_cash_balance

            if new_cashless != old_cashless:
                form.cashless.data = old_cashless

            if new_expenses != old_expenses:
                form.expenses.data = expenses_data

            if new_actual_balance != old_actual_balance:
                form.actual_balance.data = old_actual_balance

            if new_consumption_coffee_arabika != old_consumption_coffee_arabika:
                form.consumption_coffee_arabika.data = old_consumption_coffee_arabika

            if new_consumption_coffee_blend != old_consumption_coffee_blend:
                form.consumption_coffee_blend.data = old_consumption_coffee_blend

            if new_consumption_milk != old_consumption_milk:
                form.consumption_milk.data = old_consumption_milk

            if new_consumption_panini != old_consumption_panini:
                form.consumption_panini.data = old_consumption_panini

            if new_consumption_hot_dogs != old_consumption_hot_dogs:
                form.consumption_hot_dogs.data = old_consumption_hot_dogs

            self.after_model_change(form, model, False)
        return True

    def on_model_change(self, form, model, is_created):
        expanses = model.expenses
        expanses = sum([e.money for e in expanses if e.type_cost == 'cash'])
        last_actual_balance = model.shop.cash + expanses
        cash_balance = form.actual_balance.data - last_actual_balance
        remainder_of_day = cash_balance + form.cashless.data
        cashbox = remainder_of_day + expanses

        model.cash_balance = cash_balance
        model.remainder_of_day = remainder_of_day
        model.cashbox = cashbox

        if form.backdating.data:
            model.backdating = form.backdating.data
            return
        model.shop.cash += cash_balance + expanses
        model.shop.cashless += form.cashless.data

        model.consumption_coffee_arabika = model.shop.storage.coffee_arabika - float(form.coffee_arabika.data)
        model.consumption_coffee_blend = model.shop.storage.coffee_blend - float(form.coffee_blend.data)
        model.consumption_milk = model.shop.storage.milk - float(form.milk.data)
        model.consumption_panini = model.shop.storage.panini - int(form.panini.data)
        model.consumption_hot_dogs = model.shop.storage.hot_dogs - int(form.hot_dogs.data)

        model.shop.storage.coffee_arabika -= model.consumption_coffee_arabika
        model.shop.storage.coffee_blend -= model.consumption_coffee_blend
        model.shop.storage.milk -= model.consumption_milk
        model.shop.storage.panini -= model.consumption_panini
        model.shop.storage.hot_dogs -= model.consumption_hot_dogs

    def after_model_change(self, form, model, is_created):
        if not is_created:
            # TODO некоректно обрабатываются расходы
            # expanses = form.expenses.data
            # expanses = sum([e.money for e in expanses if e.type_cost == 'cash'])

            model.shop.cash -= form.cash_balance.data
            model.shop.cashless -= form.cashless.data
            model.shop.storage.coffee_arabika += float(form.consumption_coffee_arabika.data)
            model.shop.storage.coffee_blend += float(form.consumption_coffee_blend.data)
            model.shop.storage.milk += float(form.consumption_milk.data)
            model.shop.storage.panini += int(form.consumption_panini.data)
            model.shop.storage.hot_dogs += int(form.consumption_hot_dogs.data)
            self.session.commit()

    def on_model_delete(self, model):
        if model.backdating:
            return
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
        name=gettext('Название'),
        description=gettext('Описание'),
        barista=gettext('Бариста')
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
        'backdating',
        'timestamp',
        'is_global',
        'type_cost',
        'money',
        'categories',
        'shop'
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
    column_filters = ('timestamp', 'is_global', 'type_cost', 'categories', 'shop')
    column_searchable_list = ('timestamp',)
    column_labels = dict(
        timestamp=gettext('Дата'),
        is_global=gettext('Глобальная?'),
        type_cost=gettext('Тип траты'),
        money=gettext('Сумма траты'),
        categories=gettext('Категории'),
        shop=gettext('Кофейня')
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
            return
        money = model.money
        if model.type_cost == 'cash':
            model.shop.cash -= money
        else:
            model.shop.cashless -= money

    def after_model_change(self, form, model, is_created):
        if not is_created:
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

    def _list_product_name(view, context, model, name):
        prettified = dict(
            coffee_arabika=gettext('арабика'),
            coffee_blend=gettext('купаж'),
            milk=gettext('молоко'),
            panini=gettext('панини'),
            hot_dogs=gettext('хот-доги')
        )
        return Markup(f'{prettified[model.product_name]}')

    can_set_page_size = True
    column_list = ('timestamp', 'product_name', 'amount', 'money', 'storage')
    column_labels = dict(
        timestamp=gettext('Дата'),
        product_name=gettext('Название товара'),
        amount=gettext('Количество'),
        type_cost=gettext('Тип траты'),
        money=gettext('Сумма'),
        storage=gettext('Склад')
    )
    column_filters = ('timestamp', 'type_cost', 'storage')
    column_searchable_list = ('timestamp',)
    form_create_rules = ('backdating', 'timestamp', 'product_name', 'amount', 'type_cost', 'money', 'storage')
    form_edit_rules = ('backdating', 'timestamp', 'product_name', 'amount', 'type_cost', 'money', 'storage')
    column_formatters = dict(
        type_cost=lambda v, c, m, p: 'Наличка' if m.type_cost == 'cash' else 'Безнал',
        product_name=_list_product_name,
        money=_list_money,
        amount=_list_amount
    )
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
                    message=gettext('Количество не может быть нулевым, либо ниже нуля')
                )
            ]
        ),
        money=dict(
            validators=[
                InputRequired(),
                NumberRange(
                    min=-1,
                    message=gettext('Сумма не может быть нулевой, либо ниже нуля')
                )
            ]
        ),
        storage=dict(
            validators=[
                DataRequired(
                    message=gettext('Выберите склад')
                )
            ]
        )
    )
    form_extra_fields = dict(
        backdating=BooleanField(gettext('Обработка задним числом')),
        type_cost=RadioField(
            gettext('Тип траты'),
            choices=[
                ('cash', gettext('Наличка')),
                ('cashless', gettext('Безнал'))
            ],
            validators=[Required()],
            default='cash'
        ),
        product_name=SelectField(
            gettext('Название товара'),
            choices=[
                ('coffee_arabika', gettext('Арабика')),
                ('coffee_blend', gettext('Купаж')),
                ('milk', gettext('Молоко')),
                ('panini', gettext('Панини')),
                ('hot_dogs', gettext('Хот-доги'))
            ],
            validators=[Required()],
        )
    )
    form_widget_args = {
        'timestamp': {
            'data-date-format': u'DD.MM.YYYY HH:mm'
        },
        'money': {
            'placeholder': gettext('В гривнях')
        },
        'type_cost': {
            'class': 'form-check'
        },
        'amount': {
            'placeholder': gettext('Количество в кг, л, и поштучно')
        }
    }

    def update_model(self, form, model):
        try:
            new_money = form.money.data
            old_money = model.money

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
            if new_money != old_money:
                form.money.data = old_money
            if new_amount != old_amount:
                form.amount.data = old_amount
            if new_product_name != old_product_name:
                form.product_name.data = old_product_name
            self.after_model_change(form, model, False)
        return True

    def on_model_change(self, form, model, is_created):
        if form.backdating.data:
            return
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

    def after_model_change(self, form, model, is_created):
        if not is_created:
            if form.type_cost.data == 'cash':
                model.storage.shop.cash += form.money.data
            else:
                model.storage.shop.cashless += form.money.data

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
            self.session.commit()

    def on_model_delete(self, model):
        if model.backdating:
            return
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

    def _list_product_name(view, context, model, name):
        prettified = dict(
            coffee_arabika=gettext('арабика'),
            coffee_blend=gettext('купаж'),
            milk=gettext('молоко'),
            panini=gettext('панини'),
            hot_dogs=gettext('хот-доги')
        )
        return Markup(f'{prettified[model.product_name]}')

    can_set_page_size = True
    column_list = ('timestamp', 'product_name', 'amount', 'money', 'storage')
    column_labels = dict(
        timestamp=gettext('Дата'),
        product_name=gettext('Название товара'),
        amount=gettext('Количество'),
        type_cost=gettext('Тип траты'),
        money=gettext('Сумма'),
        storage=gettext('Склад')
    )
    column_filters = ('timestamp', 'product_name', 'type_cost')
    column_formatters = dict(
        type_cost=lambda v, c, m, p: 'Наличка' if m.type_cost == 'cash' else 'Безнал',
        product_name=_list_product_name,
        money=_list_money,
        amount=_list_amount
    )
    form_create_rules = ('backdating', 'timestamp', 'product_name', 'amount', 'type_cost', 'money', 'storage')
    form_edit_rules = ('backdating', 'timestamp', 'product_name', 'amount', 'type_cost', 'money', 'storage')
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
                    message=gettext('Количество не может быть нулевым, либо ниже нуля')
                )
            ]
        ),
        money=dict(
            validators=[
                InputRequired(),
                NumberRange(
                    min=-1,
                    message=gettext('Сумма не может быть нулевой, либо ниже нуля')
                )
            ]
        ),
        storage=dict(
            validators=[DataRequired(message=gettext('Выберите склад'))]
        )
    )
    form_extra_fields = dict(
        backdating=BooleanField(gettext('Обработка задним числом')),
        type_cost=RadioField(
            gettext('Тип траты'),
            choices=[
                ('cash', gettext('Наличка')),
                ('cashless', gettext('Безнал'))
            ],
            validators=[Required()],
            default='cash'
        ),
        product_name=SelectField(
            gettext('Название товара'),
            choices=[
                ('coffee_arabika', gettext('Арабика')),
                ('coffee_blend', gettext('Купаж'))
            ],
            validators=[Required()],
        )
    )
    form_widget_args = {
        'timestamp': {
            'data-date-format': u'DD.MM.YYYY HH:mm'
        },
        'money': {
            'placeholder': gettext('В гривнях')
        },
        'type_cost': {
            'class': 'form-check'
        },
        'amount': {
            'placeholder': gettext('Количество в кг, л, и поштучно')
        }
    }

    def update_model(self, form, model):
        try:
            new_money = form.money.data
            old_money = model.money

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
            if new_money != old_money:
                form.money.data = old_money
            if new_amount != old_amount:
                form.amount.data = old_amount
            if new_product_name != old_product_name:
                form.product_name.data = old_product_name
            self.after_model_change(form, model, False)
        return True

    def on_model_change(self, form, model, is_created):
        if form.backdating.data:
            return

        if form.product_name.data == 'coffee_blend':
            model.storage.coffee_blend -= float(form.amount.data)
        else:
            model.storage.coffee_arabika -= float(form.amount.data)

        if form.type_cost.data == 'cash':
            model.storage.shop.cash += form.money.data
        else:
            model.storage.shop.cashless += form.money.data

    def after_model_change(self, form, model, is_created):
        if not is_created:
            if form.type_cost.data == 'cash':
                model.storage.shop.cash -= form.money.data
            else:
                model.storage.shop.cashless -= form.money.data

            if form.product_name.data == 'coffee_blend':
                model.storage.coffee_blend += float(form.amount.data)
            else:
                model.storage.coffee_arabika += float(form.amount.data)
            self.session.commit()

    def on_model_delete(self, model):
        if model.backdating:
            return
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

    def _list_product_name(view, context, model, name):
        prettified = dict(
            coffee_arabika=gettext('арабика'),
            coffee_blend=gettext('купаж'),
            milk=gettext('молоко'),
            panini=gettext('панини'),
            hot_dogs=gettext('хот-доги')
        )
        return Markup(f'{prettified[model.product_name]}')

    can_set_page_size = True
    column_list = ('timestamp', 'product_name', 'amount', 'storage')
    column_labels = dict(
        timestamp=gettext('Дата'),
        product_name=gettext('Название товара'),
        amount=gettext('Количество'),
        storage=gettext('Склад')
    )
    column_filters = ('timestamp', 'product_name')
    column_formatters = dict(
        timestamp=lambda v, c, m, p: m.timestamp.date().strftime("%d.%m.%Y"),
        product_name=_list_product_name,
        amount=_list_amount
    )
    form_create_rules = ('timestamp', 'product_name', 'amount', 'storage')
    form_edit_rules = ('timestamp', 'product_name', 'amount', 'storage')
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
                ('hot_dogs', gettext('Хот-доги'))
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

    def after_model_change(self, form, model, is_created):
        if not is_created:
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
        else:
            model.storage.hot_dogs += model.amount


class CategoryAdmin(ModelView):
    can_view_details = True
    column_labels = dict(
        name=gettext('Название категории'),
        expense=gettext('Расходы')
    )
    form_create_rules = ('name',)
    form_args = dict(
        name=dict(
            validators=[DataRequired()]
        )
    )
    column_editable_list = ('name',)
    form_widget_args = {
        'name': {
            'placeholder': gettext('Название для расходов')
        }
    }
