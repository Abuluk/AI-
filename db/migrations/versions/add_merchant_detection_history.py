"""add merchant_detection_history

Revision ID: 3b4c5d6e7f8g
Revises: 2a3b4c5d6e7f
Create Date: 2023-10-27 11:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '3b4c5d6e7f8g'
down_revision = 'ee619d726d24'  # 最新的迁移版本
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'merchant_detection_histories',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('detection_type', sa.String(length=20), nullable=False),
        sa.Column('behavior_data', sa.JSON(), nullable=True),
        sa.Column('ai_analysis', sa.JSON(), nullable=True),
        sa.Column('active_items_count', sa.Integer(), nullable=False),
        sa.Column('is_merchant', sa.Boolean(), nullable=False),
        sa.Column('confidence', sa.Float(), nullable=False),
        sa.Column('ai_reason', sa.Text(), nullable=True),
        sa.Column('processed', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_merchant_detection_histories_id'), 'merchant_detection_histories', ['id'], unique=False)
    op.create_index(op.f('ix_merchant_detection_histories_user_id'), 'merchant_detection_histories', ['user_id'], unique=False)
    op.create_index(op.f('ix_merchant_detection_histories_detection_type'), 'merchant_detection_histories', ['detection_type'], unique=False)
    op.create_index(op.f('ix_merchant_detection_histories_created_at'), 'merchant_detection_histories', ['created_at'], unique=False)


def downgrade():
    op.drop_index(op.f('ix_merchant_detection_histories_created_at'), table_name='merchant_detection_histories')
    op.drop_index(op.f('ix_merchant_detection_histories_detection_type'), table_name='merchant_detection_histories')
    op.drop_index(op.f('ix_merchant_detection_histories_user_id'), table_name='merchant_detection_histories')
    op.drop_index(op.f('ix_merchant_detection_histories_id'), table_name='merchant_detection_histories')
    op.drop_table('merchant_detection_histories')
