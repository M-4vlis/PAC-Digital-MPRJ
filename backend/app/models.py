from datetime import datetime, UTC
from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column
from .database import Base

def utc_now():
    return datetime.now(UTC).replace(tzinfo=None)

class Demand(Base):
    __tablename__ = "demands"
    id: Mapped[int] = mapped_column(primary_key=True)
    code: Mapped[str] = mapped_column(String(30), unique=True, index=True)
    title: Mapped[str] = mapped_column(String(240))
    unit: Mapped[str] = mapped_column(String(160))
    category: Mapped[str] = mapped_column(String(60))
    status: Mapped[str] = mapped_column(String(40), default="published")
    execution_status: Mapped[str] = mapped_column(String(40), default="not_started")
    desired_date: Mapped[datetime] = mapped_column(Date)
    original_value: Mapped[float] = mapped_column(Numeric(14, 2))
    revised_value: Mapped[float | None] = mapped_column(Numeric(14, 2), nullable=True)
    adjusted_value: Mapped[float | None] = mapped_column(Numeric(14, 2), nullable=True)
    executed_value: Mapped[float] = mapped_column(Numeric(14, 2), default=0)
    loa_justification: Mapped[str | None] = mapped_column(Text, nullable=True)
    change_justification: Mapped[str | None] = mapped_column(Text, nullable=True)
    pncp_item_code: Mapped[str | None] = mapped_column(String(80), nullable=True)
    sei_process_number: Mapped[str | None] = mapped_column(String(40), nullable=True, index=True)
    sei_protocol_id: Mapped[str | None] = mapped_column(String(80), nullable=True)
    sei_status: Mapped[str] = mapped_column(String(30), default="not_linked")
    extraordinary: Mapped[bool] = mapped_column(Boolean, default=False)
    version: Mapped[int] = mapped_column(Integer, default=1)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now, onupdate=utc_now)

class DemandVersion(Base):
    __tablename__ = "demand_versions"
    id: Mapped[int] = mapped_column(primary_key=True)
    demand_id: Mapped[int] = mapped_column(ForeignKey("demands.id"), index=True)
    version: Mapped[int] = mapped_column(Integer)
    reason: Mapped[str] = mapped_column(String(80))
    payload: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now)

class Review(Base):
    __tablename__ = "reviews"
    id: Mapped[int] = mapped_column(primary_key=True)
    demand_id: Mapped[int] = mapped_column(ForeignKey("demands.id"), index=True)
    status: Mapped[str] = mapped_column(String(20), default="pending")
    proposed_title: Mapped[str | None] = mapped_column(String(240), nullable=True)
    proposed_value: Mapped[float | None] = mapped_column(Numeric(14, 2), nullable=True)
    proposed_date: Mapped[datetime | None] = mapped_column(Date, nullable=True)
    justification: Mapped[str] = mapped_column(Text)
    applied_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

class ApprovalFlow(Base):
    __tablename__ = "approval_flows"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(120), unique=True)
    description: Mapped[str] = mapped_column(Text)
    category: Mapped[str | None] = mapped_column(String(60), nullable=True)
    minimum_value: Mapped[float | None] = mapped_column(Numeric(14, 2), nullable=True)
    active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now)

class ApprovalStep(Base):
    __tablename__ = "approval_steps"
    id: Mapped[int] = mapped_column(primary_key=True)
    flow_id: Mapped[int] = mapped_column(ForeignKey("approval_flows.id"), index=True)
    position: Mapped[int] = mapped_column(Integer)
    name: Mapped[str] = mapped_column(String(120))
    actor_role: Mapped[str] = mapped_column(String(80))

class DemandApproval(Base):
    __tablename__ = "demand_approvals"
    id: Mapped[int] = mapped_column(primary_key=True)
    demand_id: Mapped[int] = mapped_column(ForeignKey("demands.id"), index=True)
    flow_id: Mapped[int] = mapped_column(ForeignKey("approval_flows.id"), index=True)
    status: Mapped[str] = mapped_column(String(20), default="pending")
    current_position: Mapped[int] = mapped_column(Integer, default=1)
    started_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

class ApprovalDecision(Base):
    __tablename__ = "approval_decisions"
    id: Mapped[int] = mapped_column(primary_key=True)
    approval_id: Mapped[int] = mapped_column(ForeignKey("demand_approvals.id"), index=True)
    step_id: Mapped[int] = mapped_column(ForeignKey("approval_steps.id"))
    decision: Mapped[str] = mapped_column(String(20))
    actor_role: Mapped[str] = mapped_column(String(80))
    justification: Mapped[str | None] = mapped_column(Text, nullable=True)
    decided_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now)

class AuditEvent(Base):
    __tablename__ = "audit_events"
    id: Mapped[int] = mapped_column(primary_key=True)
    demand_id: Mapped[int] = mapped_column(ForeignKey("demands.id"), index=True)
    action: Mapped[str] = mapped_column(String(80))
    actor_role: Mapped[str] = mapped_column(String(80), default="governance_demo")
    detail: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now)
