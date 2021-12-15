from flask import redirect, url_for
from flask_admin import AdminIndexView, expose
from flask_security import current_user
from app.models import Shop, Expense, Supply


class IndexAdmin(AdminIndexView):
    @property
    def can_view(self):
        try:
            is_admin = current_user.has_role('admin') or current_user.has_role('moderator')
            is_active = current_user.is_active and current_user.is_authenticated
            return is_active and is_admin
        except:
            pass
        return False

    @expose('/', methods=('GET', 'POST'))
    def index(self):
        if not self.can_view:
            return redirect(url_for('home'))
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
