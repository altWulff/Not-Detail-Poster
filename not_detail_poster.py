import click
from werkzeug.security import generate_password_hash
from app import app, db, user_datastore
from app.models import Barista, DailyReport, Role


@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'Barista': Barista, 'DailyReport': DailyReport}


@app.cli.command("createsuperuser")
@click.argument("username")
@click.argument("password")
def create_superuser(username, password):
    db.create_all()
    name = username
    password = generate_password_hash(password)
    user_datastore.create_user(name=name, password_hash=password)
    
    user = Barista.query.filter_by(name=name).first()
    role = Role.query.filter_by(name='admin').first()
    #user_datastore.create_role(name='admin', description='all permissions')
    user_datastore.activate_user(user)
    user_datastore.add_role_to_user(user, role)
    db.session.commit()
    print (f'Create superuser with name: {name}'
    