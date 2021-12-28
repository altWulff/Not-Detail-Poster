from datetime import datetime, date
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import func
from sqlalchemy.ext.hybrid import hybrid_property
from flask_security import UserMixin, RoleMixin
from flask_admin.babel import gettext
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
    __tablename__ = 'shop'
    id = db.Column(db.Integer, primary_key=True)
    place_name = db.Column(db.String(64), index=True, unique=True)
    address = db.Column(db.String(64), index=True, unique=True)
    timestamp = db.Column(db.DateTime(timezone=True), server_default=func.now())
    cash = db.Column(db.Integer)
    cashless = db.Column(db.Integer)
    storage = db.relationship(
        "Storage",
        back_populates="shop",
        uselist=False,
        cascade="all, delete-orphan",
        single_parent=True
    )
    shop_equipment = db.relationship(
        "ShopEquipment",
        back_populates="shop",
        uselist=False,
        cascade="all, delete-orphan",
        single_parent=True
    )
    reports = db.relationship('Report', backref='shop', lazy=True)
    baristas = db.relationship(
        'Barista',
        secondary=baristas, lazy='subquery',
        backref=db.backref('shop', lazy=True)
    )
    expenses = db.relationship('Expense', backref='shop', lazy=True)
    collection_funds = db.relationship('CollectionFund', backref='shop', lazy=True)
    deposit_funds = db.relationship('DepositFund', backref='shop', lazy=True)

    def __repr__(self):
        return f'<Shop: {self.place_name}>'

    def __str__(self):
        if self:
            return f'{self.place_name} / {self.address}'
        return f'{self}'
        
    @classmethod
    def get_barista_work(cls, barista):
        if barista.has_administrative_rights:
            _query = cls.query
        else:
            _query = cls.query.filter(cls.baristas.any(id=barista.id))
        _query = _query.order_by('place_name')
        return _query


class ShopEquipment(db.Model):
    __tablename__ = 'shop_equipment'
    id = db.Column(db.Integer, primary_key=True)
    shop_id = db.Column(db.Integer, db.ForeignKey('shop.id'))
    shop = db.relationship("Shop", back_populates="shop_equipment")
    coffee_machine = db.Column(db.String(64), index=True)
    last_cleaning_coffee_machine = db.Column(db.DateTime(timezone=True), server_default=func.now())
    grinder_1 = db.Column(db.String(64), index=True)
    grinder_2 = db.Column(db.String(64), index=True)
    last_cleaning_grinder = db.Column(db.DateTime(timezone=True), server_default=func.now())

    def __repr__(self):
        if self.shop_id:
            return f'<ShopEquipment: {self.shop.place_name}>'
        return f'<ShopEquipment_id: {self.id}>'

    def __str__(self):
        if self.shop:
            return gettext(f'Оборудование: {self.shop.address}')
        return gettext(f'Оборудование: id-{self.id}')


class Storage(db.Model):
    __tablename__ = 'storage'
    id = db.Column(db.Integer, primary_key=True)
    shop_id = db.Column(db.Integer, db.ForeignKey('shop.id'))
    shop = db.relationship("Shop", back_populates="storage")
    coffee_arabika = db.Column(db.Float(50))
    coffee_blend = db.Column(db.Float(50))
    milk = db.Column(db.Float(50))
    panini = db.Column(db.Integer)
    sausages = db.Column(db.Integer)
    buns = db.Column(db.Integer)
    supplies = db.relationship('Supply', backref='storage', lazy=True)
    by_weights = db.relationship('ByWeight', backref='storage', lazy=True)
    write_offs = db.relationship('WriteOff', backref='storage', lazy=True)

    def __repr__(self):
        if self.shop_id:
            return f'<Storage: {self.shop.address}>'
        else:
            return f'<Storage_id: {self.id}>'

    def __str__(self):
        if self.shop:
            return f'{self.shop.address}'
        return gettext(f'Склад: id-{self.id}')


roles = db.Table(
    'roles',
    db.Column('barista_id', db.Integer(), db.ForeignKey('barista.id')),
    db.Column('role_id', db.Integer(), db.ForeignKey('role.id'))
)


