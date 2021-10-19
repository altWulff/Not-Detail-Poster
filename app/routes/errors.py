from . import render_template, Blueprint
from . import db


errors = Blueprint('errors', __name__, url_prefix='/error')


@errors.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404


@errors.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('errors/500.html'), 500