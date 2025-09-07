"""merge heads

Revision ID: e97420f4f1ae
Revises: 14c510e73d2c, add_merchant_detection_config, 3b4c5d6e7f8g
Create Date: 2025-09-07 17:22:04.231447

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e97420f4f1ae'
down_revision: Union[str, None] = ('14c510e73d2c', 'add_merchant_detection_config', '3b4c5d6e7f8g')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
