"""phase5_customer_experience

Revision ID: a5b6c7d8e9f0
Revises: f1a4e2d3b4c5
Create Date: 2026-11-06 06:10:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


revision: str = 'a5b6c7d8e9f0'
down_revision: Union[str, Sequence[str], None] = 'f1a4e2d3b4c5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Customers enhancements
    with op.batch_alter_table('customers', schema=None) as batch_op:
        batch_op.add_column(sa.Column('preferred_language', sa.String(length=10), server_default='en', nullable=False))
        batch_op.add_column(sa.Column('city', sa.String(length=100), nullable=True))
        batch_op.add_column(sa.Column('pincode', sa.String(length=10), nullable=True))
        batch_op.add_column(sa.Column('state', sa.String(length=50), nullable=True))
        batch_op.add_column(sa.Column('gender', sa.String(length=20), nullable=True))
        batch_op.add_column(sa.Column('tobacco_user', sa.Boolean(), server_default='0', nullable=False))
        batch_op.add_column(sa.Column('onboarding_stage', sa.String(length=50), server_default='discovery', nullable=False))
        batch_op.add_column(sa.Column('active_conversation_id', sa.String(length=36), nullable=True))

    # 2. Customer qualifications enhancements
    with op.batch_alter_table('customer_qualifications', schema=None) as batch_op:
        batch_op.add_column(sa.Column('target_category', sa.String(length=50), server_default='term_life', nullable=False))
        batch_op.add_column(sa.Column('age', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('dependents_count', sa.Integer(), server_default='0', nullable=False))
        batch_op.add_column(sa.Column('has_pre_existing_conditions', sa.Boolean(), server_default='0', nullable=False))
        batch_op.add_column(sa.Column('existing_coverage_amount', sa.Numeric(precision=14, scale=2), server_default='0.00', nullable=False))
        batch_op.add_column(sa.Column('recommended_sum_assured', sa.Numeric(precision=14, scale=2), nullable=True))
        batch_op.add_column(sa.Column('completed_steps_json', sa.JSON(), nullable=True))

    # 3. Conversations enhancements
    with op.batch_alter_table('conversations', schema=None) as batch_op:
        batch_op.add_column(sa.Column('thread_title', sa.String(length=150), server_default='Insurance Advisory Consultation', nullable=False))
        batch_op.add_column(sa.Column('conversation_mode', sa.String(length=30), server_default='general_advisory', nullable=False))
        batch_op.add_column(sa.Column('summary_text', sa.Text(), nullable=True))
        batch_op.add_column(sa.Column('last_turn_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False))

    # 4. Conversation messages enhancements
    with op.batch_alter_table('conversation_messages', schema=None) as batch_op:
        batch_op.add_column(sa.Column('message_type', sa.String(length=30), server_default='text', nullable=False))
        batch_op.add_column(sa.Column('widget_data_json', sa.JSON(), nullable=True))


def downgrade() -> None:
    with op.batch_alter_table('conversation_messages', schema=None) as batch_op:
        batch_op.drop_column('widget_data_json')
        batch_op.drop_column('message_type')

    with op.batch_alter_table('conversations', schema=None) as batch_op:
        batch_op.drop_column('last_turn_at')
        batch_op.drop_column('summary_text')
        batch_op.drop_column('conversation_mode')
        batch_op.drop_column('thread_title')

    with op.batch_alter_table('customer_qualifications', schema=None) as batch_op:
        batch_op.drop_column('completed_steps_json')
        batch_op.drop_column('recommended_sum_assured')
        batch_op.drop_column('existing_coverage_amount')
        batch_op.drop_column('has_pre_existing_conditions')
        batch_op.drop_column('dependents_count')
        batch_op.drop_column('age')
        batch_op.drop_column('target_category')

    with op.batch_alter_table('customers', schema=None) as batch_op:
        batch_op.drop_column('active_conversation_id')
        batch_op.drop_column('onboarding_stage')
        batch_op.drop_column('tobacco_user')
        batch_op.drop_column('gender')
        batch_op.drop_column('state')
        batch_op.drop_column('pincode')
        batch_op.drop_column('city')
        batch_op.drop_column('preferred_language')

