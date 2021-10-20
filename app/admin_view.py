from flask import abort, redirect, request, url_for
from flask_security import current_user
from flask_admin.contrib import sqla
from flask_admin.model.template import macro


class MyModelView(sqla.ModelView):
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


class BaristaAdmin(MyModelView):
    column_filters = ('name', 'phone_number', 'email')
    column_searchable_list = ('name', 'phone_number', 'email')
    column_exclude_list = ('password_hash', 'roles', 'daily_reports', 'id')


class DailyReportAdmin(MyModelView):
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