import logging
from logging.handlers import RotatingFileHandler
import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_admin import Admin
from flask_moment import Moment
from flask_security import Security, SQLAlchemyUserDatastore
from flask_debugtoolbar import DebugToolbarExtension
from flask_admin import helpers as admin_helpers
from config import DevelopmentConfig

app = Flask(__name__)
app.config.from_object(DevelopmentConfig)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
login = LoginManager(app)
admin = Admin(app, name='Not Detail Poster', template_mode='bootstrap4')
toolbar = DebugToolbarExtension(app)
moment = Moment(app)

from app import routes, models, forms, routes
from app.routes import auth
from app.routes import errors
from app.routes.user import user
from app.routes.menu import menu
from app.routes.report import report
from app.routes.errors import errors
from app.admin_view import (
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


@security.context_processor
def security_context_processor():
    return dict(
        admin_base_template=admin.base_template,
        admin_view=admin.index_view,
        h=admin_helpers,
    )

app.register_blueprint(user)
app.register_blueprint(menu)
app.register_blueprint(report)

admin.add_view(ShopAdmin(models.Shop, db.session, name='Все кофейни', category="Кофейни"))
admin.add_view(ShopEquipmentAdmin(models.ShopEquipment, db.session, name='Оборудование', category="Кофейни"))
admin.add_view(StorageAdmin(models.Storage, db.session, name='Все товары', category="Склады"))
admin.add_view(ReportAdmin(models.Report, db.session, name='Отчеты', category='Статистика'))
admin.add_view(SupplyAdmin(models.Supply, db.session,  name='Поступления', category="Движения товаров"))
admin.add_view(ByWeightAdmin(models.ByWeight, db.session,  name='Развес', category="Движения товаров"))
admin.add_view(WriteOffAdmin(models.WriteOff, db.session,  name='Списания', category="Движения товаров"))
admin.add_view(ExpenseAdmin(models.Expense, db.session, name='Расходы', category='Кассовые средства'))
admin.add_view(BaristaAdmin(models.Barista, db.session, name='Сотрудники'))
admin.add_view(CategoryAdmin(models.Category, db.session, name='Категории', category='Разное'))
admin.add_view(RoleAdmin(models.Role, db.session, name='Доступ', category='Разное'))


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
