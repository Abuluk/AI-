"""create_users_table

Revision ID: d4d83233934d
Revises: 
Create Date: 2025-06-19 11:04:16.047346

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd4d83233934d'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Integer, primary_key=True, index=True),
        sa.Column("username", sa.String(100), unique=True, nullable=False),
        sa.Column("email", sa.String(200), unique=True, index=True, nullable=False),
        sa.Column("phone", sa.String(20), unique=True, index=True, nullable=True),
        sa.Column("hashed_password", sa.String(200), nullable=False),
        sa.Column("is_active", sa.Boolean, default=True),
        sa.Column("created_at", sa.TIMESTAMP, server_default=sa.func.current_timestamp(), nullable=False),
        sa.Column("updated_at", sa.TIMESTAMP, server_default=sa.func.current_timestamp(), 
                  onupdate=sa.func.current_timestamp(), nullable=False)
    )

def downgrade() -> None:
    op.drop_table("users")