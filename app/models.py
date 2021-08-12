from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from . import db, login


@login.user_loader
def load_user(id):
    return Barista.query.get(int(id))


class CoffeeShop(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    place_name = db.Column(db.String(64), index=True, unique=True)
    address = db.Column(db.String(120), index=True, unique=True)
    cash = db.Column(db.Integer)
    cashless = db.Column(db.Integer)
    equipments = db.relationship('Equipments', backref='coffee_shop', lazy=True)
    warehouse = db.relationship('Warehouse', backref='coffee_shop', lazy=True)
    daily_reports = db.relationship('DailyReports', backref='coffee_shop', lazy=True)


class CoffeeShopEquipment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    coffee_machine = db.Column(db.String(64), index=True, unique=True)
    grinder_1 = db.Column(db.String(64), index=True, unique=True)
    grinder_2 = db.Column(db.String(64), index=True, unique=True)
    coffee_shop_id = db.Column(db.Integer, db.ForeignKey('coffee_shop.id'))


class Warehouse(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    coffee_arabika = db.Column(db.Integer)
    coffee_blend = db.Column(db.Integer)
    milk = db.Column(db.Integer)
    panini = db.Column(db.Integer)
    hot_dogs = db.Column(db.Integer)
    coffee_shop_id = db.Column(db.Integer, db.ForeignKey('coffee_shop.id'))


class Barista(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), index=True, unique=True)
    phone_number = db.Column(db.String(120), unique=True)
    salary_rate = db.Column(db.Integer)
    password_hash = db.Column(db.String(128))
    # permissions
    daily_reports = db.relationship('DailyReports', backref='barista', lazy=True)

    def __repr__(self):
        return f'<Barista: {self.name}>'

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


expenses = db.Table('expenses',
    db.Column('expense_id', db.Integer, db.ForeignKey('expense.id'), primary_key=True),
    db.Column('daily_report_id', db.Integer, db.ForeignKey('daily_report.id'), primary_key=True)
)


class DailyReport(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    coffee_shop_id = db.Column(db.Integer, db.ForeignKey('coffee_shop.id'))
    barista_id = db.Column(db.Integer, db.ForeignKey('barista.id'))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    cashbox = db.Column(db.Integer)
    cash_balance = db.Column(db.Integer)
    cashless = db.Column(db.Integer)
    remainder_of_day = db.Column(db.Integer)
    expenses = db.relationship('Expense', secondary=expenses, lazy='subquery',
                               backref=db.backref('daily_reports', lazy=True))

    def __repr__(self):
        return f'<DailyReport: {self.timestamp}>'


class Expense(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    category = db.Column(db.String(64), index=True, unique=True) # целевое назначение траты
    type_cost = db.Column(db.String(64), index=True, unique=True) # налл, безнал
    money = db.Column(db.Integer)

    def __repr__(self):
        return f'<Expense: {self.category}({self.type_cost}) - {self.money}>'

