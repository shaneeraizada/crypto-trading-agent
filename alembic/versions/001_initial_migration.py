# ============================================================================
# alembic/versions/001_initial_migration.py
# ============================================================================
"""Initial migration

Revision ID: 001
Revises: 
Create Date: 2024-01-01 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers
revision: str = '001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create initial tables."""
    
    # Create networks table
    op.create_table(
        'networks',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(50), nullable=False),
        sa.Column('chain_id', sa.Integer(), nullable=True),
        sa.Column('symbol', sa.String(10), nullable=False),
        sa.Column('rpc_url', sa.Text(), nullable=True),
        sa.Column('explorer_url', sa.Text(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('chain_id'),
        sa.UniqueConstraint('name')
    )
    
    # Create tokens table
    op.create_table(
        'tokens',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('address', sa.String(42), nullable=False),
        sa.Column('network_id', sa.Integer(), nullable=False),
        sa.Column('symbol', sa.String(20), nullable=False),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('decimals', sa.Integer(), nullable=False),
        sa.Column('total_supply', sa.Numeric(36, 0), nullable=True),
        sa.Column('is_verified', sa.Boolean(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('metadata', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['network_id'], ['networks.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('address', 'network_id')
    )
    
    # Add more table creations here...
    
    # Create indexes
    op.create_index('idx_tokens_active', 'tokens', ['network_id', 'symbol'], 
                   postgresql_where=sa.text('is_active = true'))


def downgrade() -> None:
    """Drop all tables."""
    op.drop_table('tokens')
    op.drop_table('networks')