class Barista(db.Model, UserMixin):
    __tablename__ = 'barista'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), index=True, unique=True)
    phone_number = db.Column(db.String(120), unique=True)
    shop_id = db.Column(db.Integer, db.ForeignKey('shop.id'))
    reports = db.relationship('Report', backref='barista', lazy=True)
    expenses = db.relationship('Expense', backref='barista', lazy=True)
    collection_funds = db.relationship('CollectionFund', backref='barista', lazy=True)
    deposit_funds = db.relationship('DepositFund', backref='barista', lazy=True)
    transfer_products = db.relationship('TransferProduct', backref='barista', lazy=True)
    supplies = db.relationship('Supply', backref='barista', lazy=True)
    by_weights = db.relationship('ByWeight', backref='barista', lazy=True)
    write_offs = db.relationship('WriteOff', backref='barista', lazy=True)
    password_hash = db.Column(db.String(255))
    email = db.Column(db.String(255), unique=True)
    active = db.Column(db.Boolean())
    confirmed_at = db.Column(db.DateTime())
    roles = db.relationship('Role', secondary=roles, backref=db.backref('barista', lazy='dynamic'))

    def __repr__(self):
        return f'<Barista: {self.name}>'

    def __str__(self):
        return f'{self.name}'

    @hybrid_property
    def password(self):
        return self.password_hash

    @password.setter
    def password(self, new_pass):
        _password_hash = generate_password_hash(new_pass)
        self.password_hash = _password_hash

    @hybrid_property 
    def has_administrative_rights(self):
        return self.has_role('admin')
    
    @hybrid_property 
    def has_moderator_rights(self):
        return self.has_role('moderator')

    @hybrid_property
    def storage(self):
        shop_ids = [shop.id for shop in self.shop]
        storage_query = Storage.query.filter_by
        storage_list = [storage_query(shop_id=id).first() for id in shop_ids]
        return storage_list

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def check_phone_number(self, phone_number):
        return self.phone_number == phone_number


class Role(db.Model, RoleMixin):
    __tablename__ = 'role'
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(255))

    def __repr__(self):
        return f'<Role: {self.name}>'

    def __str__(self):
        return gettext(self.name.title())


expenses = db.Table(
    'expenses',
    db.Column('expense_id', db.Integer, db.ForeignKey('expense.id'), primary_key=True),
    db.Column('report_id', db.Integer, db.ForeignKey('report.id'), primary_key=True)
)

collection_funds = db.Table(
    'collection_funds',
    db.Column('collection_fund_id', db.Integer, db.ForeignKey('collection_fund.id'), primary_key=True),
    db.Column('shop_id', db.Integer, db.ForeignKey('shop.id'), primary_key=True)
)

deposit_funds = db.Table(
    'deposit_funds',
    db.Column('deposit_fund_id', db.Integer, db.ForeignKey('deposit_fund.id'), primary_key=True),
    db.Column('shop_id', db.Integer, db.ForeignKey('shop.id'), primary_key=True)
)


class Report(db.Model):
    __tablename__ = 'report'
    id = db.Column(db.Integer, primary_key=True)
    shop_id = db.Column(db.Integer, db.ForeignKey('shop.id'))
    barista_id = db.Column(db.Integer, db.ForeignKey('barista.id'))
    backdating = db.Column(db.Boolean, default=False)
    # Дата
    timestamp = db.Column(db.DateTime(timezone=True), server_default=func.now())
    last_edit = db.Column(db.DateTime(timezone=True), server_default=func.now())
    # Касса - остаток дня в сумме с расходами
    cashbox = db.Column(db.Integer)
    # Расходы
    expenses = db.relationship(
        'Expense',
        secondary=expenses,
        lazy='subquery',
        backref=db.backref('reports', lazy=True),
        cascade="all, delete-orphan",
        single_parent=True
    )
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
    consumption_sausages = db.Column(db.Integer)
    consumption_buns = db.Column(db.Integer)
    # остаток продукции в конце дня
    coffee_arabika = db.Column(db.Float(50))
    coffee_blend = db.Column(db.Float(50))
    milk = db.Column(db.Float(50))
    panini = db.Column(db.Integer)
    sausages = db.Column(db.Integer)
    buns = db.Column(db.Integer)

    def __repr__(self):
        return f'<Report: {self.timestamp}>'

    def __str__(self):
        if self.shop:
            return f'{self.shop.address} / {self.timestamp.strftime("%d.%m.%y")}г.'
        else:
            return f'{self.timestamp.strftime("%d.%m.%y")}г.'
            


categories = db.Table(
    'categories',
    db.Column('category_id', db.Integer, db.ForeignKey('category.id'), primary_key=True),
    db.Column('expense_id', db.Integer, db.ForeignKey('expense.id'), primary_key=True)
)


class Category(db.Model):
    __tablename__ = 'category'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80))

    def __repr__(self):
        return f'<Category: {self.name}>'

    def __str__(self):
        return gettext(self.name.title())


