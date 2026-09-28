import hashlib
import json
import math
import re
import time
from datetime import UTC, date, datetime

import httpx
from sqlalchemy.orm import Session

from .models import PncpHistoricalContract, PncpSyncRun

MPRJ_CNPJ = "28305936000140"
PNCP_QUERY_BASE = "https://pncp.gov.br/api/consulta/v1"
HEADERS = {"Accept": "application/json", "User-Agent": "PAC-Digital-MPRJ/0.10 (public-open-data)"}

def _datetime(value):
    if not value:
        return None
    return datetime.fromisoformat(str(value).replace("Z", "+00:00")).replace(tzinfo=None)

def _date(value):
    return date.fromisoformat(value[:10]) if value else None

def _category(source: str | None):
    value = (source or "").lower()
    if "obra" in value: return "works"
    if "inform" in value or "tic" in value or "tecnolog" in value: return "it"
    if "compra" in value or "bem" in value: return "goods"
    return "services"

def _hash(payload):
    return hashlib.sha256(json.dumps(payload, sort_keys=True, ensure_ascii=False, default=str).encode("utf-8")).hexdigest()

def _percentile(values: list[int], percentile: float):
    if not values: return None
    ordered = sorted(values)
    return ordered[max(0, math.ceil(percentile * len(ordered)) - 1)]

def _contract_values(item, url):
    category_source = (item.get("categoriaProcesso") or {}).get("nome")
    unit = item.get("unidadeOrgao") or {}
    return {
        "pncp_control_number": item["numeroControlePNCP"],
        "purchase_control_number": item.get("numeroControlePncpCompra") or item.get("numeroControlePNCPCompra"),
        "contract_number": item.get("numeroContratoEmpenho"),
        "contract_year": int(item.get("anoContrato") or 0),
        "category": _category(category_source),
        "category_source": category_source,
        "object_description": item.get("objetoContrato") or "Objeto não informado no PNCP",
        "unit_code": unit.get("codigoUnidade"),
        "unit_name": unit.get("nomeUnidade"),
        "initial_value": item.get("valorInicial") or 0,
        "signature_date": _date(item.get("dataAssinatura")),
        "contract_publication_at": _datetime(item.get("dataPublicacaoPncp")),
        "source_updated_at": _datetime(item.get("dataAtualizacao")),
        "source_url": url,
        "source_hash": _hash(item),
        "imported_at": datetime.now(UTC).replace(tzinfo=None),
    }

def _purchase_reference(control_number: str | None):
    match = re.search(r"-1-(\d+)/(\d{4})$", control_number or "")
    return (int(match.group(2)), int(match.group(1))) if match else None

def _get(client: httpx.Client, url: str, params=None, retries: int = 3):
    response = None
    for attempt in range(retries):
        response = client.get(url, params=params)
        if response.status_code not in {429, 502, 503, 504}: return response
        retry_after = response.headers.get("Retry-After")
        wait = float(retry_after) if retry_after and retry_after.isdigit() else .75 * (attempt + 1)
        time.sleep(min(wait, 5))
    return response

