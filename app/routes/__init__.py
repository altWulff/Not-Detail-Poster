from app import app
from app.forms import ExpanseForm, ByWeightForm, WriteOffForm, SupplyForm, TransferForm
from app.models import Shop, Storage, ShopEquipment, Category


@app.context_processor
def inject_form():
    expense_form, by_weight_form, write_off_form = ExpanseForm(), ByWeightForm(), WriteOffForm()
    supply_form, transfer_form = SupplyForm(), TransferForm()
    coffee_shop_list = Shop.query.all()
    storage = Storage
    cs_equip = ShopEquipment
    expense_form.categories.choices = [(c.id, c) for c in Category.query.all()]
    return dict(expense_form=expense_form, by_weight_form=by_weight_form,
                write_off_form=write_off_form, supply_form=supply_form, transfer_form=transfer_form,
                coffee_shop_list=coffee_shop_list, warehouse=storage, cs_equip=cs_equip)
