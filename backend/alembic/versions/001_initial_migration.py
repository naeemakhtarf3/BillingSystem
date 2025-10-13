"""Initial migration

Revision ID: 001
Revises: 
Create Date: 2024-01-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create staff table
    op.create_table('staff',
    sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('email', sa.String(), nullable=False),
    sa.Column('password_hash', sa.String(), nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('role', sa.Enum('ADMIN', 'BILLING_CLERK', name='staffrole'), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_staff_email'), 'staff', ['email'], unique=True)
    
    # Create patients table
    op.create_table('patients',
    sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('email', sa.String(), nullable=True),
    sa.Column('phone', sa.String(), nullable=True),
    sa.Column('dob', sa.Date(), nullable=True),
    sa.Column('metadata', sa.JSON(), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    
    # Create invoices table
    op.create_table('invoices',
    sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('invoice_number', sa.String(), nullable=False),
    sa.Column('patient_id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('staff_id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('currency', sa.String(), nullable=False),
    sa.Column('total_amount_cents', sa.Integer(), nullable=False),
    sa.Column('status', sa.Enum('DRAFT', 'ISSUED', 'PAID', 'PARTIALLY_PAID', 'CANCELLED', name='invoicestatus'), nullable=False),
    sa.Column('issued_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('due_date', sa.Date(), nullable=True),
    sa.Column('stripe_payment_link_id', sa.String(), nullable=True),
    sa.Column('stripe_checkout_session_id', sa.String(), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
    sa.ForeignKeyConstraint(['patient_id'], ['patients.id'], ),
    sa.ForeignKeyConstraint(['staff_id'], ['staff.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_invoices_invoice_number'), 'invoices', ['invoice_number'], unique=True)
    
    # Create invoice_items table
    op.create_table('invoice_items',
    sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('invoice_id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('description', sa.String(), nullable=False),
    sa.Column('quantity', sa.Integer(), nullable=False),
    sa.Column('unit_price_cents', sa.Integer(), nullable=False),
    sa.Column('tax_cents', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['invoice_id'], ['invoices.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    
    # Create payments table
    op.create_table('payments',
    sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('invoice_id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('stripe_payment_id', sa.String(), nullable=False),
    sa.Column('amount_cents', sa.Integer(), nullable=False),
    sa.Column('currency', sa.String(), nullable=False),
    sa.Column('status', sa.Enum('SUCCEEDED', 'FAILED', 'REFUNDED', name='paymentstatus'), nullable=False),
    sa.Column('received_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.Column('raw_event', sa.JSON(), nullable=True),
    sa.ForeignKeyConstraint(['invoice_id'], ['invoices.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_payments_stripe_payment_id'), 'payments', ['stripe_payment_id'], unique=True)
    
    # Create audit_logs table
    op.create_table('audit_logs',
    sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('actor_type', sa.Enum('STAFF', 'SYSTEM', name='actortype'), nullable=False),
    sa.Column('actor_id', postgresql.UUID(as_uuid=True), nullable=True),
    sa.Column('action', sa.String(), nullable=False),
    sa.Column('target_type', sa.String(), nullable=True),
    sa.Column('target_id', postgresql.UUID(as_uuid=True), nullable=True),
    sa.Column('details', sa.JSON(), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )


def downgrade() -> None:
    op.drop_table('audit_logs')
    op.drop_table('payments')
    op.drop_table('invoice_items')
    op.drop_table('invoices')
    op.drop_table('patients')
    op.drop_table('staff')
    
    # Drop enums
    op.execute('DROP TYPE IF EXISTS actortype')
    op.execute('DROP TYPE IF EXISTS paymentstatus')
    op.execute('DROP TYPE IF EXISTS invoicestatus')
    op.execute('DROP TYPE IF EXISTS staffrole')