class Expense(db.Model):
    __tablename__ = 'expense'
    id = db.Column(db.Integer, primary_key=True)
    barista_id = db.Column(db.Integer, db.ForeignKey('barista.id'))
    shop_id = db.Column(db.Integer, db.ForeignKey('shop.id'))
    backdating = db.Column(db.Boolean, default=False)
    timestamp = db.Column(db.DateTime(timezone=True), server_default=func.now())
    last_edit = db.Column(db.DateTime(timezone=True), server_default=func.now())
    is_global = db.Column(db.Boolean, default=False)
    # налл, безнал
    type_cost = db.Column(db.String(64), index=True)
    money = db.Column(db.Integer)
    categories = db.relationship(
        'Category',
        secondary=categories,
        lazy='subquery',
        backref=db.backref('expense', lazy=True)
    )

    def __repr__(self):
        return f'<Expense: {self.money} {self.timestamp.strftime("%d.%m.%y")}г.>'
     
    def __str__(self):
        if self.type_cost == 'cash':
            return f'{self.money} грн. / {self.shop.address} / {self.timestamp.strftime("%d.%m.%y")}г.'
        else:
            return f'{self.money} грн.(Безнал) / {self.shop.address} / {self.timestamp.strftime("%d.%m.%y")}г.'

    @classmethod     
    def get_global(cls, shop_id, today=False):
        _query = cls.query.filter_by(shop_id=shop_id).filter(cls.is_global)
        if today:
            _query = _query.filter(cls.timestamp >= date_today)
        return _query
    
    @classmethod
    def get_local(cls, shop_id, today=False):
        _query = cls.query.filter_by(shop_id=shop_id).filter(cls.is_global==False)
        if today:
            _query = _query.filter(cls.timestamp >= date_today)
        return _query
        
    @classmethod
    def by_timestamp(cls, shop_id, timestamp):
        _query = cls.query.filter_by(shop_id=shop_id).filter(cls.is_global==False)
        _query = _query.filter(func.date(cls.timestamp) == date.today()).all()
        return _query
    

class Supply(db.Model):
    __tablename__ = 'supply'
    id = db.Column(db.Integer, primary_key=True)
    barista_id = db.Column(db.Integer, db.ForeignKey('barista.id'))
    storage_id = db.Column(db.Integer, db.ForeignKey('storage.id'))
    backdating = db.Column(db.Boolean, default=False)
    timestamp = db.Column(db.DateTime(timezone=True), server_default=func.now())
    last_edit = db.Column(db.DateTime(timezone=True), server_default=func.now())
    product_name = db.Column(db.String(80))
    amount = db.Column(db.Float(50))
    type_cost = db.Column(db.String(64), index=True)
    money = db.Column(db.Integer)
    
    @classmethod
    def get_local(cls, storage_id, today=True):
        _query = cls.query.filter_by(storage_id=storage_id)
        if today:
            _query = _query.filter(cls.timestamp >= date_today)
        return _query
        
    @classmethod
    def get_local_by_shop(cls, shop_id):
        storage = Storage.query.filter_by(shop_id=shop_id).first_or_404()
        _query = cls.query.filter_by(storage_id=storage.id).filter(cls.timestamp >= date_today)
        return _query

    def __repr__(self):
        return f'<Supply: {self.id} / {self.timestamp.strftime("%d.%m.%y")}'

    def __str__(self):
        if self.type_cost == 'cash':
            return f'{self.money} грн. / {self.storage.shop.address} / {self.timestamp.strftime("%d.%m.%y")}г.'
        else:
            return f'{self.money} грн.(Безнал) / {self.storage.shop.address} / {self.timestamp.strftime("%d.%m.%y")}г.'


