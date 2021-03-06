"""Add timemixin

Revision ID: e966337348a4
Revises: 6f9d8f1efa95
Create Date: 2022-01-03 15:01:31.659301

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e966337348a4'
down_revision = '6f9d8f1efa95'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_index(op.f('ix_by_weight_last_edit'), 'by_weight', ['last_edit'], unique=False)
    op.create_index(op.f('ix_by_weight_timestamp'), 'by_weight', ['timestamp'], unique=False)
    op.create_index(op.f('ix_collection_fund_last_edit'), 'collection_fund', ['last_edit'], unique=False)
    op.create_index(op.f('ix_collection_fund_timestamp'), 'collection_fund', ['timestamp'], unique=False)
    op.create_index(op.f('ix_deposit_fund_last_edit'), 'deposit_fund', ['last_edit'], unique=False)
    op.create_index(op.f('ix_deposit_fund_timestamp'), 'deposit_fund', ['timestamp'], unique=False)
    op.create_index(op.f('ix_expense_last_edit'), 'expense', ['last_edit'], unique=False)
    op.create_index(op.f('ix_expense_timestamp'), 'expense', ['timestamp'], unique=False)
    op.create_index(op.f('ix_report_last_edit'), 'report', ['last_edit'], unique=False)
    op.create_index(op.f('ix_report_timestamp'), 'report', ['timestamp'], unique=False)
    op.create_index(op.f('ix_supply_last_edit'), 'supply', ['last_edit'], unique=False)
    op.create_index(op.f('ix_supply_timestamp'), 'supply', ['timestamp'], unique=False)
    op.create_index(op.f('ix_transfer_product_last_edit'), 'transfer_product', ['last_edit'], unique=False)
    op.create_index(op.f('ix_transfer_product_timestamp'), 'transfer_product', ['timestamp'], unique=False)
    op.create_index(op.f('ix_write_off_last_edit'), 'write_off', ['last_edit'], unique=False)
    op.create_index(op.f('ix_write_off_timestamp'), 'write_off', ['timestamp'], unique=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_write_off_timestamp'), table_name='write_off')
    op.drop_index(op.f('ix_write_off_last_edit'), table_name='write_off')
    op.drop_index(op.f('ix_transfer_product_timestamp'), table_name='transfer_product')
    op.drop_index(op.f('ix_transfer_product_last_edit'), table_name='transfer_product')
    op.drop_index(op.f('ix_supply_timestamp'), table_name='supply')
    op.drop_index(op.f('ix_supply_last_edit'), table_name='supply')
    op.drop_index(op.f('ix_report_timestamp'), table_name='report')
    op.drop_index(op.f('ix_report_last_edit'), table_name='report')
    op.drop_index(op.f('ix_expense_timestamp'), table_name='expense')
    op.drop_index(op.f('ix_expense_last_edit'), table_name='expense')
    op.drop_index(op.f('ix_deposit_fund_timestamp'), table_name='deposit_fund')
    op.drop_index(op.f('ix_deposit_fund_last_edit'), table_name='deposit_fund')
    op.drop_index(op.f('ix_collection_fund_timestamp'), table_name='collection_fund')
    op.drop_index(op.f('ix_collection_fund_last_edit'), table_name='collection_fund')
    op.drop_index(op.f('ix_by_weight_timestamp'), table_name='by_weight')
    op.drop_index(op.f('ix_by_weight_last_edit'), table_name='by_weight')
    # ### end Alembic commands ###
