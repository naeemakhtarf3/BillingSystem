"""fix room type enum values

Revision ID: fix_room_type_enum_values
Revises: 420c3311e1fe
Create Date: 2025-10-24 15:27:02.165091

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'fix_room_type_enum_values'
down_revision = '420c3311e1fe'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Update existing enum values to uppercase
    op.execute("UPDATE room SET type = UPPER(type)")
    # Drop and recreate the enum with uppercase values
    op.execute("DROP TYPE roomtype")
    op.execute("CREATE TYPE roomtype AS ENUM('STANDARD', 'PRIVATE', 'ICU')")
    op.alter_column('room', 'type', type_=sa.Enum('STANDARD', 'PRIVATE', 'ICU', name='roomtype'))


def downgrade() -> None:
    # Revert to lowercase values
    op.execute("UPDATE room SET type = LOWER(type)")
    op.execute("DROP TYPE roomtype")
    op.execute("CREATE TYPE roomtype AS ENUM('standard', 'private', 'icu')")
    op.alter_column('room', 'type', type_=sa.Enum('standard', 'private', 'icu', name='roomtype'))