def sync_history(db: Session, start_year: int, end_year: int, enrich_limit: int = 250, client: httpx.Client | None = None, request_delay: float = .25):
    if start_year < 2021 or end_year > datetime.now().year + 1 or start_year > end_year:
        raise ValueError("Intervalo de anos inválido")
    run = PncpSyncRun(start_year=start_year, end_year=end_year)
    db.add(run); db.commit(); db.refresh(run)
    own_client = client is None
    client = client or httpx.Client(timeout=40, follow_redirects=True, headers=HEADERS)
    warnings = []
    try:
        for year in range(start_year, end_year + 1):
            page, total_pages = 1, 1
            while page <= total_pages:
                url = f"{PNCP_QUERY_BASE}/contratos"
                response = _get(client, url, params={"dataInicial": f"{year}0101", "dataFinal": f"{year}1231", "cnpjOrgao": MPRJ_CNPJ, "pagina": page, "tamanhoPagina": 500})
                response.raise_for_status()
                payload = response.json()
                total_pages = int(payload.get("totalPaginas") or 1)
                for item in payload.get("data") or []:
                    run.records_seen += 1
                    values = _contract_values(item, str(response.url))
                    existing = db.query(PncpHistoricalContract).filter_by(pncp_control_number=values["pncp_control_number"]).first()
                    if existing:
                        if existing.source_hash != values["source_hash"]:
                            for key, value in values.items(): setattr(existing, key, value)
                            run.updated += 1
                    else:
                        db.add(PncpHistoricalContract(**values)); run.inserted += 1
                db.commit(); page += 1

        pending = db.query(PncpHistoricalContract).filter(PncpHistoricalContract.purchase_publication_at.is_(None), PncpHistoricalContract.purchase_control_number.is_not(None)).order_by(PncpHistoricalContract.contract_publication_at.desc()).limit(max(0, enrich_limit)).all()
        for record in pending:
            reference = _purchase_reference(record.purchase_control_number)
            if not reference: continue
            purchase_year, sequence = reference
            url = f"{PNCP_QUERY_BASE}/orgaos/{MPRJ_CNPJ}/compras/{purchase_year}/{sequence}"
            response = _get(client, url)
            if response.status_code == 404: continue
            if response.status_code != 200:
                warnings.append(f"{record.purchase_control_number}: HTTP {response.status_code}")
                if response.status_code == 429: break
                continue
            purchase = response.json()
            record.modality = purchase.get("modalidadeNome")
            record.purchase_publication_at = _datetime(purchase.get("dataPublicacaoPncp"))
            record.proposal_opening_at = _datetime(purchase.get("dataAberturaProposta"))
            record.proposal_closing_at = _datetime(purchase.get("dataEncerramentoProposta"))
            if record.purchase_publication_at and record.signature_date:
                days = (record.signature_date - record.purchase_publication_at.date()).days
                record.public_phase_days = days if 0 <= days <= 3000 else None
            run.enriched += 1
            if run.enriched % 25 == 0: db.commit()
            if request_delay: time.sleep(request_delay)
        run.status = "completed_with_warnings" if warnings else "completed"
        run.error = "; ".join(warnings[:20]) or None
        run.finished_at = datetime.now(UTC).replace(tzinfo=None)
        db.commit(); db.refresh(run)
        return sync_run_payload(run)
    except Exception as exc:
        db.rollback()
        run = db.get(PncpSyncRun, run.id)
        run.status = "failed"; run.error = str(exc)[:3000]; run.finished_at = datetime.now(UTC).replace(tzinfo=None)
        db.commit()
        raise
    finally:
        if own_client: client.close()

def sync_run_payload(run: PncpSyncRun):
    return {"id": run.id, "status": run.status, "start_year": run.start_year, "end_year": run.end_year, "records_seen": run.records_seen, "inserted": run.inserted, "updated": run.updated, "enriched": run.enriched, "error": run.error, "started_at": run.started_at.isoformat(), "finished_at": run.finished_at.isoformat() if run.finished_at else None}

def historical_metrics(db: Session):
    records = db.query(PncpHistoricalContract).all()
    runs = db.query(PncpSyncRun).order_by(PncpSyncRun.started_at.desc()).all()
    annual = {}
    categories = {}
    for record in records:
        year = record.contract_publication_at.year if record.contract_publication_at else record.contract_year
        annual[year] = annual.get(year, 0) + 1
        bucket = categories.setdefault(record.category, {"count": 0, "value": 0.0, "durations": []})
        bucket["count"] += 1; bucket["value"] += float(record.initial_value or 0)
        if record.public_phase_days is not None: bucket["durations"].append(record.public_phase_days)
    durations = [record.public_phase_days for record in records if record.public_phase_days is not None]
    def stats(values):
        return {"sample_size": len(values), "p50_days": _percentile(values, .50), "p75_days": _percentile(values, .75), "p90_days": _percentile(values, .90)}
    return {
        "source": "PNCP — dados abertos", "source_cnpj": MPRJ_CNPJ,
        "source_organization": "MINISTERIO PUBLICO DO ESTADO DO RIO DE JANEIRO",
        "records": len(records), "enriched_records": len(durations),
        "initial_value_total": round(sum(float(record.initial_value or 0) for record in records), 2),
        "years": [{"year": year, "records": annual[year]} for year in sorted(annual)],
        "overall": stats(durations),
        "categories": [{"category": key, "records": value["count"], "initial_value_total": round(value["value"], 2), **stats(value["durations"])} for key, value in sorted(categories.items())],
        "last_sync": sync_run_payload(runs[0]) if runs else None,
        "calibration_status": "calibrated" if len(durations) >= 30 else "insufficient_sample",
        "notice": "Referência estatística da fase pública entre publicação da contratação e assinatura. Não representa prazo normativo nem o ciclo preparatório interno do MPRJ.",
    }

def category_benchmarks(db: Session):
    metrics = historical_metrics(db)
    return {item["category"]: item for item in metrics["categories"] if item["sample_size"] >= 10}
