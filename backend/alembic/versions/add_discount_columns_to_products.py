"""Add discount and offer columns to products table.

Revision ID: 001
Revises: 2ae15150517a
Create Date: 2026-04-26 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '001'
down_revision = '2ae15150517a'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Add new columns to products table."""
    # Check if columns already exist before adding them
    op.add_column('products', sa.Column('discount_percentage', sa.Float(), nullable=True))
    op.add_column('products', sa.Column('offer_price', sa.Float(), nullable=True))
    op.add_column('products', sa.Column('offer_description', sa.String(255), nullable=True))
    op.add_column('products', sa.Column('min_quantity_for_offer', sa.Float(), nullable=True))
    op.add_column('products', sa.Column('max_quantity_per_order', sa.Float(), nullable=True))


def downgrade() -> None:
    """Remove added columns from products table."""
    op.drop_column('products', 'max_quantity_per_order')
    op.drop_column('products', 'min_quantity_for_offer')
    op.drop_column('products', 'offer_description')
    op.drop_column('products', 'offer_price')
    op.drop_column('products', 'discount_percentage')
