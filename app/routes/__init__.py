from flask import g
from flask_babelex import get_locale
from app import app
from app.forms import ExpanseForm, ByWeightForm, WriteOffForm, SupplyForm, TransferForm
from app.models import Shop, Storage, ShopEquipment, Category, Expense, Supply, WriteOff
from app.business_logic import is_report_send as is_send


@app.before_request
def before_request():
    g.locale = str(get_locale())


@app.context_processor
def inject_form():
    expense_form = ExpanseForm()
    by_weight_form = ByWeightForm()
    write_off_form = WriteOffForm()
    supply_form = SupplyForm()
    transfer_form = TransferForm()
    return dict(
        expense_form=expense_form,
        by_weight_form=by_weight_form,
        write_off_form=write_off_form,
        supply_form=supply_form,
        transfer_form=transfer_form
    )


@app.context_processor
def inject_models():
    coffee_shop_list = Shop.query.all()
    return dict(
        coffee_shop_list=coffee_shop_list,
        warehouse=Storage,
        supply=Supply,
        write_off=WriteOff,
        cs_equip=ShopEquipment,
        expense=Expense,
        is_report_send=is_send
    )
