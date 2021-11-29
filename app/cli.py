import os
import click
from datetime import datetime
from werkzeug.security import generate_password_hash
from app import app, db, user_datastore
from app.models import Role, Barista, Category


@app.cli.group()
def create():
    """Create user, roles, and categories commands."""
    pass


@create.command()
def roles():
    """
    Create role to permissions,
    create before superuser
    """
    db.create_all()
    user_datastore.create_role(name='admin', description='all permissions')
    user_datastore.create_role(name='moderator', description='moderator permissions')
    user_datastore.create_role(name='user', description='user permissions')
    db.session.commit()
    click.echo("Create roles: user, moderator, admin.")


@create.command()
def categories():
    """
    Create base categories
    """
    db.create_all()
    categories_names = ('Зарплата', 'Аренда помещения', 'Аренда оборудования', 'Запупка', 'Вода')
    for name in categories_names:
        is_exist = Category.query.filter_by(name=name).first()
        if is_exist:
            category = Category(name=name)
            db.session.add(category)
    db.session.commit()
    click.echo(f'Create categories:  {categories_names}')


@create.command()
@click.argument("username")
@click.argument("password")
def superuser(username, password):
    """
    Create Super User
    :param username: Superuser name
    :param password: Any words
    """
    db.create_all()
    name = username
    password = generate_password_hash(password)
    user_datastore.create_user(name=name, password_hash=password)
    user = Barista.query.filter_by(name=name).first()
    user.confirmed_at = datetime.now()
    role = Role.query.filter_by(name='admin').first()
    user_datastore.activate_user(user)
    user_datastore.add_role_to_user(user, role)
    db.session.commit()
    click.echo(f'Create superuser with name: {name}')


@app.cli.group()
def translate():
    """Translation and localization commands."""
    pass


@translate.command()
def update():
    """Update all languages."""
    if os.system('pybabel extract -F babel.cfg -k _l -o messages.pot .'):
        raise RuntimeError('extract command failed')
    if os.system('pybabel update -i messages.pot -d app/translations'):
        raise RuntimeError('update command failed')
    os.remove('messages.pot')


@translate.command()
def compile():
    """Compile all languages."""
    if os.system('pybabel compile -d app/translations'):
        raise RuntimeError('compile command failed')


@translate.command()
@click.argument('lang')
def init(lang):
    """Initialize a new language."""
    if os.system('pybabel extract -F babel.cfg -k _l -o messages.pot .'):
        raise RuntimeError('extract command failed')
    if os.system(
            'pybabel init -i messages.pot -d app/translations -l ' + lang):
        raise RuntimeError('init command failed')
    os.remove('messages.pot')
