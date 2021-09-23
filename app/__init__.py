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

from app import views, models, forms, admin

user_datastore = SQLAlchemyUserDatastore(db, models.Barista, models.Role)
security = Security(app, user_datastore)


admin.add_view(ModelView(models.CoffeeShop, db.session, name='Кофейня', category="CoffeShop"))
admin.add_view(ModelView(models.CoffeeShopEquipment, db.session, name='Оборудование', category="CoffeShop"))
admin.add_view(ModelView(models.Warehouse, db.session,  name='Склад', category="CoffeShop"))
admin.add_view(ModelView(models.Expense, db.session, name='Расходы', category="Daily"))
admin.add_view(ModelView(models.DailyReport, db.session, name='Отчеты', category="Daily"))
admin.add_view(ModelView(models.Barista, db.session, name='Сотрудники'))
admin.add_view(ModelView(models.Role, db.session, name='Роли'))
# admin.add_view(ModelView(models.expenses, db.session))
