"""Add Deposit and Collection Funds models, add column last_cleaning on Equipment

Revision ID: 0a8a9ab3e8fa
Revises: c2884864ed78
Create Date: 2021-12-04 09:32:43.910912

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0a8a9ab3e8fa'
down_revision = 'c2884864ed78'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('collection_funds',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('barista_id', sa.Integer(), nullable=True),
    sa.Column('shop_id', sa.Integer(), nullable=True),
    sa.Column('backdating', sa.Boolean(), nullable=True),
    sa.Column('timestamp', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.Column('last_edit', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.Column('type_cost', sa.String(length=64), nullable=True),
    sa.Column('money', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['barista_id'], ['barista.id'], ),
    sa.ForeignKeyConstraint(['shop_id'], ['shop.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_collection_funds_type_cost'), 'collection_funds', ['type_cost'], unique=False)
    op.create_table('deposit_funds',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('barista_id', sa.Integer(), nullable=True),
    sa.Column('shop_id', sa.Integer(), nullable=True),
    sa.Column('backdating', sa.Boolean(), nullable=True),
    sa.Column('timestamp', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.Column('last_edit', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.Column('type_cost', sa.String(length=64), nullable=True),
    sa.Column('money', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['barista_id'], ['barista.id'], ),
    sa.ForeignKeyConstraint(['shop_id'], ['shop.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_deposit_funds_type_cost'), 'deposit_funds', ['type_cost'], unique=False)
    op.add_column('shop_equipment', sa.Column('last_cleaning_coffee_machine', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True))
    op.add_column('shop_equipment', sa.Column('last_cleaning_grinder', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('shop_equipment', 'last_cleaning_grinder')
    op.drop_column('shop_equipment', 'last_cleaning_coffee_machine')
    op.drop_index(op.f('ix_deposit_funds_type_cost'), table_name='deposit_funds')
    op.drop_table('deposit_funds')
    op.drop_index(op.f('ix_collection_funds_type_cost'), table_name='collection_funds')
    op.drop_table('collection_funds')
    # ### end Alembic commands ###