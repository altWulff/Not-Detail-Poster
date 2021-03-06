"""
Module define Transaction logic
"""


from datetime import date, datetime

from flask_security import current_user
from sqlalchemy import func

from app import app, db
from app.models import (ByWeight, Category, Expense, Report, Shop,
                        ShopEquipment, Storage, Supply, WriteOff)


def transaction_count(shop_id: int) -> int:
    """Lengths list reports by today"""
    reports = Report.query.filter_by(shop_id=shop_id)
    reports_today = reports.filter(func.date(Report.timestamp) == date.today()).all()
    return len(reports_today)


def is_report_send(shop_id: int) -> bool:
    """Check if report send and compare with config variable"""
    return transaction_count(shop_id) >= app.config["REPORTS_PER_DAY"]


class TransactionHandler:
    """
    Transaction handler
    Get shop, storage, equipment from shop_id
    """

    def __init__(self, shop_id=None):
        self.shop = self.get_shop_from_id(shop_id)
        self.storage = self.get_storage_from_id(shop_id)
        self.equipment = self.get_equipment_from_id(shop_id)

    @staticmethod
    def get_shop_from_id(shop_id):
        """Query shop by shop id"""
        query = Shop.query.filter_by(id=shop_id).first_or_404()
        return query

    @staticmethod
    def get_storage_from_id(shop_id):
        """Query storage by shop id"""
        query = Storage.query.filter_by(shop_id=shop_id).first_or_404()
        return query

    @staticmethod
    def get_equipment_from_id(shop_id):
        """Query shop equipment by shop id"""
        query = ShopEquipment.query.filter_by(shop_id=shop_id).first_or_404()
        return query

    @staticmethod
    def is_report_send(shop_id: int) -> bool:
        """Check if report send and compare with config variable"""
        return transaction_count(shop_id) >= app.config["REPORTS_PER_DAY"]

    def funds_expenditure(self, money, type_cost):
        """Funds expenditure by type cost"""
        if type_cost == "cash":
            self.shop.cash -= money
        else:
            self.shop.cashless -= money

    def cash_flow(self, money, type_cost):
        """Cash flow by type cost"""
        if type_cost == "cash":
            self.shop.cash += money
        else:
            self.shop.cashless += money

    @staticmethod
    def write_to_db(record):
        """Write record to database"""
        db.session.add(record)
        db.session.commit()

    def create_expense(self, form):
        """Create expense transaction"""
        expense = Expense(
            type_cost=form.type_cost.data,
            money=form.money.data,
            is_global=form.is_global.data,
            barista=current_user,
        )
        self.funds_expenditure(form.money.data, form.type_cost.data)
        for c_id in form.categories.data:
            category = Category.query.filter_by(id=c_id).first_or_404()
            expense.categories.append(category)
        self.shop.expenses.append(expense)
        self.write_to_db(expense)

    def crete_by_weight(self, form):
        """Create by weight transaction"""
        if form.by_weight_choice.data == "coffee_blend":
            self.storage.coffee_blend -= form.amount.data
        else:
            self.storage.coffee_arabika -= form.amount.data

        self.cash_flow(form.money.data, form.type_cost.data)
        by_weight = ByWeight(
            storage=self.storage,
            amount=form.amount.data,
            product_name=form.by_weight_choice.data,
            type_cost=form.type_cost.data,
            money=form.money.data,
            barista=current_user,
        )
        self.write_to_db(by_weight)

    def create_write_off(self, form):
        """Create write off transaction"""
        if form.write_off_choice.data == "coffee_blend":
            self.storage.coffee_blend -= form.amount.data
        elif form.write_off_choice.data == "coffee_arabika":
            self.storage.coffee_arabika -= form.amount.data
        elif form.write_off_choice.data == "milk":
            self.storage.milk -= form.amount.data
        elif form.write_off_choice.data == "panini":
            self.storage.panini -= int(form.amount.data)
        elif form.write_off_choice.data == "sausages":
            self.storage.sausages -= int(form.amount.data)
        else:
            self.storage.buns -= int(form.amount.data)
        write_off = WriteOff(
            storage=self.storage,
            amount=form.amount.data,
            product_name=form.write_off_choice.data,
            barista=current_user,
        )
        self.write_to_db(write_off)

    def create_supply(self, form):
        """Create supply transaction"""
        if form.supply_choice.data == "coffee_blend":
            self.storage.coffee_blend += form.amount.data
        elif form.supply_choice.data == "coffee_arabika":
            self.storage.coffee_arabika += form.amount.data
        elif form.supply_choice.data == "milk":
            self.storage.milk += form.amount.data
        elif form.supply_choice.data == "panini":
            self.storage.panini += int(form.amount.data)
        elif form.supply_choice.data == "sausages":
            self.storage.sausages += int(form.amount.data)
        else:
            self.storage.buns += int(form.amount.data)

        self.funds_expenditure(form.money.data, form.type_cost.data)
        supply = Supply(
            storage=self.storage,
            product_name=form.supply_choice.data,
            amount=form.amount.data,
            type_cost=form.type_cost.data,
            money=form.money.data,
            barista=current_user,
        )
        self.write_to_db(supply)

    def create_report(self, form):
        """Create day report transaction"""
        day_expanses = Expense.get_local(self.shop.id, True)
        day_by_weight = ByWeight.get_local_by_shop(self.shop.id)
        expanses = sum([e.money for e in day_expanses if e.type_cost == "cash"])
        by_weight = sum([e.money for e in day_by_weight if e.type_cost == "cash"])
        last_actual_balance = self.shop.cash + expanses - by_weight
        cash_balance = form.actual_balance.data - last_actual_balance
        remainder_of_day = cash_balance + form.cashless.data
        if form.cleaning_coffee_machine.data:
            self.equipment.last_cleaning_coffee_machine = datetime.utcnow()
        if form.cleaning_grinder.data:
            self.equipment.last_cleaning_grinder = datetime.utcnow()
        report = Report(
            cashbox=remainder_of_day + expanses,
            cash_balance=cash_balance,
            cashless=form.cashless.data,
            actual_balance=form.actual_balance.data,
            remainder_of_day=remainder_of_day,
            barista=current_user,
            shop=self.shop,
            coffee_arabika=form.coffee_arabika.data,
            coffee_blend=form.coffee_blend.data,
            milk=form.milk.data,
            panini=form.panini.data,
            sausages=form.sausages.data,
            buns=form.buns.data,
        )
        report.expenses = day_expanses.all()
        self.cash_flow(cash_balance + expanses - by_weight, "cash")
        self.cash_flow(form.cashless.data, "cashless")

        def weight_amount(product_name):
            weight = [w.amount for w in day_by_weight if w.product_name == product_name]
            return sum(weight)

        products = (
            "coffee_arabika",
            "coffee_blend",
            "milk",
            "panini",
            "sausages",
            "buns",
        )
        for i in products:
            consumption_value = (
                getattr(self.storage, i) - getattr(form, i).data + weight_amount(i)
            )
            setattr(report, f"consumption_{i}", consumption_value)
            consumption_to_storage = getattr(self.storage, i) - getattr(
                report, f"consumption_{i}"
            )
            setattr(self.storage, i, consumption_to_storage)

        self.write_to_db(report)
