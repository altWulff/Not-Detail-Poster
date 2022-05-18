"""
Module contains error templates
"""


from flask import Blueprint, render_template

from app import db

errors = Blueprint("errors", __name__, url_prefix="/error")


@errors.errorhandler(404)
def not_found_error(error):
    """Not Found Error"""
    return render_template("errors/404.html", error=error), 404


@errors.errorhandler(500)
def internal_error(error):
    """Internal error"""
    db.session.rollback()
    return render_template("errors/500.html", error=error), 500
