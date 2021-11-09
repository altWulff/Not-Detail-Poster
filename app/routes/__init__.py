from flask_security import current_user
from app import app
from app.forms import ExpanseForm, ByWeightForm, WriteOffForm, SupplyForm, TransferForm
from app.models import Shop, Storage, ShopEquipment, Category, Expense, Supply, WriteOff
from app.business_logic import is_report_send as is_send


@app.context_processor
def inject_form():
    expense_form, by_weight_form, write_off_form = ExpanseForm(), ByWeightForm(), WriteOffForm()
    supply_form, transfer_form = SupplyForm(), TransferForm()
    coffee_shop_list = Shop.query.all()
    if current_user.is_authenticated:
        barista_work_list = Shop.get_barista_work(current_user.id).all()
    else:
        barista_work_list = []
    expense = Expense
    storage = Storage
    supply = Supply
    write_off = WriteOff
    cs_equip = ShopEquipment
    expense_form.categories.choices = [(c.id, c) for c in Category.query.all()]
    is_report_send = is_send
    return dict(expense_form=expense_form, by_weight_form=by_weight_form,
                write_off_form=write_off_form, supply_form=supply_form, transfer_form=transfer_form,
                coffee_shop_list=coffee_shop_list,
                barista_work_list=barista_work_list, warehouse=storage,
                supply=supply,
                write_off=WriteOff,
                cs_equip=cs_equip, expense=Expense, 
                is_report_send=is_report_send)
