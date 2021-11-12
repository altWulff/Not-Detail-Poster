from datetime import datetime, date
from sqlalchemy import func
from flask import flash, redirect, url_for
from app.models import Shop, Report, Expense, Storage, Category, WriteOff, Supply, ByWeight
from app import app, db

date_today = datetime(datetime.today().year, datetime.today().month, datetime.today().day)


def transaction_count(shop_id: int) -> int:
    reports = Report.query.filter_by(shop_id=shop_id)
    reports_today = reports.filter(func.date(Report.timestamp) == date.today()).all()
    return len(reports_today)

def is_report_send(shop_id: int) -> bool:
    return transaction_count(shop_id) >= app.config['REPORTS_PER_DAY']


class TransactionHandler:
    COMMIT_MESSAGE = 'Транзакция принята!'
    NON_VALID_MESSAGE = 'Транзакция не принята!  Попробуйте заново, с коректными значениями.'
    LIMIT_MESSAGE = 'Сегодняшний отчет уже был отправлен!'
    
    def __init__(self, shop_id=None):
        self.shop = self.get_shop_from_id(shop_id)
        self.storage = self.get_storage_from_id(shop_id)

    def get_shop_from_id(self, shop_id):
        query = Shop.query.filter_by(id=shop_id).first_or_404()
        return query
    
    def get_storage_from_id(self, shop_id):
        query = Storage.query.filter_by(shop_id=shop_id).first_or_404()
        return query

    def validate_report_limit(self):
        if is_report_send(self.shop.id):
            flash(self.LIMIT_MESSAGE)
            return redirect(url_for('home'))
            
    def add_money(self, money, type_cost):
        if type_cost == 'cash':
            self.shop.cash -= money
        else:
            self.shop.cashless -= money

    def write_to_db(self, record):
        db.session.add(record)
        db.session.commit()
        
    def create_expense(self, form):
        self.validate_report_limit()
        expense = Expense(
            type_cost=form.type_cost.data,
            money=form.money.data,
            is_global=form.is_global.data,
            timestamp = datetime.now()
        )
        self.add_money(form.money.data, form.type_cost.data)
        for c_id in form.categories.data:
            category = Category.query.filter_by(id=c_id).first_or_404()
            expense.categories.append(category)
        self.shop.expenses.append(expense)
        self.write_to_db(expense)
    
    def crete_by_weight(self, form):
        self.validate_report_limit()
        if form.by_weight_choice.data == 'blend':
            self.storage.coffee_blend -= form.amount.data
        else:
            self.storage.coffee_arabika -= form.amount.data

        self.add_money(form.money.data, form.type_cost.data)
        by_weight = ByWeight(
            storage=self.storage,
            amount=form.amount.data,
            product_name=form.by_weight_choice.data,
            type_cost=form.cash_type.data, 
            money=form.money.data,
            timestamp = datetime.now()
        )
        self.write_to_db(by_weight)
        
    def create_write_off(self, form):
        self.validate_report_limit()
        if form.write_off_choice.data == 'blend':
            self.storage.coffee_blend -= form.amount.data
        elif form.write_off_choice.data == 'arabica':
            self.storage.coffee_arabika -= form.amount.data
        elif form.write_off_choice.data == 'milk':
            self.storage.milk -= form.amount.data
        elif form.write_off_choice.data == 'panini':
            self.storage.panini -= int(form.amount.data)
        else:
            self.storage.hot_dogs -= int(form.amount.data)
        write_off = WriteOff(
            storage=self.storage, 
            amount=form.amount.data, 
            product_name=form.write_off_choice.data,
            timestamp = datetime.now()
        )
        self.write_to_db(write_off)
    
    def create_supply(self, form):
        self.validate_report_limit()
        if form.supply_choice.data == 'blend':
            self.storage.coffee_blend += form.amount.data
        elif form.supply_choice.data == 'arabica':
            self.storage.coffee_arabika += form.amount.data
        elif form.supply_choice.data == 'milk':
            self.storage.milk += form.amount.data
        elif form.supply_choice.data == 'panini':
            self.storage.panini += int(form.amount.data)
        else:
            self.storage.hot_dogs += int(form.amount.data)
            
        self.add_money(form.money.data, form.type_cost.data)
        supply = Supply(
            storage=self.storage,
            product_name=form.supply_choice.data,
            amount=form.amount.data,
            type_cost=form.cash_type.data,
            money=form.money.data,
            timestamp = datetime.now()
        )
        self.write_to_db(supply)
