"""
Init package to admin panel
"""


import logging
from datetime import date

from flask import abort, redirect, request, url_for
from flask_admin.contrib import sqla
from flask_admin.model import typefmt
from flask_security import current_user

from app.models import Storage

from .exceptions import UserRoleException

log = logging.getLogger("flask-admin.sqla")


class ModelView(sqla.ModelView):
    """Base Model View"""

    column_type_formatters = dict(typefmt.BASE_FORMATTERS)
    column_type_formatters.update(
        {date: lambda view, value: value.strftime("%d.%m.%Y")}
    )

    details_template = "admin/model/details.html"

    @property
    def can_delete(self):
        """Delete operation, depends on role"""
        try:
            is_admin = current_user.has_role("admin")
            is_active = current_user.is_active and current_user.is_authenticated
            return is_active and is_admin
        except UserRoleException:
            pass
        return False

    @property
    def can_create(self):
        """Create operation, depends on role"""
        try:
            is_admin = current_user.has_role("admin")
            is_active = current_user.is_active and current_user.is_authenticated
            return is_active and is_admin
        except UserRoleException:
            pass
        return False

    def is_accessible(self):
        """Is accessible, depends on role"""
        try:
            is_active = current_user.is_active and current_user.is_authenticated

            is_admin = current_user.has_administrative_rights
            is_moderator = current_user.has_moderator_rights

            return is_active and is_admin or is_moderator
        except UserRoleException:
            return False

    def _handle_view(self, name, **kwargs):
        """Login required redirection"""
        if not self.is_accessible():
            if current_user.is_authenticated:
                abort(403)
            else:
                return redirect(url_for("login", next=request.url))

    def get_model_data(self):
        """Return model data"""
        view_args = self._get_list_extra_args()
        sort_column = self._get_column_by_idx(view_args.sort)
        if sort_column is not None:
            sort_column = sort_column[0]

        _, data = self.get_list(
            view_args.page,
            sort_column,
            view_args.sort_desc,
            view_args.search,
            view_args.filters,
            page_size=self.page_size,
        )
        return data


class ModeratorView(ModelView):
    """Base moderator view in admin panel"""

    @property
    def shop_id(self):
        """
        Must be overridden in a child class,
        the correct execution of get_query and get_count_query depends on the shop_id
        """
        return self.model.id

    @staticmethod
    def staff_shops_id():
        """Get shop list by current_user"""
        shop_ids = (shop.id for shop in current_user.shop)
        return shop_ids

    def get_query(self):
        """Query depends on role"""
        shop_id = self.shop_id
        _query = super().get_query()
        if not current_user.has_role("admin"):
            _query = _query.filter(shop_id.in_(self.staff_shops_id()))
        return _query

    def get_count_query(self):
        """Count shops depends on role"""
        shop_id = self.shop_id
        _query = super().get_count_query()
        if not current_user.has_role("admin"):
            _query = _query.filter(shop_id.in_(self.staff_shops_id()))
        return _query


class StorageModeratorView(ModelView):
    """Storage moderator view in admin panel"""

    @staticmethod
    def staff_storage_id():
        """Get storage list by current_user"""
        storage_ids = (storage.id for storage in current_user.storage)
        return storage_ids

    def get_query(self):
        """Query depends on role"""
        _query = super().get_query()
        if not current_user.has_role("admin"):
            _query = self.model.query.join(self.model.storage).filter(
                Storage.id.in_(self.staff_storage_id())
            )
        return _query

    def get_count_query(self):
        """Count shops depends on role"""
        _query = super().get_count_query()
        if not current_user.has_role("admin"):
            _query = _query.join(self.model.storage).filter(
                Storage.id.in_(self.staff_storage_id())
            )
        return _query
