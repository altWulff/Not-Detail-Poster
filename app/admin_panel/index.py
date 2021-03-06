"""Module contains index view for admin panel"""

from flask import redirect, url_for
from flask_admin import AdminIndexView, expose
from flask_security import current_user

from app.models import Expense, Shop, Storage, Supply

from .exceptions import UserRoleException


class IndexAdmin(AdminIndexView):
    """Index view for admin panel"""

    @property
    def can_view(self):
        """User can view, depends on role"""
        try:
            is_admin = current_user.has_role("admin") or current_user.has_role(
                "moderator"
            )
            is_active = current_user.is_active and current_user.is_authenticated
            return is_active and is_admin
        except UserRoleException:
            pass
        return False

    @staticmethod
    def staff_shops_id():
        """Wolk place list"""
        shop_ids = (shop.id for shop in current_user.shop)
        return shop_ids

    @staticmethod
    def staff_storage_id():
        """Storage list"""
        storage_ids = (storage.id for storage in current_user.storage)
        return storage_ids

    def shop_query(self):
        """Shop query, different query for user role"""
        _query = Shop.query
        if not current_user.has_role("admin"):
            _query = _query.filter(Shop.id.in_(self.staff_shops_id()))
        return _query

    def expense_query(self, type_cost):
        """Expense query, different query for user role"""
        _query = Expense.query.filter_by(type_cost=type_cost)
        shop_id = Expense.shop_id
        if not current_user.has_role("admin"):
            _query = _query.filter(shop_id.in_(self.staff_shops_id()))
        return _query

    def supply_query(self, type_cost):
        """Supply query, different query for user role"""
        _query = Supply.query.filter_by(type_cost=type_cost)
        if not current_user.has_role("admin"):
            _query = _query.join(Supply.storage).filter(
                Storage.id.in_(self.staff_storage_id())
            )
        return _query

    @expose("/", methods=("GET", "POST"))
    def index(self):
        """Prepare to render view and call render template"""
        if not self.can_view:
            return redirect(url_for("home"))
        template = "admin/index.html"

        _query_exp_cash = self.expense_query(type_cost="cash").all()
        _query_exp_cashless = self.expense_query(type_cost="cashless").all()
        _query_supply_cash = self.supply_query(type_cost="cash").all()
        _query_supply_cashless = self.supply_query(type_cost="cashless").all()
        _query_shop = self.shop_query().all()

        kwargs = {
            "shop_cash": sum([s.cash for s in _query_shop]),
            "shop_cashless": sum([s.cashless for s in _query_shop]),
            "exp_cash": sum([e.money for e in _query_exp_cash]),
            "exp_cashless": sum([e.money for e in _query_exp_cashless]),
        }
        kwargs["exp_cash"] += sum([s.money for s in _query_supply_cash])
        kwargs["exp_cashless"] += sum([s.money for s in _query_supply_cashless])
        kwargs["all_shop"] = kwargs["shop_cash"] + kwargs["shop_cashless"]
        kwargs["all_exp"] = kwargs["exp_cash"] + kwargs["exp_cashless"]
        return self.render(template, **kwargs)
