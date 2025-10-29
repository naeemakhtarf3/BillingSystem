"""fix invoice_id foreign key type

Revision ID: 007_fix_invoice_id_foreign_key
Revises: 006_fix_model_inconsistencies
Create Date: 2025-01-27 10:30:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '007_fix_invoice_id_foreign_key'
down_revision = '006_fix_model_inconsistencies'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Fix admission table - change invoice_id from VARCHAR to UUID
    with op.batch_alter_table('admission', schema=None) as batch_op:
        # First drop the foreign key constraint
        batch_op.drop_constraint('admission_invoice_id_fkey', type_='foreignkey')
        
        # Change the column type from VARCHAR to UUID
        batch_op.alter_column('invoice_id',
                              existing_type=sa.String(),
                              type_=postgresql.UUID(as_uuid=True),
                              existing_nullable=True)
        
        # Recreate the foreign key constraint
        batch_op.create_foreign_key('admission_invoice_id_fkey', 'invoices', ['invoice_id'], ['id'])


def downgrade() -> None:
    # Reverse the changes
    with op.batch_alter_table('admission', schema=None) as batch_op:
        # Drop the foreign key constraint
        batch_op.drop_constraint('admission_invoice_id_fkey', type_='foreignkey')
        
        # Change the column type back from UUID to VARCHAR
        batch_op.alter_column('invoice_id',
                              existing_type=postgresql.UUID(as_uuid=True),
                              type_=sa.String(),
                              existing_nullable=True)
        
        # Recreate the foreign key constraint (this might fail if there are data type mismatches)
        batch_op.create_foreign_key('admission_invoice_id_fkey', 'invoices', ['invoice_id'], ['id'])
