"""phase4_lead_management

Revision ID: f1a4e2d3b4c5
Revises: eb93f7a5ff1f
Create Date: 2026-11-06 05:35:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f1a4e2d3b4c5'
down_revision: Union[str, Sequence[str], None] = 'eb93f7a5ff1f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Create lead_scoring_rules table
    op.create_table(
        'lead_scoring_rules',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('rule_code', sa.String(length=50), nullable=False),
        sa.Column('category', sa.String(length=50), nullable=False),
        sa.Column('rule_name', sa.String(length=100), nullable=False),
        sa.Column('description', sa.String(length=255), nullable=False),
        sa.Column('point_value', sa.Integer(), nullable=False),
        sa.Column('condition_json', sa.JSON(), nullable=True),
        sa.Column('is_active', sa.Boolean(), server_default=sa.text('1'), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('lead_scoring_rules', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_lead_scoring_rules_rule_code'), ['rule_code'], unique=True)

    # 2. Add columns to prospects table using batch mode for SQLite support
    with op.batch_alter_table('prospects', schema=None) as batch_op:
        batch_op.add_column(sa.Column('assigned_advisor_id', sa.String(length=36), nullable=True))
        batch_op.add_column(sa.Column('assigned_at', sa.DateTime(timezone=True), nullable=True))
        batch_op.add_column(sa.Column('segment', sa.String(length=50), server_default='top_of_funnel', nullable=False))
        batch_op.add_column(sa.Column('last_activity_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False))
        batch_op.add_column(sa.Column('estimated_budget_min', sa.Numeric(precision=12, scale=2), nullable=True))
        batch_op.add_column(sa.Column('estimated_budget_max', sa.Numeric(precision=12, scale=2), nullable=True))
        batch_op.add_column(sa.Column('target_insurance_type', sa.String(length=50), nullable=True))
        batch_op.create_foreign_key('fk_prospects_advisor_id', 'advisors', ['assigned_advisor_id'], ['id'], ondelete='SET NULL')
        batch_op.create_index(batch_op.f('ix_prospects_assigned_advisor_id'), ['assigned_advisor_id'], unique=False)
        batch_op.create_index(batch_op.f('ix_prospects_segment'), ['segment'], unique=False)
        batch_op.create_index(batch_op.f('ix_prospects_last_activity_at'), ['last_activity_at'], unique=False)


def downgrade() -> None:
    with op.batch_alter_table('prospects', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_prospects_last_activity_at'))
        batch_op.drop_index(batch_op.f('ix_prospects_segment'))
        batch_op.drop_index(batch_op.f('ix_prospects_assigned_advisor_id'))
        batch_op.drop_constraint('fk_prospects_advisor_id', type_='foreignkey')
        batch_op.drop_column('target_insurance_type')
        batch_op.drop_column('estimated_budget_max')
        batch_op.drop_column('estimated_budget_min')
        batch_op.drop_column('last_activity_at')
        batch_op.drop_column('segment')
        batch_op.drop_column('assigned_at')
        batch_op.drop_column('assigned_advisor_id')

    with op.batch_alter_table('lead_scoring_rules', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_lead_scoring_rules_rule_code'))

    op.drop_table('lead_scoring_rules')

