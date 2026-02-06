"""Add session_id to scores and responses

Revision ID: 026c42076d07
Revises: 0394250e44ad
Create Date: 2026-02-05 18:58:49.625536

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '026c42076d07'
down_revision: Union[str, Sequence[str], None] = '0394250e44ad'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    with op.batch_alter_table('scores', schema=None) as batch_op:
        batch_op.add_column(sa.Column('session_id', sa.String(), nullable=True))
        batch_op.create_index(batch_op.f('ix_scores_session_id'), ['session_id'], unique=False)

    with op.batch_alter_table('responses', schema=None) as batch_op:
        batch_op.add_column(sa.Column('session_id', sa.String(), nullable=True))
        batch_op.create_index(batch_op.f('ix_responses_session_id'), ['session_id'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    with op.batch_alter_table('responses', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_responses_session_id'))
        batch_op.drop_column('session_id')

    with op.batch_alter_table('scores', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_scores_session_id'))
        batch_op.drop_column('session_id')
