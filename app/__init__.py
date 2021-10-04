from logging.handlers import RotatingFileHandler
import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_admin import Admin
from flask_moment import Moment
from flask_admin.contrib.sqla import ModelView
from flask_security import Security, SQLAlchemyUserDatastore
from flask_debugtoolbar import DebugToolbarExtension
from werkzeug.security import generate_password_hash
from config import DevelopmentConfig


app = Flask(__name__)
app.config.from_object(DevelopmentConfig)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
login = LoginManager(app)
admin = Admin(app, name='Not Detail Poster', template_mode='bootstrap4')
toolbar = DebugToolbarExtension(app)
moment = Moment(app)

from app import views, models, forms, admin, errors

user_datastore = SQLAlchemyUserDatastore(db, models.Barista, models.Role)
security = Security(app, user_datastore)


admin.add_view(ModelView(models.CoffeeShop, db.session, name='Кофейня', category="CoffeShop"))
admin.add_view(ModelView(models.CoffeeShopEquipment, db.session, name='Оборудование', category="CoffeShop"))
admin.add_view(ModelView(models.Warehouse, db.session,  name='Склад', category="CoffeShop"))
admin.add_view(ModelView(models.Supply, db.session,  name='Поступления', category="CoffeShop"))
admin.add_view(ModelView(models.ByWeight, db.session,  name='Развес', category="CoffeShop"))
admin.add_view(ModelView(models.WriteOff, db.session,  name='Списания', category="CoffeShop"))
admin.add_view(ModelView(models.Expense, db.session, name='Расходы'))
admin.add_view(ModelView(models.DailyReport, db.session, name='Отчеты'))
admin.add_view(ModelView(models.Barista, db.session, name='Сотрудники'))
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