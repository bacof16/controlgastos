"""Add notification tables for ETAPA 1.5

Revision ID: 002
Revises: 001
Create Date: 2026-01-13

"""
from alembic import op

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic
revision = '002'
down_revision = '001'
branch_labels = None
depends_on = None


def upgrade():
    # Create notification_settings table
    op.create_table(
        'notification_settings',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('company_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('telegram_enabled', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('telegram_chat_id', sa.String(), nullable=True),
        sa.Column('email_enabled', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('email_to', sa.String(), nullable=True),
        sa.Column('daily_summary_time', sa.Time(), nullable=False, server_default='08:00:00'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['company_id'], ['companies.id'], ),
        sa.UniqueConstraint('company_id')
    )

    # Create notification_queue table
    op.create_table(
        'notification_queue',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('company_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('notification_date', sa.Date(), nullable=False),
        sa.Column('channel', sa.String(length=50), nullable=False),
        sa.Column('status', sa.String(length=20), nullable=False, server_default='pending'),
        sa.Column('summary_content', sa.Text(), nullable=True),
        sa.Column('sent_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['company_id'], ['companies.id'], )
    )

    # Create indexes
    op.create_index('ix_notification_queue_company_id', 'notification_queue', ['company_id'])
    op.create_index('ix_notification_queue_notification_date', 'notification_queue', ['notification_date'])


def downgrade():
    # Drop indexes
    op.drop_index('ix_notification_queue_notification_date', table_name='notification_queue')
    op.drop_index('ix_notification_queue_company_id', table_name='notification_queue')
    
    # Drop tables
    op.drop_table('notification_queue')
    op.drop_table('notification_settings')
