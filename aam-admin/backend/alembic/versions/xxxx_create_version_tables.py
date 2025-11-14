"""create version tables

Revision ID: xxxx_create_version_tables
Revises: 6ffd7a52d3fe
Create Date: 2025-01-14 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'xxxx_create_version_tables'
down_revision: Union[str, None] = '6ffd7a52d3fe'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 创建版本状态枚举类型
    versionstatus_enum = postgresql.ENUM('ACTIVE', 'AVAILABLE', 'DEPRECATED', name='versionstatus', create_type=True)
    versionstatus_enum.create(op.get_bind(), checkfirst=True)

    # 创建 versions 表
    op.create_table('versions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('version', sa.String(length=100), nullable=False),
        sa.Column('status', versionstatus_enum, nullable=False),
        sa.Column('git_commit', sa.String(length=40), nullable=True),
        sa.Column('git_branch', sa.String(length=255), nullable=True),
        sa.Column('git_tag', sa.String(length=255), nullable=True),
        sa.Column('image_tag', sa.String(length=255), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('created_by', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_version_version', 'versions', ['version'], unique=True)
    op.create_index('idx_version_status', 'versions', ['status'], unique=False)
    op.create_index('idx_version_created_at', 'versions', ['created_at'], unique=False)
    op.create_index(op.f('ix_versions_id'), 'versions', ['id'], unique=False)

    # 创建 version_configs 表
    op.create_table('version_configs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('version_id', sa.Integer(), nullable=False),
        sa.Column('docker_compose_config', sa.JSON(), nullable=True),
        sa.Column('environment_variables', sa.JSON(), nullable=True),
        sa.Column('service_config', sa.JSON(), nullable=True),
        sa.Column('config_snapshot', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['version_id'], ['versions.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_version_config_version_id', 'version_configs', ['version_id'], unique=False)
    op.create_index(op.f('ix_version_configs_id'), 'version_configs', ['id'], unique=False)


def downgrade() -> None:
    # 删除索引和表
    op.drop_index(op.f('ix_version_configs_id'), table_name='version_configs')
    op.drop_index('idx_version_config_version_id', table_name='version_configs')
    op.drop_table('version_configs')
    
    op.drop_index(op.f('ix_versions_id'), table_name='versions')
    op.drop_index('idx_version_created_at', table_name='versions')
    op.drop_index('idx_version_status', table_name='versions')
    op.drop_index('idx_version_version', table_name='versions')
    op.drop_table('versions')
    
    # 删除枚举类型
    versionstatus_enum = postgresql.ENUM('ACTIVE', 'AVAILABLE', 'DEPRECATED', name='versionstatus')
    versionstatus_enum.drop(op.get_bind(), checkfirst=True)