class ByWeight(db.Model):
    __tablename__ = 'by_weight'
    id = db.Column(db.Integer, primary_key=True)
    barista_id = db.Column(db.Integer, db.ForeignKey('barista.id'))
    storage_id = db.Column(db.Integer, db.ForeignKey('storage.id'))
    backdating = db.Column(db.Boolean, default=False)
    timestamp = db.Column(db.DateTime(timezone=True), server_default=func.now())
    last_edit = db.Column(db.DateTime(timezone=True), server_default=func.now())
    product_name = db.Column(db.String(80))
    amount = db.Column(db.Float(50))
    type_cost = db.Column(db.String(64), index=True)
    money = db.Column(db.Integer)
    
    @classmethod
    def get_local(cls, storage_id, today=True):
        _query = cls.query.filter_by(storage_id=storage_id)
        if today:
            _query = _query.filter(cls.timestamp >= date_today)
        return _query
    
    @classmethod
    def get_local_by_shop(cls, shop_id):
        storage = Storage.query.filter_by(shop_id=shop_id).first_or_404()
        _query = cls.query.filter_by(storage_id=storage.id).filter(cls.timestamp >= date_today)
        return _query

    def __repr__(self):
        return f'{self.money} / {self.timestamp.strftime("%d.%m.%y")}г.'

    def __str__(self):
        if self.type_cost == 'cash':
            return f'{self.money} грн. / {self.storage.shop.address} / {self.timestamp.strftime("%d.%m.%y")}г.'
        else:
            return f'{self.money} грн.(Безнал) / {self.storage.shop.address} / {self.timestamp.strftime("%d.%m.%y")}г.'


class WriteOff(db.Model):
    __tablename__ = 'write_off'
    id = db.Column(db.Integer, primary_key=True)
    barista_id = db.Column(db.Integer, db.ForeignKey('barista.id'))
    storage_id = db.Column(db.Integer, db.ForeignKey('storage.id'))
    backdating = db.Column(db.Boolean, default=False)
    timestamp = db.Column(db.DateTime(timezone=True), server_default=func.now())
    last_edit = db.Column(db.DateTime(timezone=True), server_default=func.now())
    amount = db.Column(db.Float(50))
    product_name = db.Column(db.String(80))

    def __repr__(self):
        return f'{self.product_name} / {self.timestamp.strftime("%d.%m.%y")}г.'

    def __str__(self):
        return f'{self.product_name} / {self.storage.shop.address} / {self.timestamp.strftime("%d.%m.%y")}г.'

    @classmethod
    def get_local_by_shop(cls, shop_id):
        storage = Storage.query.filter_by(shop_id=shop_id).first_or_404()
        _query = cls.query.filter_by(storage_id=storage.id).filter(cls.timestamp >= date_today)
        return _query


class DepositFund(db.Model):
    __tablename__ = 'deposit_fund'
    id = db.Column(db.Integer, primary_key=True)
    barista_id = db.Column(db.Integer, db.ForeignKey('barista.id'))
    shop_id = db.Column(db.Integer, db.ForeignKey('shop.id'))
    backdating = db.Column(db.Boolean, default=False)
    timestamp = db.Column(db.DateTime(timezone=True), server_default=func.now())
    last_edit = db.Column(db.DateTime(timezone=True), server_default=func.now())
    type_cost = db.Column(db.String(64), index=True)
    money = db.Column(db.Integer)

    @classmethod
    def get_local_by_shop(cls, shop_id, today=True):
        _query = cls.query.filter_by(shop_id=shop_id)
        if today:
            _query = _query.filter(cls.timestamp >= date_today)
        return _query


class CollectionFund(db.Model):
    __tablename__ = 'collection_fund'
    id = db.Column(db.Integer, primary_key=True)
    barista_id = db.Column(db.Integer, db.ForeignKey('barista.id'))
    shop_id = db.Column(db.Integer, db.ForeignKey('shop.id'))
    backdating = db.Column(db.Boolean, default=False)
    timestamp = db.Column(db.DateTime(timezone=True), server_default=func.now())
    last_edit = db.Column(db.DateTime(timezone=True), server_default=func.now())
    type_cost = db.Column(db.String(64), index=True)
    money = db.Column(db.Integer)

    @classmethod
    def get_local_by_shop(cls, shop_id, today=True):
        _query = cls.query.filter_by(shop_id=shop_id)
        if today:
            _query = _query.filter(cls.timestamp >= date_today)
        return _query


class TransferProduct(db.Model):
    __tablename__ = 'transfer_product'
    id = db.Column(db.Integer, primary_key=True)
    barista_id = db.Column(db.Integer, db.ForeignKey('barista.id'))
    where_shop = db.Column(db.String(64), index=True)
    to_shop = db.Column(db.String(64), index=True)
    backdating = db.Column(db.Boolean, default=False)
    timestamp = db.Column(db.DateTime(timezone=True), server_default=func.now())
    last_edit = db.Column(db.DateTime(timezone=True), server_default=func.now())
    product_name = db.Column(db.String(80))
    amount = db.Column(db.Float(50))

    @classmethod
    def get_shop(cls, shop_id, today=True):
        _query = Shop.query.filter_by(id=shop_id)
        if today:
            _query = _query.filter(cls.timestamp >= date_today)
        return _query
