import click
from datetime import datetime
from werkzeug.security import generate_password_hash
from app import app, db, user_datastore
from app.models import (
    Role,
    Barista,
    Report,
    Shop,
    ShopEquipment,
    Storage
    Expense,
    Supply,
    ByWeight,
    WriteOff,
    Category
)


@app.shell_context_processor
def make_shell_context():
    return {
        'db': db,
        'Barista': Barista,
        'Report': Report,
        'Role': Role,
        'Shop': Shop,
        'ShopEquipment': ShopEquipment,
        'Storage': Storage,
        'Expense': Expense,
        'Category': Category,
        'Supply': Supply,
        'WriteOff': WriteOff,
    }


def create_roles():
    db.create_all()
    user_datastore.create_role(name='admin', description='all permissions')
    user_datastore.create_role(name='moderator', description='moderator permissions')
    user_datastore.create_role(name='user', description='user permissions')
    db.session.commit()
    print('Create roles: user, moderator, admin')

@app.cli.command('create-categories')
def create_categories():
    db.create_all()
    categories_names = ('Зарплата', 'Аренда', 'Запупка', 'Вода')
    for name in categories_names:
        category = Category(name=name)
        db.session.add(category)
    db.session.commit()
    print(f'Create categories:  {categories_names}')

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
    user.confirmed_at = datetime.utcnow()
    role = Role.query.filter_by(name='admin').first()
    user_datastore.activate_user(user)
    user_datastore.add_role_to_user(user, role)
    db.session.commit()
    print(f'Create superuser with name: {name}')

