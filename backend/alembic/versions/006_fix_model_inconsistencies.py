"""fix model inconsistencies

Revision ID: 006_fix_model_inconsistencies
Revises: 420c3311e1fe
Create Date: 2025-01-27 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '006_fix_model_inconsistencies'
down_revision = '420c3311e1fe'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Fix admission table - change id from String to Integer
    with op.batch_alter_table('admission', schema=None) as batch_op:
        # First, we need to handle existing data if any
        # For now, we'll assume the table is empty or we can safely convert
        batch_op.alter_column('id',
                              existing_type=sa.String(),
                              type_=sa.Integer(),
                              existing_nullable=False)
        
        # Add missing columns
        batch_op.add_column(sa.Column('discharge_reason', sa.String(), nullable=True))
        batch_op.add_column(sa.Column('discharge_notes', sa.Text(), nullable=True))
        batch_op.add_column(sa.Column('version', sa.Integer(), nullable=False, server_default='1'))
        
        # Fix admission_date to have proper server_default
        batch_op.alter_column('admission_date',
                              existing_type=sa.DateTime(),
                              server_default=sa.text('(CURRENT_TIMESTAMP)'),
                              existing_nullable=False)
        
        # Fix invoice_id to be String to match Invoice model UUID
        batch_op.alter_column('invoice_id',
                              existing_type=sa.String(),
                              type_=sa.String(),
                              existing_nullable=True)
    
    # Fix room table - add version column
    with op.batch_alter_table('room', schema=None) as batch_op:
        batch_op.add_column(sa.Column('version', sa.Integer(), nullable=False, server_default='1'))


def downgrade() -> None:
    # Remove added columns
    with op.batch_alter_table('admission', schema=None) as batch_op:
        batch_op.drop_column('version')
        batch_op.drop_column('discharge_notes')
        batch_op.drop_column('discharge_reason')
        batch_op.alter_column('id',
                              existing_type=sa.Integer(),
                              type_=sa.String(),
                              existing_nullable=False)
    
    with op.batch_alter_table('room', schema=None) as batch_op:
        batch_op.drop_column('version')
