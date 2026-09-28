"""configurable sequential approval flows"""
revision = "0003"
down_revision = "0002"
from alembic import op
import sqlalchemy as sa

def upgrade():
    op.create_table("approval_flows",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(120), nullable=False, unique=True),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("category", sa.String(60), nullable=True),
        sa.Column("minimum_value", sa.Numeric(14, 2), nullable=True),
        sa.Column("active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )
    op.create_table("approval_steps",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("flow_id", sa.Integer(), sa.ForeignKey("approval_flows.id"), nullable=False),
        sa.Column("position", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(120), nullable=False),
        sa.Column("actor_role", sa.String(80), nullable=False),
    )
    op.create_index("ix_approval_steps_flow_id", "approval_steps", ["flow_id"])
    op.create_table("demand_approvals",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("demand_id", sa.Integer(), sa.ForeignKey("demands.id"), nullable=False),
        sa.Column("flow_id", sa.Integer(), sa.ForeignKey("approval_flows.id"), nullable=False),
        sa.Column("status", sa.String(20), nullable=False, server_default="pending"),
        sa.Column("current_position", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("started_at", sa.DateTime(), nullable=False),
        sa.Column("completed_at", sa.DateTime(), nullable=True),
    )
    op.create_index("ix_demand_approvals_demand_id", "demand_approvals", ["demand_id"])
    op.create_index("ix_demand_approvals_flow_id", "demand_approvals", ["flow_id"])
    op.create_table("approval_decisions",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("approval_id", sa.Integer(), sa.ForeignKey("demand_approvals.id"), nullable=False),
        sa.Column("step_id", sa.Integer(), sa.ForeignKey("approval_steps.id"), nullable=False),
        sa.Column("decision", sa.String(20), nullable=False),
        sa.Column("actor_role", sa.String(80), nullable=False),
        sa.Column("justification", sa.Text(), nullable=True),
        sa.Column("decided_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_approval_decisions_approval_id", "approval_decisions", ["approval_id"])

def downgrade():
    op.drop_index("ix_approval_decisions_approval_id", table_name="approval_decisions")
    op.drop_table("approval_decisions")
    op.drop_index("ix_demand_approvals_flow_id", table_name="demand_approvals")
    op.drop_index("ix_demand_approvals_demand_id", table_name="demand_approvals")
    op.drop_table("demand_approvals")
    op.drop_index("ix_approval_steps_flow_id", table_name="approval_steps")
    op.drop_table("approval_steps")
    op.drop_table("approval_flows")
