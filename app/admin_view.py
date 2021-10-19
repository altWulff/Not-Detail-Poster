from flask import abort, redirect, request, url_for
from flask_security import current_user
from flask_admin.contrib import sqla


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
