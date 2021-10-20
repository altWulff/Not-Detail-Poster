import logging
from logging.handlers import RotatingFileHandler
import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_admin import Admin
from flask_moment import Moment
#from flask_admin.contrib.sqla import ModelView
from flask_security import Security, SQLAlchemyUserDatastore
from flask_debugtoolbar import DebugToolbarExtension
from config import DevelopmentConfig, ProductionConfig
from flask_admin import helpers as admin_helpers

app = Flask(__name__)
app.config.from_object(DevelopmentConfig)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
login = LoginManager(app)
admin = Admin(app, name='Not Detail Poster', template_mode='bootstrap4')
toolbar = DebugToolbarExtension(app)
moment = Moment(app)

from app import routes, models, forms, routes
from app.routes import errors
from app.routes.user import user
from app.routes.menu import menu
from app.routes.report import report
from app.routes.errors import errors
from app.admin_view import MyModelView as ModelView
from app.admin_view import BaristaAdmin, DailyReportAdmin
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

admin.add_view(ModelView(models.CoffeeShop, db.session, name='Все кофейни', category="Кофейни"))
admin.add_view(ModelView(models.CoffeeShopEquipment, db.session, name='Оборудование', category="Кофейни"))
admin.add_view(ModelView(models.Warehouse, db.session,  name='Все товары', category="Склады"))
admin.add_view(DailyReportAdmin(models.DailyReport, db.session, name='Отчеты', category='Статистика'))
admin.add_view(ModelView(models.Supply, db.session,  name='Поступления', category="Движения товаров"))
admin.add_view(ModelView(models.ByWeight, db.session,  name='Развес', category="Движения товаров"))
admin.add_view(ModelView(models.WriteOff, db.session,  name='Списания', category="Движения товаров"))
admin.add_view(ModelView(models.Expense, db.session, name='Расходы', category='Кассовые средства'))
admin.add_view(BaristaAdmin(models.Barista, db.session, name='Сотрудники'))
admin.add_view(ModelView(models.Role, db.session, name='Роли'))
# admin.add_view(ModelView(models.expenses, db.session))

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
