"""PNCP public historical intelligence"""
revision = "0004"
down_revision = "0003"
from alembic import op
import sqlalchemy as sa

def upgrade():
    op.create_table("pncp_historical_contracts",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("pncp_control_number", sa.String(80), nullable=False, unique=True),
        sa.Column("purchase_control_number", sa.String(80), nullable=True),
        sa.Column("contract_number", sa.String(80), nullable=True),
        sa.Column("contract_year", sa.Integer(), nullable=False),
        sa.Column("category", sa.String(60), nullable=False),
        sa.Column("category_source", sa.String(120), nullable=True),
        sa.Column("modality", sa.String(120), nullable=True),
        sa.Column("object_description", sa.Text(), nullable=False),
        sa.Column("unit_code", sa.String(60), nullable=True),
        sa.Column("unit_name", sa.String(200), nullable=True),
        sa.Column("initial_value", sa.Numeric(18, 4), nullable=False, server_default="0"),
        sa.Column("signature_date", sa.Date(), nullable=True),
        sa.Column("contract_publication_at", sa.DateTime(), nullable=True),
        sa.Column("purchase_publication_at", sa.DateTime(), nullable=True),
        sa.Column("proposal_opening_at", sa.DateTime(), nullable=True),
        sa.Column("proposal_closing_at", sa.DateTime(), nullable=True),
        sa.Column("public_phase_days", sa.Integer(), nullable=True),
        sa.Column("source_updated_at", sa.DateTime(), nullable=True),
        sa.Column("source_url", sa.String(500), nullable=False),
        sa.Column("source_hash", sa.String(64), nullable=False),
        sa.Column("imported_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_pncp_historical_contracts_pncp_control_number", "pncp_historical_contracts", ["pncp_control_number"])
    op.create_index("ix_pncp_historical_contracts_purchase_control_number", "pncp_historical_contracts", ["purchase_control_number"])
    op.create_index("ix_pncp_historical_contracts_category", "pncp_historical_contracts", ["category"])
    op.create_table("pncp_sync_runs",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("status", sa.String(20), nullable=False, server_default="running"),
        sa.Column("start_year", sa.Integer(), nullable=False),
        sa.Column("end_year", sa.Integer(), nullable=False),
        sa.Column("records_seen", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("inserted", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("updated", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("enriched", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("error", sa.Text(), nullable=True),
        sa.Column("started_at", sa.DateTime(), nullable=False),
        sa.Column("finished_at", sa.DateTime(), nullable=True),
    )

def downgrade():
    op.drop_table("pncp_sync_runs")
    op.drop_index("ix_pncp_historical_contracts_category", table_name="pncp_historical_contracts")
    op.drop_index("ix_pncp_historical_contracts_purchase_control_number", table_name="pncp_historical_contracts")
    op.drop_index("ix_pncp_historical_contracts_pncp_control_number", table_name="pncp_historical_contracts")
    op.drop_table("pncp_historical_contracts")
