"""add site_config table

Revision ID: 750792150d71
Revises: 1f2aa26b86fd
Create Date: 2025-06-26 00:56:35.158311

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '750792150d71'
down_revision: Union[str, None] = '1f2aa26b86fd'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        'site_config',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('key', sa.String(100), unique=True, nullable=False),
        sa.Column('value', sa.Text(), nullable=True)
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table('site_config')
