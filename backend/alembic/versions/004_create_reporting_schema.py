"""create reporting schema tables

Revision ID: 004_create_reporting_schema
Revises: 003_add_audit_logs_table
Create Date: 2025-10-20
"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "004_create_reporting_schema"
down_revision = "003_add_audit_logs_table"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "revenue_metrics",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("date_key", sa.Date, nullable=False, index=True),
        sa.Column("total_revenue", sa.Numeric(10, 2), nullable=False, server_default="0"),
        sa.Column("payment_count", sa.Integer, nullable=False, server_default="0"),
        sa.Column("average_payment", sa.Numeric(10, 2), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
    )

    op.create_table(
        "patient_payment_history",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("patient_id", sa.String(50), nullable=False, index=True),
        sa.Column("payment_date", sa.Date, nullable=False, index=True),
        sa.Column("amount", sa.Numeric(10, 2), nullable=False),
        sa.Column("payment_status", sa.String(20), nullable=False, index=True),
        sa.Column("invoice_id", sa.String(50), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    op.create_table(
        "outstanding_payments",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("patient_id", sa.String(50), nullable=False, index=True),
        sa.Column("invoice_id", sa.String(50), nullable=False),
        sa.Column("amount_due", sa.Numeric(10, 2), nullable=False),
        sa.Column("days_overdue", sa.Integer, nullable=False, index=True),
        sa.Column("last_payment_date", sa.Date, nullable=True),
        sa.Column("payment_status", sa.String(20), nullable=False, index=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
    )


def downgrade() -> None:
    op.drop_table("outstanding_payments")
    op.drop_table("patient_payment_history")
    op.drop_table("revenue_metrics")


