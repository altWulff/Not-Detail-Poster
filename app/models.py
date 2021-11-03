from datetime import datetime, date
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import func
from flask_security import UserMixin, RoleMixin
from app import db, login


date_today = datetime(datetime.today().year, datetime.today().month, datetime.today().day)

@login.user_loader
def load_user(user_id):
    return Barista.query.get(int(user_id))


baristas = db.Table(
    'baristas',
    db.Column('barista_id', db.Integer, db.ForeignKey('barista.id'), primary_key=True),
    db.Column('shop_id', db.Integer, db.ForeignKey('shop.id'), primary_key=True)
)


class Shop(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    place_name = db.Column(db.String(64), index=True, unique=True)
    address = db.Column(db.String(64), index=True, unique=True)
    cash = db.Column(db.Integer)
    cashless = db.Column(db.Integer)
    storage = db.relationship('Storage', backref='shop', lazy=True)
    shop_equipments = db.relationship('ShopEquipment', backref='shop', lazy=True)
    reports = db.relationship('Report', backref='shop', lazy=True)
    baristas = db.relationship('Barista', secondary=baristas, lazy='subquery',
                               backref=db.backref('shop', lazy=True))
    expenses = db.relationship('Expense', backref='shop', lazy=True)

    def __repr__(self):
        return f'<Shop: {self.place_name}>'

    def __str__(self):
        return f'{self.place_name} / {self.address}'


class ShopEquipment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    coffee_machine = db.Column(db.String(64), index=True)
    grinder_1 = db.Column(db.String(64), index=True)
    grinder_2 = db.Column(db.String(64), index=True)
    shop_id = db.Column(db.Integer, db.ForeignKey('shop.id'))

    def __repr__(self):
        if self.shop_id:
            return f'<ShopEquipment: {self.shop.place_name}>'
        return f'<ShopEquipment: {self.id}>'


class Storage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    coffee_arabika = db.Column(db.Float(50))
    coffee_blend = db.Column(db.Float(50))
    milk = db.Column(db.Float(50))
    panini = db.Column(db.Integer)
    hot_dogs = db.Column(db.Integer)
    supplies = db.relationship('Supply', backref='storage', lazy=True)
    by_weights = db.relationship('ByWeight', backref='storage', lazy=True)
    write_offs = db.relationship('WriteOff', backref='storage', lazy=True)
    shop_id = db.Column(db.Integer, db.ForeignKey('shop.id'))

    def __repr__(self):
        if self.shop_id:
            return f'<Storage: {self.shop.place_name}>'
        else:
            return f'<Storage: {self.id}>'

    def __str__(self):
        return f'{self.shop.place_name} / {self.shop.address}'


roles = db.Table(
    'roles',
    db.Column('barista_id', db.Integer(), db.ForeignKey('barista.id')),
    db.Column('role_id', db.Integer(), db.ForeignKey('role.id'))
)


class Barista(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), index=True, unique=True)
    phone_number = db.Column(db.String(120), unique=True)
    salary_rate = db.Column(db.Integer)
    shop_id = db.Column(db.Integer, db.ForeignKey('shop.id'))
    reports = db.relationship('Report', backref='barista', lazy=True)
    password_hash = db.Column(db.String(255))
    email = db.Column(db.String(255), unique=True)
    active = db.Column(db.Boolean())
    confirmed_at = db.Column(db.DateTime())
    roles = db.relationship('Role', secondary=roles, backref=db.backref('barista', lazy='dynamic'))

    def __repr__(self):
        return f'<Barista: {self.name}>'

    def __str__(self):
        return f'{self.name}'

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


expenses = db.Table(
    'expenses',
    db.Column('expense_id', db.Integer, db.ForeignKey('expense.id'), primary_key=True),
    db.Column('report_id', db.Integer, db.ForeignKey('report.id'), primary_key=True)
)


class Report(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    shop_id = db.Column(db.Integer, db.ForeignKey('shop.id'))
    barista_id = db.Column(db.Integer, db.ForeignKey('barista.id'))
    # Дата
    timestamp = db.Column(db.DateTime(timezone=True), server_default=func.now())
    # Касса - остаток дня в сумме с расходами
    cashbox = db.Column(db.Integer)
    # Расходы
    expenses = db.relationship('Expense', secondary=expenses, lazy='subquery',
                               backref=db.backref('reports', lazy=True))
    # О.Д. - сумма нала и безнала за день
    remainder_of_day = db.Column(db.Integer)
    # Б.Н. безнал да день
    cashless = db.Column(db.Integer)
    # О.Н. остаток наличности за день
    cash_balance = db.Column(db.Integer)
    # Ф.О. остаток налички на коней дня
    actual_balance = db.Column(db.Integer)
    # потребление за день
    consumption_coffee_arabika = db.Column(db.Float(50))
    consumption_coffee_blend = db.Column(db.Float(50))
    consumption_milk = db.Column(db.Float(50))
    consumption_panini = db.Column(db.Integer)
    consumption_hot_dogs = db.Column(db.Integer)
    # остаток продукции в конце дня
    coffee_arabika = db.Column(db.Float(50))
    coffee_blend = db.Column(db.Float(50))
    milk = db.Column(db.Float(50))
    panini = db.Column(db.Integer)
    hot_dogs = db.Column(db.Integer)

    def __repr__(self):
        return f'<Report {self.timestamp}>'


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
        
    def __str__(self):
        return self.name


class Expense(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    is_global = db.Column(db.Boolean, default=False)
    # налл, безнал
    type_cost = db.Column(db.String(64), index=True)
    money = db.Column(db.Integer)
    # один ко многому одна Кофейня много расходов
    shop_id = db.Column(db.Integer, db.ForeignKey('shop.id'))
    categories = db.relationship('Category', secondary=categories, lazy='subquery',
                                 backref=db.backref('expense', lazy=True))

    def __repr__(self):
        return f'<Expense: {self.categories}({self.type_cost}) - {self.money}>'

    @classmethod     
    def get_global(cls, shop_id, today=False):
        _query = cls.query.filter_by(shop_id=shop_id).filter(cls.is_global)
        if today:
            _query = _query.filter(cls.timestamp >= date_today)
        return _query
    
    @classmethod
    def get_local(cls, shop_id, today=False):
        _query =cls.query.filter_by(shop_id=shop_id).filter(cls.is_global==False)
        if today:
            _query = _query.filter(cls.timestamp >= date_today)
        return _query
    


class Supply(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    storage_id = db.Column(db.Integer, db.ForeignKey('storage.id'))
    product_name = db.Column(db.String(80))
    amount = db.Column(db.Float(50))
    type_cost = db.Column(db.String(64), index=True)
    money = db.Column(db.Integer)


class ByWeight(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    storage_id = db.Column(db.Integer, db.ForeignKey('storage.id'))
    product_name = db.Column(db.String(80))
    amount = db.Column(db.Float(50))
    type_cost = db.Column(db.String(64), index=True)
    money = db.Column(db.Integer)


class WriteOff(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    storage_id = db.Column(db.Integer, db.ForeignKey('storage.id'))
    amount = db.Column(db.Float(50))
    product_name = db.Column(db.String(80))
