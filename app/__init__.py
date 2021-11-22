import os
import logging
from logging.handlers import RotatingFileHandler
from flask import Flask, request, url_for
from flask_babelex import Babel
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_admin import Admin
from flask_moment import Moment
from flask_security import Security, SQLAlchemyUserDatastore
from flask_debugtoolbar import DebugToolbarExtension
from flask_admin import helpers as admin_helpers
from flask_admin.menu import MenuLink
from flask_modals import Modal
from flask_babelex import lazy_gettext as _l
from config import DevelopmentConfig

app = Flask(__name__)
app.config.from_object(DevelopmentConfig)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
login = LoginManager(app)
login.login_message = _l('Please log in to access this page.')
toolbar = DebugToolbarExtension(app)
moment = Moment(app)
modal = Modal(app)
babel = Babel(app)

from app import routes, models, forms, routes
from app.routes import auth
from app.routes import errors
from app.routes.user import user
from app.routes.menu import menu
from app.routes.report import report
from app.routes.errors import errors
from app.admin_view import (
    IndexAdmin,
    ModelView,
    ShopAdmin,
    ShopEquipmentAdmin,
    StorageAdmin,
    ReportAdmin,
    BaristaAdmin,
    RoleAdmin,
    ExpenseAdmin,
    ByWeightAdmin,
    SupplyAdmin,
    WriteOffAdmin,
    CategoryAdmin
)
user_datastore = SQLAlchemyUserDatastore(db, models.Barista, models.Role)
security = Security(app, user_datastore)


app.register_blueprint(user)
app.register_blueprint(menu)
app.register_blueprint(report)

admin = Admin(app, name='Not Detail Poster', template_mode='bootstrap4', index_view=IndexAdmin(name=_l('Обзор')))
admin.add_view(ShopAdmin(models.Shop, db.session, name=_l('Кофейни'), category=_l("Кофейни")))
admin.add_view(ShopEquipmentAdmin(models.ShopEquipment, db.session, name=_l('Оборудование'), category=_l("Кофейни")))
admin.add_view(StorageAdmin(models.Storage, db.session, name=_l('Товары'), category=_l("Кофейни")))
admin.add_view(ReportAdmin(models.Report, db.session, name=_l('Отчеты'), category=_l('Статистика')))
admin.add_view(SupplyAdmin(models.Supply, db.session,  name=_l('Поступления'), category=_l("Движения товаров")))
admin.add_view(ByWeightAdmin(models.ByWeight, db.session,  name=_l('Развес'), category=_l("Движения товаров")))
admin.add_view(WriteOffAdmin(models.WriteOff, db.session,  name=_l('Списания'), category=_l("Движения товаров")))
admin.add_view(ExpenseAdmin(models.Expense, db.session, name=_l('Расходы'), category=_l('Кассовые средства')))
admin.add_view(BaristaAdmin(models.Barista, db.session, name=_l('Сотрудники')))
admin.add_view(CategoryAdmin(models.Category, db.session, name=_l('Категории'), category=_l('Разное')))
admin.add_view(RoleAdmin(models.Role, db.session, name=_l('Доступ'), category=_l('Разное')))
admin.add_link(MenuLink(name=_l('Выход'), url='/index'))


@security.context_processor
def security_context_processor():
    return dict(
        admin_base_template=admin.base_template,
        admin_view=admin.index_view,
        h=admin_helpers,
    )


@babel.localeselector
def get_locale():
    return request.accept_languages.best_match(app.config['LANGUAGES'])


if not app.debug:
    if not os.path.exists('logs'):
        os.mkdir('logs')
    file_handler = RotatingFileHandler('logs/not_detail_poster.log', maxBytes=10240, backupCount=10)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)

    app.logger.setLevel(logging.INFO)
    app.logger.info(' Not Detail Poster startup')
