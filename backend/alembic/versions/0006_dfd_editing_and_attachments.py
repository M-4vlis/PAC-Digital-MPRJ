"""DFD fields, governed removal and attachments

Revision ID: 0006
Revises: 0005
"""
from alembic import op
import sqlalchemy as sa

revision = "0006"
down_revision = "0005"
branch_labels = None
depends_on = None

def upgrade():
    with op.batch_alter_table("demands") as batch:
        batch.add_column(sa.Column("justification", sa.Text(), nullable=True))
        batch.add_column(sa.Column("quantity", sa.Numeric(17, 4), nullable=False, server_default="1"))
        batch.add_column(sa.Column("unit_measure", sa.String(80), nullable=False, server_default="unidade"))
        batch.add_column(sa.Column("unit_value", sa.Numeric(17, 4), nullable=True))
        batch.add_column(sa.Column("priority", sa.String(20), nullable=False, server_default="medium"))
        batch.add_column(sa.Column("dependency_description", sa.Text(), nullable=True))
        batch.add_column(sa.Column("requester_name", sa.String(160), nullable=True))
        batch.add_column(sa.Column("requester_email", sa.String(240), nullable=True))
        batch.add_column(sa.Column("desired_start_date", sa.Date(), nullable=True))
        batch.add_column(sa.Column("renewal_contract", sa.Boolean(), nullable=False, server_default=sa.false()))
        batch.add_column(sa.Column("pncp_catalog_code", sa.Integer(), nullable=True))
        batch.add_column(sa.Column("pncp_classification", sa.Integer(), nullable=True))
        batch.add_column(sa.Column("pncp_superior_code", sa.String(100), nullable=True))
        batch.add_column(sa.Column("pncp_superior_name", sa.String(255), nullable=True))
        batch.add_column(sa.Column("deleted_at", sa.DateTime(), nullable=True))
        batch.add_column(sa.Column("deletion_reason", sa.Text(), nullable=True))
        batch.add_column(sa.Column("deleted_by_role", sa.String(80), nullable=True))
        batch.create_index("ix_demands_deleted_at", ["deleted_at"])
    op.execute("UPDATE demands SET unit_value = original_value WHERE unit_value IS NULL")
    op.execute("UPDATE demands SET justification = COALESCE(change_justification, 'Necessidade demonstrativa registrada antes da ampliação do DFD.') WHERE justification IS NULL")
    op.execute("UPDATE demands SET requester_name = 'Responsável demonstrativo da unidade' WHERE requester_name IS NULL")
    op.create_table(
        "demand_attachments",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("demand_id", sa.Integer(), sa.ForeignKey("demands.id"), nullable=False),
        sa.Column("document_type", sa.String(40), nullable=False, server_default="dfd"),
        sa.Column("original_name", sa.String(255), nullable=False),
        sa.Column("stored_name", sa.String(255), nullable=False, unique=True),
        sa.Column("content_type", sa.String(120), nullable=False),
        sa.Column("size_bytes", sa.Integer(), nullable=False),
        sa.Column("sha256", sa.String(64), nullable=False),
        sa.Column("uploaded_by_role", sa.String(80), nullable=False, server_default="requesting_unit"),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("deleted_at", sa.DateTime(), nullable=True),
    )
    op.create_index("ix_demand_attachments_demand_id", "demand_attachments", ["demand_id"])

def downgrade():
    op.drop_index("ix_demand_attachments_demand_id", table_name="demand_attachments")
    op.drop_table("demand_attachments")
    with op.batch_alter_table("demands") as batch:
        batch.drop_index("ix_demands_deleted_at")
        for name in ["deleted_by_role","deletion_reason","deleted_at","pncp_superior_name","pncp_superior_code","pncp_classification","pncp_catalog_code","renewal_contract","desired_start_date","requester_email","requester_name","dependency_description","priority","unit_value","unit_measure","quantity","justification"]:
            batch.drop_column(name)
