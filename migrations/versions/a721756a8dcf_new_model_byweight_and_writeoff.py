"""New model ByWeight and WriteOff

Revision ID: a721756a8dcf
Revises: c47c25a9b62a
Create Date: 2021-10-04 21:29:18.963327

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a721756a8dcf'
down_revision = 'c47c25a9b62a'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('by_weight',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('timestamp', sa.DateTime(), nullable=True),
    sa.Column('coffee_shop_id', sa.Integer(), nullable=True),
    sa.Column('product_name', sa.String(length=80), nullable=True),
    sa.Column('amount', sa.Float(), nullable=True),
    sa.Column('type_cost', sa.String(length=64), nullable=True),
    sa.Column('money', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['coffee_shop_id'], ['coffee_shop.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_by_weight_timestamp'), 'by_weight', ['timestamp'], unique=False)
    op.create_index(op.f('ix_by_weight_type_cost'), 'by_weight', ['type_cost'], unique=False)
    op.create_table('write_off',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('timestamp', sa.DateTime(), nullable=True),
    sa.Column('coffee_shop_id', sa.Integer(), nullable=True),
    sa.Column('amount', sa.Float(), nullable=True),
    sa.ForeignKeyConstraint(['coffee_shop_id'], ['coffee_shop.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_write_off_timestamp'), 'write_off', ['timestamp'], unique=False)
    op.add_column('supply', sa.Column('product_name', sa.String(length=80), nullable=True))
    op.drop_column('supply', 'name')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('supply', sa.Column('name', sa.VARCHAR(length=80), autoincrement=False, nullable=True))
    op.drop_column('supply', 'product_name')
    op.drop_index(op.f('ix_write_off_timestamp'), table_name='write_off')
    op.drop_table('write_off')
    op.drop_index(op.f('ix_by_weight_type_cost'), table_name='by_weight')
    op.drop_index(op.f('ix_by_weight_timestamp'), table_name='by_weight')
    op.drop_table('by_weight')
    # ### end Alembic commands ###
