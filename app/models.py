from datetime import datetime, date
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import func
from flask_security import UserMixin, RoleMixin
from app import db, login


@login.user_loader
def load_user(id):
    return Barista.query.get(int(id))


baristas = db.Table('baristas',
                    db.Column('barista_id', db.Integer, db.ForeignKey('barista.id'), primary_key=True),
                    db.Column('coffee_shop_id', db.Integer, db.ForeignKey('coffee_shop.id'), primary_key=True))


class CoffeeShop(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    place_name = db.Column(db.String(64), index=True, unique=True)
    address = db.Column(db.String(64), index=True, unique=True)
    cash = db.Column(db.Integer)
    cashless = db.Column(db.Integer)
    coffee_shop_equipments = db.relationship('CoffeeShopEquipment', backref='coffee_shop', lazy=True)
    warehouse = db.relationship('Warehouse', backref='coffee_shop', lazy=True)
    daily_reports = db.relationship('DailyReport', backref='coffee_shop', lazy=True)
    # baristas = db.relationship('Barista', backref='coffee_shop', lazy=True)
    baristas = db.relationship('Barista', secondary=baristas, lazy='subquery',
                               backref=db.backref('coffee_shop', lazy=True))
    expenses = db.relationship('Expense', backref='coffee_shop', lazy=True)
    supplies = db.relationship('Supply', backref='coffee_shop', lazy=True)
    by_weights = db.relationship('ByWeight', backref='coffee_shop', lazy=True)
    write_offs = db.relationship('WriteOff', backref='coffee_shop', lazy=True)

    def __repr__(self):
        return f'<CoffeeShop: {self.place_name}>'


class CoffeeShopEquipment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    coffee_machine = db.Column(db.String(64), index=True)
    grinder_1 = db.Column(db.String(64), index=True)
    grinder_2 = db.Column(db.String(64), index=True)
    coffee_shop_id = db.Column(db.Integer, db.ForeignKey('coffee_shop.id'))

    def __repr__(self):
        if self.coffee_shop_id:
            return f'<CoffeeShopEquipment: {self.coffee_shop.place_name}>'
        return  f'<CoffeeShopEquipment: {self.id}>'


class Warehouse(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    coffee_arabika = db.Column(db.Float(64))
    coffee_blend = db.Column(db.Float(64))
    milk = db.Column(db.Float(64))
    panini = db.Column(db.Integer)
    hot_dogs = db.Column(db.Integer)
    coffee_shop_id = db.Column(db.Integer, db.ForeignKey('coffee_shop.id'))

    def __repr__(self):
        if self.coffee_shop_id:
            return f'<Warehouse: {self.coffee_shop.place_name}>'
        else:
            return f'<Warehouse: {self.id}>'


roles = db.Table('roles',
                 db.Column('barista_id', db.Integer(), db.ForeignKey('barista.id')),
                 db.Column('role_id', db.Integer(), db.ForeignKey('role.id')))


class Barista(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), index=True, unique=True)
    phone_number = db.Column(db.String(120), unique=True)
    salary_rate = db.Column(db.Integer)
    coffee_shop_id = db.Column(db.Integer, db.ForeignKey('coffee_shop.id'))
    daily_reports = db.relationship('DailyReport', backref='barista', lazy=True)
    password_hash = db.Column(db.String(255))
    email = db.Column(db.String(255), unique=True)
    active = db.Column(db.Boolean())
    confirmed_at = db.Column(db.DateTime())
    roles = db.relationship('Role', secondary=roles, backref=db.backref('barista', lazy='dynamic'))

    def __repr__(self):
        return f'<Barista: {self.name}>'

    def check_phone_number(self, phone_number):
        return self.phone_number == phone_number

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Role(db.Model, RoleMixin):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(255))

    def __repr__(self):
        return f'<Role: {self.name}>'


expenses = db.Table('expenses',
                    db.Column('expense_id', db.Integer, db.ForeignKey('expense.id'), primary_key=True),
                    db.Column('daily_report_id', db.Integer, db.ForeignKey('daily_report.id'), primary_key=True))


class DailyReport(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    coffee_shop_id = db.Column(db.Integer, db.ForeignKey('coffee_shop.id'))
    barista_id = db.Column(db.Integer, db.ForeignKey('barista.id'))
    # Дата
    timestamp = db.Column(db.DateTime(timezone=True), server_default=func.now())
    # Касса - остаток дня в сумме с расходами
    cashbox = db.Column(db.Integer)
    # Расходы
    expenses = db.relationship('Expense', secondary=expenses, lazy='subquery',
                               backref=db.backref('daily_reports', lazy=True))
    # О.Д. - сумма нала и безнала за день
    remainder_of_day = db.Column(db.Integer)
    # Б.Н. безнал да день
    cashless = db.Column(db.Integer)
    # О.Н. остаток наличности за день
    cash_balance = db.Column(db.Integer)
    # Ф.О. остаток налички на коней дня
    actual_balance = db.Column(db.Integer)
    # потребление за день
    consumption_coffee_arabika = db.Column(db.Float(64))
    consumption_coffee_blend = db.Column(db.Float(64))
    consumption_milk = db.Column(db.Float(64))
    consumption_panini = db.Column(db.Integer)
    consumption_hot_dogs = db.Column(db.Integer)
    # остаток продукции в конце дня
    coffee_arabika = db.Column(db.Float(64))
    coffee_blend = db.Column(db.Float(64))
    milk = db.Column(db.Float(64))
    panini = db.Column(db.Integer)
    hot_dogs = db.Column(db.Integer)

    def __repr__(self):
        return f'<DailyReport {self.timestamp}>'


categories = db.Table(
    'categories',
    db.Column('category_id', db.Integer, db.ForeignKey('category.id'), primary_key=True),
    db.Column('expense_id', db.Integer, db.ForeignKey('expense.id'), primary_key=True)
)


class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80))

    def __repr__(self):
        return f'<Category: {self.name}>'


class Expense(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    is_global = db.Column(db.Boolean, default=False)
    # целевое назначение траты
    category = db.Column(db.String(64), index=True)
    # налл, безнал
    type_cost = db.Column(db.String(64), index=True)
    money = db.Column(db.Integer)
    # один ко многому одна Кофейня много расходов
    coffee_shop_id = db.Column(db.Integer, db.ForeignKey('coffee_shop.id'))
    categories = db.relationship('Category', secondary=categories, lazy='subquery',
                                 backref=db.backref('expense', lazy=True))

    def __repr__(self):
        return f'<Expense: {self.category}({self.type_cost}) - {self.money}>'


class Supply(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    coffee_shop_id = db.Column(db.Integer, db.ForeignKey('coffee_shop.id'))
    product_name = db.Column(db.String(80))
    amount = db.Column(db.Float(120))
    type_cost = db.Column(db.String(64), index=True)
    money = db.Column(db.Integer)


class ByWeight(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    coffee_shop_id = db.Column(db.Integer, db.ForeignKey('coffee_shop.id'))
    product_name = db.Column(db.String(80))
    amount = db.Column(db.Float(120))
    type_cost = db.Column(db.String(64), index=True)
    money = db.Column(db.Integer)


class WriteOff(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    coffee_shop_id = db.Column(db.Integer, db.ForeignKey('coffee_shop.id'))
    amount = db.Column(db.Float(120))
    product_name = db.Column(db.String(80))
