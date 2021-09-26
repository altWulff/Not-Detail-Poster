"""Remove unique args on CoffeeShopEquipment

Revision ID: 5a64ff1befa8
Revises: 5d5320430c93
Create Date: 2021-09-26 18:40:04.177961

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '5a64ff1befa8'
down_revision = '5d5320430c93'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index('ix_coffee_shop_equipment_coffee_machine', table_name='coffee_shop_equipment')
    op.create_index(op.f('ix_coffee_shop_equipment_coffee_machine'), 'coffee_shop_equipment', ['coffee_machine'], unique=False)
    op.drop_index('ix_coffee_shop_equipment_grinder_1', table_name='coffee_shop_equipment')
    op.create_index(op.f('ix_coffee_shop_equipment_grinder_1'), 'coffee_shop_equipment', ['grinder_1'], unique=False)
    op.drop_index('ix_coffee_shop_equipment_grinder_2', table_name='coffee_shop_equipment')
    op.create_index(op.f('ix_coffee_shop_equipment_grinder_2'), 'coffee_shop_equipment', ['grinder_2'], unique=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_coffee_shop_equipment_grinder_2'), table_name='coffee_shop_equipment')
    op.create_index('ix_coffee_shop_equipment_grinder_2', 'coffee_shop_equipment', ['grinder_2'], unique=False)
    op.drop_index(op.f('ix_coffee_shop_equipment_grinder_1'), table_name='coffee_shop_equipment')
    op.create_index('ix_coffee_shop_equipment_grinder_1', 'coffee_shop_equipment', ['grinder_1'], unique=False)
    op.drop_index(op.f('ix_coffee_shop_equipment_coffee_machine'), table_name='coffee_shop_equipment')
    op.create_index('ix_coffee_shop_equipment_coffee_machine', 'coffee_shop_equipment', ['coffee_machine'], unique=False)
    # ### end Alembic commands ###
