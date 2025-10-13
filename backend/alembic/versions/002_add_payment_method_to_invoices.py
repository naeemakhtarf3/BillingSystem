"""Add payment_method to invoices

Revision ID: 002
Revises: 001
Create Date: 2025-10-08 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '002'
down_revision = '001'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('invoices', sa.Column('payment_method', sa.String(), nullable=True))


def downgrade() -> None:
    op.drop_column('invoices', 'payment_method')
