"""create_user_profiles_table

Revision ID: 73e92db0ee84
Revises: 
Create Date: 2025-11-12 10:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '73e92db0ee84'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """創建 user_profiles 表"""
    op.create_table(
        'user_profiles',
        sa.Column('user_id', sa.String(length=255), nullable=False, comment='用戶 ID（主鍵）'),
        sa.Column('style_tags', postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default='{}', comment='風格標籤字典'),
        sa.Column('sentiment_history', postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default='{}', comment='情感歷史字典'),
        sa.Column('last_updated', sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text('now()'), comment='最後更新時間'),
        sa.PrimaryKeyConstraint('user_id'),
        comment='用戶畫像數據表'
    )
    # 創建索引以優化查詢性能
    op.create_index(
        'ix_user_profiles_last_updated',
        'user_profiles',
        ['last_updated'],
        unique=False
    )


def downgrade() -> None:
    """刪除 user_profiles 表"""
    op.drop_index('ix_user_profiles_last_updated', table_name='user_profiles')
    op.drop_table('user_profiles')
