"""Create alert_state table for ETAPA 5.3

Revision ID: 003
Revises: 002
Create Date: 2026-01-13

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '003'
down_revision = '002'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create alert_state table for anti-spam persistence."""
    op.create_table(
        'alert_state',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column(
            'alert_type',
            sa.String(length=50),
            nullable=False,
            comment='Unique alert type identifier (e.g., FAILED_THRESHOLD)'
        ),
        sa.Column(
            'is_active',
            sa.Boolean(),
            nullable=False,
            server_default='false',
            comment='True if alert is currently active, False if resolved'
        ),
        sa.Column(
            'last_triggered_at',
            sa.DateTime(timezone=True),
            nullable=True,
            comment='Timestamp when alert was last detected'
        ),
        sa.Column(
            'last_resolved_at',
            sa.DateTime(timezone=True),
            nullable=True,
            comment='Timestamp when alert was last resolved'
        ),
        sa.Column(
            'created_at',
            sa.DateTime(timezone=True),
            server_default=sa.text('now()'),
            nullable=False
        ),
        sa.Column(
            'updated_at',
            sa.DateTime(timezone=True),
            server_default=sa.text('now()'),
            onupdate=sa.text('now()'),
            nullable=False
        ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('alert_type', name='uq_alert_state_alert_type'),
        comment='Stores alert states for anti-spam and reactivation logic'
    )
    
    # Create index on alert_type for fast lookups
    op.create_index(
        'idx_alert_state_alert_type',
        'alert_state',
        ['alert_type'],
        unique=True
    )
    
    # Create index on is_active for filtering active alerts
    op.create_index(
        'idx_alert_state_is_active',
        'alert_state',
        ['is_active']
    )


def downgrade() -> None:
    """Drop alert_state table and indexes."""
    # Drop indexes first
    op.drop_index('idx_alert_state_is_active', table_name='alert_state')
    op.drop_index('idx_alert_state_alert_type', table_name='alert_state')
    
    # Drop table
    op.drop_table('alert_state')
