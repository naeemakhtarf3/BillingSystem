"""add etl status table

Revision ID: 005_add_etl_status_table
Revises: 004_create_reporting_schema
Create Date: 2025-10-20
"""

from alembic import op
import sqlalchemy as sa


revision = "005_add_etl_status_table"
down_revision = "004_create_reporting_schema"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "etl_process_status",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("process_name", sa.String(100), nullable=False),
        sa.Column("status", sa.String(20), nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("records_processed", sa.Integer, nullable=False, server_default="0"),
        sa.Column("error_message", sa.Text, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )


def downgrade() -> None:
    op.drop_table("etl_process_status")


