from flask import render_template, redirect, url_for, flash, Blueprint, request
from flask_security import login_required, current_user
from flask_babelex import _
from app import db
from app.forms import EditProfileForm, NewPassword
from app.models import Barista

user = Blueprint('user', __name__, url_prefix='/user')


@user.route('/<user_name>')
@login_required
def profile(user_name):
    user_obj = Barista.query.filter_by(name=user_name).first_or_404()
    return render_template('user/user.html', user=user_obj)


@user.route('/edit_profile', methods=('GET', 'POST'))
@login_required
def edit():
    form = EditProfileForm(current_user.name, current_user.phone_number, current_user.email)
    if form.validate_on_submit():
        current_user.name = form.name.data
        current_user.phone_number = form.phone_number.data
        current_user.email = form.email.data
        db.session.commit()
        flash(_('Ваши изменения сохранены.'))
        return redirect(url_for('user.profile', user_name=current_user))
    elif request.method == 'GET':
        form.name.data = current_user.name
        form.phone_number.data = current_user.phone_number
        form.email.data = current_user.email
    return render_template('user/user_edit.html', user=current_user, form=form)


@user.route('/new_password', methods=('POST',  'GET'))
@login_required
def change_password():
    form = NewPassword()
    if form.validate_on_submit():
        current_user.password = form.password.data
        db.session.commit()
        flash(_('Ваши изменения сохранены.'))
        return redirect(url_for('user.profile', user_name=current_user))
    return render_template('user/user_password.html', user=current_user, form=form)