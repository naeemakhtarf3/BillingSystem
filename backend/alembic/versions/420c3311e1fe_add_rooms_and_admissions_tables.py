"""add rooms and admissions tables

Revision ID: 420c3311e1fe
Revises: 005_add_etl_status_table
Create Date: 2025-10-24 15:27:02.165091

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '420c3311e1fe'
down_revision = '005_add_etl_status_table'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create rooms table
    op.create_table('room',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('room_number', sa.String(), nullable=False),
        sa.Column('type', sa.Enum('standard', 'private', 'icu', name='roomtype'), nullable=False),
        sa.Column('status', sa.Enum('available', 'occupied', 'maintenance', name='roomstatus'), nullable=False),
        sa.Column('daily_rate_cents', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=True),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_room_id'), 'room', ['id'], unique=False)
    op.create_index(op.f('ix_room_room_number'), 'room', ['room_number'], unique=True)

    # Create admissions table
    op.create_table('admission',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('room_id', sa.Integer(), nullable=False),
        sa.Column('patient_id', sa.String(), nullable=False),
        sa.Column('staff_id', sa.String(), nullable=False),
        sa.Column('admission_date', sa.DateTime(), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
        sa.Column('discharge_date', sa.DateTime(), nullable=True),
        sa.Column('invoice_id', sa.String(), nullable=True),
        sa.Column('status', sa.Enum('active', 'discharged', name='admissionstatus'), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=True),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=True),
        sa.ForeignKeyConstraint(['room_id'], ['room.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_admission_id'), 'admission', ['id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_admission_id'), table_name='admission')
    op.drop_table('admission')
    op.drop_index(op.f('ix_room_room_number'), table_name='room')
    op.drop_index(op.f('ix_room_id'), table_name='room')
    op.drop_table('room')
