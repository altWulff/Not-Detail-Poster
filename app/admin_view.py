from sqlalchemy import func
from flask import abort, redirect, request, url_for, flash
from flask_security import current_user
from flask_admin.contrib import sqla
from flask_admin.model.template import macro
from flask_admin import BaseView, expose
from app.models import DailyReport, CoffeeShop, Barista
from app.admin_forms import ReportsFilterForm


class ModelView(sqla.ModelView):
    def is_accessible(self):
        return (current_user.is_active and current_user.is_authenticated and current_user.has_role('admin')
                )

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


class ReportsAdminView(BaseView):
    @expose('/', methods=('POST', 'GET'))
    def index(self):
        form = ReportsFilterForm()
        reports = DailyReport.query.all()
        form.target_coffee_shop.choices = [(g.id, g.place_name) for g in CoffeeShop.query.order_by('place_name')]
        form.target_barista.choices = [(g.id, g.name) for g in Barista.query.order_by('name')]
        if request.method == "POST":
            reports = DailyReport.query.filter_by(coffee_shop_id=form.target_coffee_shop.data).filter_by(barista_name=form.target_barista.data).first_or_404()
            flash('...')
            return self.render('admin/reports_filter.html', reports=reports, form=form)
        return self.render('admin/reports_filter.html', reports=reports, form=form)


class CoffeeShopAdmin(ModelView):
    column_searchable_list = ('place_name', 'address')
    column_labels = dict(
        place_name='Название',
        address='Адрес',
        cash='Наличка',
        cashless='Безнал'
    )


class CoffeeShopEquipmentAdmin(ModelView):
    column_searchable_list = ('coffee_machine', )
    column_labels = dict(
        coffee_machine='Кофе Машина',
        grinder_1='Кофемолка 1',
        grinder_2='Кофемолка 2',
        coffee_shop='Кофейня'
    )


class WarehouseAdmin(ModelView):
    column_labels = dict(
        coffee_arabika='Арабика',
        coffee_blend='Бленд',
        milk='Молоко',
        panini='Панини',
        hot_dogs='Хот-доги',
        coffee_shop='Кофейня'
    )
    column_formatters = dict(
        coffee_arabika=lambda v, c, m, p: f'{m.coffee_arabika} кг',
        coffee_blend=lambda v, c, m, p: f'{m.coffee_blend} кг',
        milk=lambda v, c, m, p: f'{m.milk} л',
        panini=lambda v, c, m, p: f'{m.panini} шт.',
        hot_dogs=lambda v, c, m, p: f'{m.hot_dogs} шт.',
    )


class BaristaAdmin(ModelView):
    column_filters = ('name', 'phone_number', 'email')
    column_searchable_list = ('name', 'phone_number', 'email')
    column_exclude_list = ('password_hash', 'roles', 'daily_reports', 'id', 'salary_rate')
    column_labels = dict(
        name='Имя',
        phone_number='Тел.',
        email='Емейл',
        coffee_shop='Кофейня',
        daily_reports='Отчеты',
        roles='Доступ',
    )
    column_formatters = dict(confirmed_at=lambda v, c, m, p: m.confirmed_at.date().strftime("%d.%m.%Y"))


class DailyReportAdmin(ModelView):
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
    column_filters = ('timestamp', )
    column_labels = dict(
        coffee_shop='Кофейня',
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
    )
    column_formatters = dict(timestamp=lambda v, c, m, p: m.timestamp.date().strftime("%d.%m.%Y"))
    list_template = 'admin/model/custom_list.html'
    page_size = 5

    def page_cashbox(self, current_page):
        # this should take into account any filters/search inplace
        _query = self.get_query().limit(self.page_size).offset(current_page * self.page_size)
        return sum([p.cashbox for p in _query])

    def total_cashbox(self):
        # this should take into account any filters/search inplace
        return self.session.query(func.sum(DailyReport.cashbox)).scalar()

    def page_cash_balance(self, current_page):
        _query = self.session.query(DailyReport).limit(self.page_size).offset(current_page * self.page_size)
        return sum([p.cash_balance for p in _query])

    def total_cash_balance(self):
        return self.session.query(func.sum(DailyReport.cash_balance)).scalar()

    def page_remainder_of_day(self, current_page):
        _query = self.session.query(DailyReport).limit(self.page_size).offset(current_page * self.page_size)
        return sum([p.remainder_of_day for p in _query])

    def total_remainder_of_day(self):
        return self.session.query(func.sum(DailyReport.remainder_of_day)).scalar()

    def page_cashless(self, current_page):
        _query = self.session.query(DailyReport).limit(self.page_size).offset(current_page * self.page_size)
        return sum([p.cashless for p in _query])

    def total_cashless(self):
        return self.session.query(func.sum(DailyReport.cashless)).scalar()

    def page_actual_balance(self, current_page):
        _query = self.session.query(DailyReport).limit(self.page_size).offset(current_page * self.page_size)
        return sum([p.actual_balance for p in _query])

    def total_actual_balance(self):
        return self.session.query(func.sum(DailyReport.actual_balance)).scalar()

    def render(self, template, **kwargs):
        # we are only interested in the list page
        if template == 'admin/model/custom_list.html':
            # append a summary_data dictionary into kwargs
            _current_page = kwargs['page']
            kwargs['summary_data'] = [
                {'title': 'На странице', 'name': None, 'cashbox': self.page_cashbox(_current_page)},
                {'title': 'Полная сумма', 'name': None, 'cashbox': self.total_cashbox()},
                {'title': 'На странице', 'name': None, 'cash_balance': self.page_cash_balance(_current_page)},
                {'title': 'Полная сумма', 'name': None, 'cash_balance': self.total_cash_balance()},
                {'title': 'На странице', 'name': None, 'remainder_of_day': self.page_remainder_of_day(_current_page)},
                {'title': 'Полная сумма', 'name': None, 'remainder_of_day': self.total_remainder_of_day()},
                {'title': 'На странице', 'name': None, 'cashless': self.page_cashless(_current_page)},
                {'title': 'Полная сумма', 'name': None, 'cashless': self.total_cashless()},
                {'title': 'На странице', 'name': None, 'actual_balance': self.page_actual_balance(_current_page)},
                {'title': 'Полная сумма', 'name': None, 'actual_balance': self.total_actual_balance()},
            ]
        return super(DailyReportAdmin, self).render(template, **kwargs)


class RoleAdmin(ModelView):
    column_labels = dict(
        name='Название',
        description='Описание',
        barista='Бариста'
    )
    column_formatters = dict(name=lambda v, c, m, p: m.name.title())
