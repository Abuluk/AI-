"""Add merchant detection config table

Revision ID: add_merchant_detection_config
Revises: 
Create Date: 2024-01-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_merchant_detection_config'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Create merchant_detection_configs table
    op.create_table('merchant_detection_configs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('key', sa.String(length=100), nullable=False),
        sa.Column('value', sa.Text(), nullable=True),
        sa.Column('description', sa.String(length=500), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('key')
    )
    
    # Create index on key column
    op.create_index(op.f('ix_merchant_detection_configs_key'), 'merchant_detection_configs', ['key'], unique=True)


def downgrade():
    # Drop the table
    op.drop_index(op.f('ix_merchant_detection_configs_key'), table_name='merchant_detection_configs')
    op.drop_table('merchant_detection_configs')
