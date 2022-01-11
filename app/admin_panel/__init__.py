import logging
from datetime import date
from flask import redirect, request, url_for, abort
from flask_admin.contrib import sqla
from flask_admin.model import typefmt
from app.models import Storage
from flask_security import current_user

log = logging.getLogger("flask-admin.sqla")


class ModelView(sqla.ModelView):
    column_type_formatters = dict(typefmt.BASE_FORMATTERS)
    column_type_formatters.update({
        date: lambda view, value: value.strftime('%d.%m.%Y')
    })
    
    details_template = "admin/model/details.html"

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
        if not self.is_accessible():
            if current_user.is_authenticated:
                abort(403)
            else:
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


class ModeratorView(ModelView):
    @property 
    def shop_id(self):
        """
        Необходимо переопределить в дочернем классе, от shop_id зависит корректное выполнение get_query и get_count_query.
        """
        return self.model.id

    def staff_shops_id(self):
        shop_ids = (shop.id for shop in current_user.shop)
        return shop_ids
        
    def get_query(self):
        shop_id = self.shop_id
        _query = super(ModeratorView, self).get_query()
        if not current_user.has_role('admin'):
            _query = _query.filter(shop_id.in_(self.staff_shops_id()))
        return _query
       
    def get_count_query(self):
        shop_id = self.shop_id
        _query = super(ModeratorView, self).get_count_query()
        if not current_user.has_role('admin'):
            _query = _query.filter(shop_id.in_(self.staff_shops_id()))
        return _query


class StorageModeratorView(ModelView):
    def staff_storage_id(self):
        storage_ids = (storage.id for storage in current_user.storage)
        return storage_ids

    def get_query(self):
        _query = super(StorageModeratorView, self).get_query()
        if not current_user.has_role('admin'):
            _query = self.model.query.join(self.model.storage).filter(Storage.id.in_(self.staff_storage_id()))
        return _query

    def get_count_query(self):
        _query = super(StorageModeratorView, self).get_count_query()
        if not current_user.has_role('admin'):
            _query = _query.join(self.model.storage).filter(Storage.id.in_(self.staff_storage_id()))
        return _query


from .barista import BaristaAdmin
from .by_weight import ByWeightAdmin
from .category import CategoryAdmin
from .collection_funds import CollectionFundsAdmin
from .deposit_funds import DepositFundsAdmin
from .expense import ExpenseAdmin
from .index import IndexAdmin
from .report import ReportAdmin
from .role import RoleAdmin
from .shop import ShopAdmin
from .shop_equipment import ShopEquipmentAdmin
from .storage import StorageAdmin
from .supply import SupplyAdmin
from .transfer_product import TransferProductAdmin
from .write_off import WriteOffAdmin
