"""add optimistic locking version columns

Revision ID: add_version_columns
Revises: 420c3311e1fe
Create Date: 2025-10-24 15:45:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'add_version_columns'
down_revision = '420c3311e1fe'
branch_labels = None
depends_on = None

def upgrade() -> None:
    # Add version column to room table
    op.add_column('room', sa.Column('version', sa.Integer(), nullable=False, server_default='1'))
    
    # Add version column to admission table
    op.add_column('admission', sa.Column('version', sa.Integer(), nullable=False, server_default='1'))

def downgrade() -> None:
    op.drop_column('admission', 'version')
    op.drop_column('room', 'version')
