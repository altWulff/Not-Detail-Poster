import click
from werkzeug.security import generate_password_hash
from app import app, db, user_datastore
from app.models import Barista, DailyReport, Role, CoffeeShop, CoffeeShopEquipment, Expense


@app.shell_context_processor
def make_shell_context():
    return {
        'db': db,
        'Barista': Barista,
        'DailyReport': DailyReport,
        'Role': Role,
        'CoffeeShop': CoffeeShop,
        'CoffeeShopEquipment': CoffeeShopEquipment,
        'Expense': Expense
    }


def create_roles():
    db.create_all()
    user_datastore.create_role(name='admin', description='all permissions')
    user_datastore.create_role(name='moderator', description='moderator permissions')
    user_datastore.create_role(name='user', description='user permissions')
    db.session.commit()
    print('Create roles: user, moderator, admin')


@app.cli.command("createsuperuser")
@click.argument("username")
@click.argument("password")
def create_superuser(username, password):
    db.create_all()
    name = username
    password = generate_password_hash(password)
    user_datastore.create_user(name=name, password_hash=password)
    create_roles()
    user = Barista.query.filter_by(name=name).first()
    role = Role.query.filter_by(name='admin').first()
    user_datastore.activate_user(user)
    user_datastore.add_role_to_user(user, role)
    db.session.commit()
    print(f'Create superuser with name: {name}')

