"""merge user behavior and ai recommendation tables

Revision ID: 1164fca8824d
Revises: e97420f4f1ae, add_user_behavior_ai_config
Create Date: 2025-09-07 18:34:15.492278

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '1164fca8824d'
down_revision: Union[str, None] = ('e97420f4f1ae', 'add_user_behavior_ai_config')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
