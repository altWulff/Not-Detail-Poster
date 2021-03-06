"""
Main module
define app, and extensions
add admin models and views
"""


import logging
import os
from datetime import datetime
from logging.handlers import RotatingFileHandler, SMTPHandler

from flask import Flask, request, url_for
from flask_admin import Admin
from flask_admin import helpers as admin_helpers
from flask_admin.menu import MenuLink
from flask_babelex import Babel
from flask_babelex import lazy_gettext as _l
from flask_debugtoolbar import DebugToolbarExtension
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_modals import Modal
from flask_moment import Moment
from flask_security import Security, SQLAlchemyUserDatastore
from flask_sqlalchemy import SQLAlchemy

from config import ProductionConfig

app = Flask(__name__)
app.config.from_object(ProductionConfig)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
login = LoginManager(app)
login.login_message = _l("Please log in to access this page.")
toolbar = DebugToolbarExtension(app)
moment = Moment(app)
modal = Modal(app)
babel = Babel(app)

date_today = datetime(
    datetime.today().year, datetime.today().month, datetime.today().day
)

from app.admin_panel.barista import BaristaAdmin
from app.admin_panel.by_weight import ByWeightAdmin
from app.admin_panel.category import CategoryAdmin
from app.admin_panel.collection_funds import CollectionFundsAdmin
from app.admin_panel.deposit_funds import DepositFundsAdmin
from app.admin_panel.expense import ExpenseAdmin
from app.admin_panel.index import IndexAdmin
from app.admin_panel import ModelView
from app.admin_panel.report import ReportAdmin
from app.admin_panel.role import RoleAdmin
from app.admin_panel.shop import ShopAdmin
from app.admin_panel.shop_equipment import ShopEquipmentAdmin
from app.admin_panel.storage import StorageAdmin
from app.admin_panel.supply import SupplyAdmin
from app.admin_panel.transfer_product import TransferProductAdmin
from app.admin_panel.write_off import WriteOffAdmin

from app import models
from app.routes import auth, errors
from app.routes.menu import menu
from app.routes.report import report
from app.routes.user import user


user_datastore = SQLAlchemyUserDatastore(db, models.Barista, models.Role)
security = Security(app, user_datastore)


app.register_blueprint(user)
app.register_blueprint(menu)
app.register_blueprint(report)

admin = Admin(
    app,
    name="Not Detail Poster",
    template_mode="bootstrap4",
    index_view=IndexAdmin(name=_l("??????????")),
)
admin.add_view(
    ShopAdmin(models.Shop, db.session, name=_l("??????????????"), category=_l("??????????????"))
)
admin.add_view(
    ShopEquipmentAdmin(
        models.ShopEquipment,
        db.session,
        name=_l("????????????????????????"),
        category=_l("??????????????"),
    )
)
admin.add_view(
    StorageAdmin(models.Storage, db.session, name=_l("????????????"), category=_l("??????????????"))
)
admin.add_view(
    ReportAdmin(models.Report, db.session, name=_l("????????????"), category=_l("????????????????????"))
)
admin.add_view(
    SupplyAdmin(
        models.Supply,
        db.session,
        name=_l("??????????????????????"),
        category=_l("???????????????? ??????????????"),
    )
)
admin.add_view(
    ByWeightAdmin(
        models.ByWeight, db.session, name=_l("????????????"), category=_l("???????????????? ??????????????")
    )
)
admin.add_view(
    WriteOffAdmin(
        models.WriteOff,
        db.session,
        name=_l("????????????????"),
        category=_l("???????????????? ??????????????"),
    )
)
admin.add_view(
    TransferProductAdmin(
        models.TransferProduct,
        db.session,
        name=_l("??????????????????????"),
        category=_l("???????????????? ??????????????"),
    )
)
admin.add_view(
    ExpenseAdmin(
        models.Expense, db.session, name=_l("??????????????"), category=_l("???????????????? ????????????????")
    )
)
admin.add_view(
    DepositFundsAdmin(
        models.DepositFund,
        db.session,
        name=_l("????????????????"),
        category=_l("???????????????? ????????????????"),
    )
)
admin.add_view(
    CollectionFundsAdmin(
        models.CollectionFund,
        db.session,
        name=_l("??????????????????"),
        category=_l("???????????????? ????????????????"),
    )
)
admin.add_view(BaristaAdmin(models.Barista, db.session, name=_l("????????????????????")))
admin.add_view(
    CategoryAdmin(
        models.Category, db.session, name=_l("??????????????????"), category=_l("????????????")
    )
)
admin.add_view(
    RoleAdmin(models.Role, db.session, name=_l("????????????"), category=_l("????????????"))
)
admin.add_link(MenuLink(name=_l("??????????"), url="/index"))


@security.context_processor
def security_context_processor():
    return dict(
        admin_base_template=admin.base_template,
        admin_view=admin.index_view,
        h=admin_helpers,
    )


@babel.localeselector
def get_locale():
    return request.accept_languages.best_match(app.config["LANGUAGES"])


if not app.debug and not app.testing:
    if app.config["LOG_TO_STDOUT"]:
        stream_handler = logging.StreamHandler()
        stream_handler.setLevel(logging.INFO)
        app.logger.addHandler(stream_handler)
    else:
        if not os.path.exists("logs"):
            os.mkdir("logs")
        file_handler = RotatingFileHandler(
            "logs/not_detail_poster.log", maxBytes=10240, backupCount=10
        )
        file_handler.setFormatter(
            logging.Formatter(
                "%(asctime)s %(levelname)s: %(message)s " "[in %(pathname)s:%(lineno)d]"
            )
        )
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)

    app.logger.setLevel(logging.INFO)
    app.logger.info("Not Detail Poster: startup")
