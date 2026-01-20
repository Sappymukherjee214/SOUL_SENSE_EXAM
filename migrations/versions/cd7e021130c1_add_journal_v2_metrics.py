"""Add journal v2 metrics

Revision ID: cd7e021130c1
Revises: f62984ab805f
Create Date: 2026-01-14 22:34:02.357037

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'cd7e021130c1'
down_revision: Union[str, Sequence[str], None] = 'f62984ab805f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('journal_entries', sa.Column('screen_time_mins', sa.Integer(), nullable=True))
    op.add_column('journal_entries', sa.Column('stress_level', sa.Integer(), nullable=True))
    op.add_column('journal_entries', sa.Column('stress_triggers', sa.Text(), nullable=True))
    op.add_column('journal_entries', sa.Column('daily_schedule', sa.Text(), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    with op.batch_alter_table('journal_entries') as batch_op:
        batch_op.drop_column('daily_schedule')
        batch_op.drop_column('stress_triggers')
        batch_op.drop_column('stress_level')
        batch_op.drop_column('screen_time_mins')
