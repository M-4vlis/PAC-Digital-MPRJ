import hashlib
import json
from datetime import UTC, date, datetime

from sqlalchemy.orm import Session

from .models import Demand, PublicPacSnapshot
from .services import demand_payload


PUBLIC_FIELDS = (
    "code", "title", "unit", "category", "status", "execution_status",
    "desired_date", "original_value", "revised_value", "adjusted_value",
    "executed_value", "extraordinary", "version",
)


def _canonical_payload(db: Session, year: int):
    rows = db.query(Demand).filter(Demand.deleted_at.is_(None), Demand.desired_date >= date(year, 1, 1), Demand.desired_date <= date(year, 12, 31)).order_by(Demand.code).all()
    demands = [{key: demand_payload(row)[key] for key in PUBLIC_FIELDS} for row in rows]
    planned = sum(float(row.adjusted_value or row.revised_value or row.original_value) for row in rows)
    executed = sum(float(row.executed_value or 0) for row in rows)
    return {
        "schema_version": "1.0", "year": year,
        "organization": "Ministério Público do Estado do Rio de Janeiro",
        "data_classification": "fictitious_demo",
        "summary": {"demands": len(rows), "planned_value": round(planned, 2), "executed_value": round(executed, 2), "execution_rate": round(executed / planned * 100, 2) if planned else 0},
        "demands": demands,
        "notice": "Snapshot demonstrativo, sem dados internos reais. Publicação institucional depende de homologação.",
    }


def publish_snapshot(db: Session, year: int):
    payload = _canonical_payload(db, year)
    canonical = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    digest = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
    existing = db.query(PublicPacSnapshot).filter_by(year=year, content_hash=digest, status="published").first()
    if existing:
        return existing
    latest = db.query(PublicPacSnapshot).filter_by(year=year).order_by(PublicPacSnapshot.version.desc()).first()
    record = PublicPacSnapshot(year=year, version=(latest.version + 1 if latest else 1), payload=canonical, content_hash=digest, published_at=datetime.now(UTC).replace(tzinfo=None))
    db.add(record); db.commit(); db.refresh(record)
    return record


def snapshot_payload(record: PublicPacSnapshot):
    return {"id": record.id, "year": record.year, "version": record.version, "status": record.status, "content_hash": record.content_hash, "published_at": record.published_at.isoformat(), "data": json.loads(record.payload)}
