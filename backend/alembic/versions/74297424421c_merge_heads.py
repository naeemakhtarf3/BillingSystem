"""merge_heads

Revision ID: 74297424421c
Revises: 007_fix_invoice_id_foreign_key, add_version_columns
Create Date: 2025-10-29 17:17:08.294611

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '74297424421c'
down_revision = ('007_fix_invoice_id_foreign_key', 'add_version_columns')
branch_labels = None
depends_on = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
