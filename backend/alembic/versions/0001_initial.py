"""initial PAC domain"""
revision = "0001"
down_revision = None
from alembic import op
import sqlalchemy as sa

def upgrade():
    op.create_table("demands", sa.Column("id", sa.Integer, primary_key=True), sa.Column("code", sa.String(30), nullable=False, unique=True), sa.Column("title", sa.String(240), nullable=False), sa.Column("unit", sa.String(160), nullable=False), sa.Column("category", sa.String(60), nullable=False), sa.Column("status", sa.String(40), nullable=False), sa.Column("execution_status", sa.String(40), nullable=False), sa.Column("desired_date", sa.Date, nullable=False), sa.Column("original_value", sa.Numeric(14,2), nullable=False), sa.Column("revised_value", sa.Numeric(14,2)), sa.Column("adjusted_value", sa.Numeric(14,2)), sa.Column("executed_value", sa.Numeric(14,2), nullable=False, server_default="0"), sa.Column("loa_justification", sa.Text), sa.Column("change_justification", sa.Text), sa.Column("pncp_item_code", sa.String(80)), sa.Column("extraordinary", sa.Boolean, nullable=False, server_default=sa.false()), sa.Column("version", sa.Integer, nullable=False, server_default="1"), sa.Column("created_at", sa.DateTime, nullable=False), sa.Column("updated_at", sa.DateTime, nullable=False))
    op.create_table("demand_versions", sa.Column("id", sa.Integer, primary_key=True), sa.Column("demand_id", sa.Integer, sa.ForeignKey("demands.id"), nullable=False), sa.Column("version", sa.Integer, nullable=False), sa.Column("reason", sa.String(80), nullable=False), sa.Column("payload", sa.Text, nullable=False), sa.Column("created_at", sa.DateTime, nullable=False))
    op.create_table("reviews", sa.Column("id", sa.Integer, primary_key=True), sa.Column("demand_id", sa.Integer, sa.ForeignKey("demands.id"), nullable=False), sa.Column("status", sa.String(20), nullable=False), sa.Column("proposed_title", sa.String(240)), sa.Column("proposed_value", sa.Numeric(14,2)), sa.Column("proposed_date", sa.Date), sa.Column("justification", sa.Text, nullable=False), sa.Column("applied_at", sa.DateTime))
    op.create_table("audit_events", sa.Column("id", sa.Integer, primary_key=True), sa.Column("demand_id", sa.Integer, sa.ForeignKey("demands.id"), nullable=False), sa.Column("action", sa.String(80), nullable=False), sa.Column("actor_role", sa.String(80), nullable=False), sa.Column("detail", sa.Text, nullable=False), sa.Column("created_at", sa.DateTime, nullable=False))

def downgrade():
    op.drop_table("audit_events"); op.drop_table("reviews"); op.drop_table("demand_versions"); op.drop_table("demands")
