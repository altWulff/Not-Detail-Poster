from flask_babelex import get_locale
from flask_babelex import lazy_gettext as _l
from flask import g
from app import app
from app.forms import ExpanseForm, ByWeightForm, WriteOffForm, SupplyForm, TransferForm
from app.models import Shop, Expense, DepositFund, CollectionFund, Supply, WriteOff
from app.business_logic import is_report_send as is_send


@app.before_request
def before_request():
    g.locale = str(get_locale())


@app.template_filter('translate')
def translate_filter(s):
    dict_translate = dict(
        cash=_l('наличка'),
        cashless=_l('безнал'),
        coffee_arabika=_l('арабика'),
        coffee_blend=_l('купаж'),
        milk=_l('молоко'),
        panini=_l('панини'),
        sausages=_l('колбаски'),
        buns=_l('булочки'),
    )
    return dict_translate.get(s, s).title()


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
        supply=Supply,
        write_off=WriteOff,
        expense=Expense,
        deposit_fund=DepositFund,
        collection_fund=CollectionFund,
        is_report_send=is_send
    )
