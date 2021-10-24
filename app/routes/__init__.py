from app import app
from app.forms import ExpanseForm, ByWeightForm, WriteOffForm, SupplyForm, TransferForm
from app.models import CoffeeShop, Warehouse, CoffeeShopEquipment


@app.context_processor
def inject_form():
    expense_form, by_weight_form, write_off_form = ExpanseForm(), ByWeightForm(), WriteOffForm()
    supply_form, transfer_form = SupplyForm(), TransferForm()
    coffee_shop_list = CoffeeShop.query.all()
    warehouse = Warehouse
    cs_equip = CoffeeShopEquipment
    return dict(expense_form=expense_form, by_weight_form=by_weight_form,
                write_off_form=write_off_form, supply_form=supply_form, transfer_form=transfer_form,
                coffee_shop_list=coffee_shop_list, warehouse=warehouse, cs_equip=cs_equip)
