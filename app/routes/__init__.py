"""
Init route package
"""


from flask import g
from flask_babelex import get_locale
from flask_babelex import lazy_gettext as _l

from app import app
from app.business_logic import is_report_send as is_send
from app.forms import (ByWeightForm, ExpanseForm, SupplyForm, TransferForm,
                       WriteOffForm)
from app.models import (ByWeight, CollectionFund, DepositFund, Expense, Shop,
                        Supply, TransferProduct, WriteOff)


@app.before_request
def before_request():
    """Locale variables in templates"""
    g.locale = str(get_locale())


@app.template_filter("translate")
def translate_filter(word):
    """Jinja filter, translate words from dict"""
    default = word
    dict_translate = dict(
        cash=_l("наличка"),
        cashless=_l("безнал"),
        coffee_arabika=_l("арабика"),
        coffee_blend=_l("купаж"),
        milk=_l("молоко"),
        panini=_l("панини"),
        sausages=_l("колбаски"),
        buns=_l("булочки"),
    )
    return dict_translate.get(word, default).title()


@app.context_processor
def inject_form():
    """
    Injection forms instance in context view
    :return: dict from predict forms
    """
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
        transfer_form=transfer_form,
    )


@app.context_processor
def inject_models():
    """
    Inject db models in context view
    :return: dict from predict models
    """
    coffee_shop_list = Shop.query.all()
    return dict(
        coffee_shop_list=coffee_shop_list,
        supply=Supply,
        by_weight=ByWeight,
        write_off=WriteOff,
        expense=Expense,
        deposit_fund=DepositFund,
        collection_fund=CollectionFund,
        transfer=TransferProduct,
        is_report_send=is_send,
    )
