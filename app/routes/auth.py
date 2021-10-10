from . import datetime
from . import render_template, redirect, url_for, flash, Blueprint
from . import login_required, login_user, logout_user, current_user, roles_required
from . import app, db, login
from . import LoginForm, RegistrationForm
from . import Barista

auth = Blueprint('auth', __name__, url_prefix='/auth')


@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    app.logger.info(form.validate_on_submit())
    if form.validate_on_submit():
        user = Barista.query.filter_by(name=form.name.data).first()
        if user is None:
            flash('Invalid name, phone number or password')
            return redirect(url_for('auth.login'))
        login_user(user, remember=form.remember_me.data)
        return redirect('index')
    return render_template('auth/login.html', title='Sign In', form=form)


@auth.route('/new_staff', methods=['GET', 'POST'])
def create_new_staff():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = Barista(name=form.name.data,
                       phone_number=form.phone_number.data,
                       email=form.email.data)
        user.set_password(form.password.data)
        user.confirmed_at = datetime.utcnow()
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('auth.login'))
    return render_template('auth/new_staff.html', form=form)


@auth.route('/logout')
def logout():
    logout_user()
    return redirect('index')
