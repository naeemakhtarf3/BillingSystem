"""Add audit_logs table

Revision ID: 003_add_audit_logs_table
Revises: 002_add_payment_method_to_invoices
Create Date: 2025-10-09 05:10:00.000000
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '003_add_audit_logs_table'
down_revision = '002_add_payment_method_to_invoices'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'audit_logs',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, default=sa.text('gen_random_uuid()')),
        sa.Column('actor_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('actor_type', sa.String(), nullable=True),
        sa.Column('action', sa.String(), nullable=False),
        sa.Column('object_type', sa.String(), nullable=True),
        sa.Column('object_id', sa.String(), nullable=True),
        sa.Column('details', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'))
    )


def downgrade():
    op.drop_table('audit_logs')
