import hashlib, io, json, os, uuid
from contextlib import asynccontextmanager
from datetime import datetime, UTC
from pathlib import Path
from fastapi import Depends, FastAPI, File, Header, HTTPException, Response, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, StreamingResponse
from openpyxl import Workbook
from sqlalchemy import text
from sqlalchemy.orm import Session
from .database import Base, engine, get_session
from .models import ApprovalDecision, ApprovalFlow, ApprovalStep, AuditEvent, Demand, DemandApproval, DemandAttachment, DemandVersion, PublicPacSnapshot, Review
from .schemas import ApprovalDecisionCreate, ApprovalStart, BackplanRequest, DemandCreate, DemandDelete, DemandUpdate, LoaAdjustment, ReviewCreate, SeiLinkRequest, TransitionRequest
from .seed import seed
from .services import EXECUTION_TRANSITIONS, backplan, csv_export, demand_payload, integration_catalog, pncp_payload, risk_assessment, sei_integration_plan, snapshot
from .pncp_history import category_benchmarks, historical_metrics
from .public_snapshot import snapshot_payload
from .reports import executive_pdf, executive_xlsx

@asynccontextmanager
async def lifespan(_: FastAPI):
    Base.metadata.create_all(bind=engine)
    db = next(get_session())
    try: seed(db)
    finally: db.close()
    yield

app = FastAPI(title="PAC Digital MPRJ", version="1.0.0-rc.2", description="Candidata v1 do PAC Digital MPRJ para demonstração e homologação institucional.", lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=["http://localhost:5173"], allow_methods=["GET", "POST", "PATCH", "DELETE"], allow_headers=["Content-Type", "X-Actor-Role"])

UPLOAD_DIR = Path(os.getenv("UPLOAD_DIR", Path(__file__).resolve().parents[1] / "data" / "uploads"))
ALLOWED_DFD_TYPES = {"application/pdf": ".pdf", "application/msword": ".doc", "application/vnd.openxmlformats-officedocument.wordprocessingml.document": ".docx"}
ALLOWED_DEMAND_ROLES = {"requesting_unit", "governance"}

@app.middleware("http")
async def security_headers(request, call_next):
    content_length = request.headers.get("content-length")
    try: requested_size = int(content_length) if content_length else 0
    except ValueError: return Response(content="Content-Length inválido.", status_code=400, media_type="text/plain")
    size_limit = 10_485_760 if request.url.path.endswith("/attachments") else 1_048_576
    if requested_size > size_limit: return Response(content="Requisição excede o limite permitido.", status_code=413, media_type="text/plain")
    response = await call_next(request)
    response.headers["X-Request-ID"] = request.headers.get("X-Request-ID", str(uuid.uuid4()))[:128]
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "no-referrer"
    response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
    response.headers["Content-Security-Policy"] = "default-src 'none'; frame-ancestors 'none'; base-uri 'none'"
    if request.url.path.startswith("/api/"): response.headers["Cache-Control"] = "no-store"
    return response

def get_demand(db, demand_id):
    demand = db.get(Demand, demand_id)
    if not demand or demand.deleted_at is not None: raise HTTPException(404, "Demanda não encontrada")
    return demand

def require_demand_role(x_actor_role: str = Header(default="requesting_unit")):
    if x_actor_role not in ALLOWED_DEMAND_ROLES: raise HTTPException(403, "Perfil não autorizado")
    return x_actor_role

@app.get("/health")
def health(): return {"status":"ok", "version":"1.0.0-rc.2", "data_classification":"fictitious_demo_with_public_pncp_history"}

@app.get("/health/ready")
def readiness(db: Session = Depends(get_session)):
    db.execute(text("SELECT 1"))
    return {"status": "ready", "database": "available", "version": "1.0.0-rc.2"}

@app.get("/api/public/pac/snapshots")
def public_snapshots(year: int | None = None, db: Session = Depends(get_session)):
    query = db.query(PublicPacSnapshot).filter_by(status="published")
    if year is not None: query = query.filter_by(year=year)
    rows = query.order_by(PublicPacSnapshot.year.desc(), PublicPacSnapshot.version.desc()).all()
    return [{"id": row.id, "year": row.year, "version": row.version, "content_hash": row.content_hash, "published_at": row.published_at.isoformat()} for row in rows]

@app.get("/api/public/pac/latest")
def latest_public_snapshot(year: int = 2026, db: Session = Depends(get_session)):
    row = db.query(PublicPacSnapshot).filter_by(year=year, status="published").order_by(PublicPacSnapshot.version.desc()).first()
    if not row: raise HTTPException(404, "Snapshot público não encontrado")
    return snapshot_payload(row)

def approval_payload(db: Session, approval: DemandApproval):
    demand = db.get(Demand, approval.demand_id)
    flow = db.get(ApprovalFlow, approval.flow_id)
    steps = db.query(ApprovalStep).filter_by(flow_id=approval.flow_id).order_by(ApprovalStep.position).all()
    decisions = db.query(ApprovalDecision).filter_by(approval_id=approval.id).order_by(ApprovalDecision.decided_at).all()
    decided = {item.step_id: item for item in decisions}
    return {
        "id": approval.id, "status": approval.status, "current_position": approval.current_position,
        "demand_id": demand.id, "demand_code": demand.code, "demand_title": demand.title,
        "flow_id": flow.id, "flow_name": flow.name,
        "started_at": approval.started_at.isoformat(), "completed_at": approval.completed_at.isoformat() if approval.completed_at else None,
        "steps": [{"id": step.id, "position": step.position, "name": step.name, "actor_role": step.actor_role,
                   "status": "approved" if step.id in decided and decided[step.id].decision == "approve" else "rejected" if step.id in decided else "current" if approval.status == "pending" and step.position == approval.current_position else "pending"}
                  for step in steps],
    }

@app.get("/api/approval-flows")
def approval_flows(db: Session = Depends(get_session)):
    flows = db.query(ApprovalFlow).filter_by(active=True).order_by(ApprovalFlow.id).all()
    return [{"id": flow.id, "name": flow.name, "description": flow.description, "category": flow.category,
             "minimum_value": float(flow.minimum_value) if flow.minimum_value is not None else None,
             "steps": [{"position": step.position, "name": step.name, "actor_role": step.actor_role} for step in db.query(ApprovalStep).filter_by(flow_id=flow.id).order_by(ApprovalStep.position).all()],
             "non_normative_notice": "Fluxo demonstrativo configurável; autoridades e alçadas dependem de homologação institucional."} for flow in flows]

@app.get("/api/approvals")
def approvals(status: str | None = None, db: Session = Depends(get_session)):
    query = db.query(DemandApproval)
    if status: query = query.filter_by(status=status)
    return [approval_payload(db, item) for item in query.order_by(DemandApproval.started_at.desc()).all()]

@app.post("/api/demands/{demand_id}/approvals", status_code=201)
def start_approval(demand_id: int, body: ApprovalStart, db: Session = Depends(get_session)):
    demand = get_demand(db, demand_id)
    flow = db.get(ApprovalFlow, body.flow_id)
    if not flow or not flow.active: raise HTTPException(404, "Fluxo de aprovação não encontrado")
    if db.query(DemandApproval).filter_by(demand_id=demand.id, status="pending").first(): raise HTTPException(409, "Demanda já possui aprovação pendente")
    if flow.category and flow.category != demand.category: raise HTTPException(422, "Fluxo não se aplica à categoria da demanda")
    amount = float(demand.adjusted_value or demand.revised_value or demand.original_value)
    if flow.minimum_value is not None and amount < float(flow.minimum_value): raise HTTPException(422, "Demanda abaixo da alçada mínima configurada")
    approval = DemandApproval(demand_id=demand.id, flow_id=flow.id)
    db.add(approval); db.flush()
    db.add(AuditEvent(demand_id=demand.id, action="approval_started", detail=f"Fluxo '{flow.name}' iniciado em modo demonstrativo."))
    db.commit(); db.refresh(approval)
    return approval_payload(db, approval)

@app.post("/api/approvals/{approval_id}/decisions")
def decide_approval(approval_id: int, body: ApprovalDecisionCreate, db: Session = Depends(get_session)):
    approval = db.get(DemandApproval, approval_id)
    if not approval: raise HTTPException(404, "Aprovação não encontrada")
    if approval.status != "pending": raise HTTPException(409, "Aprovação já foi encerrada")
    step = db.query(ApprovalStep).filter_by(flow_id=approval.flow_id, position=approval.current_position).first()
    if not step: raise HTTPException(409, "Etapa atual inválida")
    if body.actor_role != step.actor_role: raise HTTPException(403, "Perfil não autorizado para a etapa atual")
    if body.decision == "reject" and (not body.justification or len(body.justification.strip()) < 10): raise HTTPException(422, "Rejeição exige justificativa")
    db.add(ApprovalDecision(approval_id=approval.id, step_id=step.id, decision=body.decision, actor_role=body.actor_role, justification=body.justification))
    demand = get_demand(db, approval.demand_id)
    if body.decision == "reject":
        approval.status = "rejected"; approval.completed_at = datetime.now(UTC).replace(tzinfo=None)
    else:
        next_step = db.query(ApprovalStep).filter_by(flow_id=approval.flow_id, position=approval.current_position + 1).first()
        if next_step: approval.current_position += 1
        else: approval.status = "approved"; approval.completed_at = datetime.now(UTC).replace(tzinfo=None)
    db.add(AuditEvent(demand_id=demand.id, action=f"approval_{body.decision}", actor_role=body.actor_role, detail=body.justification or f"Etapa '{step.name}' aprovada."))
    db.commit(); db.refresh(approval)
    return approval_payload(db, approval)

@app.get("/api/demands")
def demands(db: Session = Depends(get_session)):
    benchmarks = category_benchmarks(db)
    rows = db.query(Demand).filter(Demand.deleted_at.is_(None)).order_by(Demand.code).all()
    return [{**demand_payload(d), "risk": risk_assessment(d, historical=benchmarks)} for d in rows]

@app.post("/api/demands", status_code=201)
def create_demand(body: DemandCreate, db: Session = Depends(get_session), actor_role: str = Depends(require_demand_role)):
    code = f"PAC-{body.desired_date.year}-{db.query(Demand).count() + 1:03d}"
    values = body.model_dump(exclude={"extraordinary_justification"})
    demand = Demand(code=code, **values, change_justification=body.extraordinary_justification, status="draft")
    db.add(demand); db.flush(); snapshot(db, demand, "demand_created", "DFD registrado pela unidade requisitante.", actor_role=actor_role); db.commit(); db.refresh(demand)
    return demand_payload(demand)

@app.patch("/api/demands/{demand_id}")
def update_demand(demand_id: int, body: DemandUpdate, db: Session = Depends(get_session), actor_role: str = Depends(require_demand_role)):
    demand = get_demand(db, demand_id)
    if actor_role == "requesting_unit" and (demand.status != "draft" or demand.execution_status != "not_started"):
        raise HTTPException(409, "Após o envio para governança, alterações devem seguir o fluxo formal de revisão")
    values = body.model_dump(exclude={"change_justification"})
    for key, value in values.items(): setattr(demand, key, value)
    demand.version += 1; demand.change_justification = body.change_justification
    snapshot(db, demand, "demand_updated", body.change_justification, actor_role=actor_role)
    db.commit(); db.refresh(demand)
    return demand_payload(demand)

@app.delete("/api/demands/{demand_id}", status_code=204)
def delete_demand(demand_id: int, body: DemandDelete, db: Session = Depends(get_session), actor_role: str = Depends(require_demand_role)):
    demand = get_demand(db, demand_id)
    if actor_role == "requesting_unit" and (demand.status != "draft" or demand.execution_status != "not_started"):
        raise HTTPException(409, "Após o envio para governança, a retirada deve seguir o fluxo formal de cancelamento")
    snapshot(db, demand, "demand_removed", body.justification, actor_role=actor_role)
    demand.deleted_at = datetime.now(UTC).replace(tzinfo=None); demand.deletion_reason = body.justification; demand.deleted_by_role = actor_role
    db.commit()
    return Response(status_code=204)

@app.get("/api/demands/{demand_id}/attachments")
def demand_attachments(demand_id: int, db: Session = Depends(get_session)):
    get_demand(db, demand_id)
    rows = db.query(DemandAttachment).filter_by(demand_id=demand_id, deleted_at=None).order_by(DemandAttachment.created_at.desc()).all()
    return [{"id": x.id, "document_type": x.document_type, "name": x.original_name, "content_type": x.content_type, "size_bytes": x.size_bytes, "created_at": x.created_at.isoformat()} for x in rows]

@app.post("/api/demands/{demand_id}/attachments", status_code=201)
async def upload_demand_attachment(demand_id: int, file: UploadFile = File(...), db: Session = Depends(get_session), actor_role: str = Depends(require_demand_role)):
    demand = get_demand(db, demand_id)
    content_type = file.content_type or "application/octet-stream"
    if content_type not in ALLOWED_DFD_TYPES: raise HTTPException(415, "DFD deve estar em PDF, DOC ou DOCX")
    content = await file.read(8_388_609)
    if not content: raise HTTPException(422, "Arquivo vazio")
    if len(content) > 8_388_608: raise HTTPException(413, "DFD excede o limite de 8 MiB")
    signatures = {
        "application/pdf": lambda data: data.startswith(b"%PDF-"),
        "application/msword": lambda data: data.startswith(bytes.fromhex("D0CF11E0A1B11AE1")),
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document": lambda data: data.startswith(b"PK"),
    }
    if not signatures[content_type](content): raise HTTPException(422, "Conteúdo do arquivo não corresponde ao formato declarado")
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    stored_name = f"{uuid.uuid4().hex}{ALLOWED_DFD_TYPES[content_type]}"
    (UPLOAD_DIR / stored_name).write_bytes(content)
    row = DemandAttachment(demand_id=demand.id, original_name=(Path(file.filename or "DFD").name[:255]), stored_name=stored_name, content_type=content_type, size_bytes=len(content), sha256=hashlib.sha256(content).hexdigest(), uploaded_by_role=actor_role)
    db.add(row); db.flush(); db.add(AuditEvent(demand_id=demand.id, action="dfd_attached", actor_role=actor_role, detail=f"DFD anexado: {row.original_name}.")); db.commit(); db.refresh(row)
    return {"id": row.id, "name": row.original_name, "content_type": row.content_type, "size_bytes": row.size_bytes, "created_at": row.created_at.isoformat()}

@app.get("/api/demands/{demand_id}/attachments/{attachment_id}")
def download_demand_attachment(demand_id: int, attachment_id: int, db: Session = Depends(get_session)):
    get_demand(db, demand_id)
    row = db.query(DemandAttachment).filter_by(id=attachment_id, demand_id=demand_id, deleted_at=None).first()
    if not row: raise HTTPException(404, "Documento não encontrado")
    path = UPLOAD_DIR / row.stored_name
    if not path.is_file(): raise HTTPException(410, "Documento indisponível no armazenamento")
    return FileResponse(path, media_type=row.content_type, filename=row.original_name)

@app.get("/api/demands/{demand_id}")
def demand(demand_id: int, db: Session = Depends(get_session)):
    item = get_demand(db, demand_id)
    return {**demand_payload(item), "risk": risk_assessment(item, historical=category_benchmarks(db))}

@app.get("/api/pncp/history/metrics")
def pncp_history_metrics(db: Session = Depends(get_session)):
    return historical_metrics(db)

@app.get("/api/demands/{demand_id}/versions")
def versions(demand_id: int, db: Session = Depends(get_session)):
    get_demand(db, demand_id)
    rows = db.query(DemandVersion).filter_by(demand_id=demand_id).order_by(DemandVersion.version).all()
    return [{"version":x.version,"reason":x.reason,"payload":json.loads(x.payload),"created_at":x.created_at.isoformat()} for x in rows]

@app.post("/api/demands/{demand_id}/reviews", status_code=201)
def create_review(demand_id: int, body: ReviewCreate, db: Session = Depends(get_session)):
    get_demand(db, demand_id)
    review = Review(demand_id=demand_id, **body.model_dump()); db.add(review); db.commit(); db.refresh(review)
    return {"id":review.id,"status":review.status}

@app.post("/api/reviews/{review_id}/approve")
def approve_review(review_id: int, db: Session = Depends(get_session)):
    review = db.get(Review, review_id)
    if not review: raise HTTPException(404, "Revisão não encontrada")
    if review.status != "pending": raise HTTPException(409, "Revisão já foi decidida")
    demand = get_demand(db, review.demand_id)
    if review.proposed_title: demand.title = review.proposed_title
    if review.proposed_value is not None: demand.revised_value = review.proposed_value
    if review.proposed_date: demand.desired_date = review.proposed_date
    demand.version += 1; demand.change_justification = review.justification
    review.status = "approved"; review.applied_at = datetime.now(UTC).replace(tzinfo=None)
    snapshot(db, demand, "approved_review_applied", review.justification); db.commit()
    return {"review_id":review.id,"demand":demand_payload(demand),"history_preserved":True}

@app.post("/api/demands/{demand_id}/loa-adjustment")
def loa_adjustment(demand_id: int, body: LoaAdjustment, db: Session = Depends(get_session)):
    demand = get_demand(db, demand_id)
    demand.revised_value = body.revised_value; demand.adjusted_value = body.adjusted_value; demand.loa_justification = body.justification; demand.version += 1
    snapshot(db, demand, "post_loa_adjustment", body.justification); db.commit()
    return demand_payload(demand)

@app.post("/api/backplanning")
def calculate_backplanning(body: BackplanRequest):
    return backplan(body.desired_date, body.category, body.parameters)

@app.post("/api/demands/{demand_id}/execution-transition")
def transition_execution(demand_id: int, body: TransitionRequest, db: Session = Depends(get_session)):
    demand = get_demand(db, demand_id)
    allowed = EXECUTION_TRANSITIONS.get(demand.execution_status, set())
    if body.target not in allowed:
        raise HTTPException(409, f"Transição {demand.execution_status} → {body.target} não permitida")
    if body.target in {"reprogrammed", "cancelled"} and not body.justification:
        raise HTTPException(422, "Justificativa obrigatória para reprogramação ou cancelamento")
    demand.execution_status = body.target
    if body.justification: demand.change_justification = body.justification
    snapshot(db, demand, "execution_transition", f"Situação alterada para {body.target}. {body.justification or ''}".strip()); db.commit()
    return demand_payload(demand)

@app.post("/api/demands/{demand_id}/sei-link")
def link_sei(demand_id: int, body: SeiLinkRequest, db: Session = Depends(get_session)):
    demand = get_demand(db, demand_id)
    demand.sei_process_number = body.process_number; demand.sei_protocol_id = body.protocol_id; demand.sei_status = "linked_manually"
    snapshot(db, demand, "sei_process_linked", f"Vínculo demonstrativo ao processo SEI {body.process_number}."); db.commit()
    return demand_payload(demand)

@app.get("/api/demands/{demand_id}/sei-integration-plan")
def sei_plan(demand_id: int, db: Session = Depends(get_session)):
    return sei_integration_plan(get_demand(db, demand_id))

@app.get("/api/integrations/sei/status")
def sei_status():
    return next(item for item in integration_catalog() if item["id"] == "sei")

@app.get("/api/integrations")
def integrations():
    return integration_catalog()

@app.get("/api/system/readiness")
def system_readiness(db: Session = Depends(get_session)):
    db.execute(text("SELECT 1"))
    catalog = integration_catalog()
    return {
        "version": "1.0.0-rc.2", "application": "ready_for_institutional_validation", "database": "available",
        "data_classification": "fictitious_demo", "external_transmission_enabled": False,
        "integrations": {item["id"]: item["status"] for item in catalog},
        "institutional_dependencies": ["provedor de identidade", "autorização e WSDL do SEI-MPRJ", "homologação e credenciais do PNCP"],
    }

@app.get("/api/audit-events")
def audit_events(limit: int = 50, db: Session = Depends(get_session)):
    safe_limit = max(1, min(limit, 200))
    rows = db.query(AuditEvent).order_by(AuditEvent.created_at.desc(), AuditEvent.id.desc()).limit(safe_limit).all()
    demands = {d.id: d.code for d in db.query(Demand).filter(Demand.id.in_({row.demand_id for row in rows})).all()} if rows else {}
    return [{"id": row.id, "demand_id": row.demand_id, "demand_code": demands.get(row.demand_id), "action": row.action, "actor_role": row.actor_role, "detail": row.detail, "created_at": row.created_at.isoformat()} for row in rows]

@app.get("/api/governance/dashboard")
def dashboard(db: Session = Depends(get_session)):
    rows = db.query(Demand).filter(Demand.deleted_at.is_(None)).all(); planned = sum(float(x.adjusted_value or x.revised_value or x.original_value) for x in rows); executed = sum(float(x.executed_value) for x in rows)
    altered = sum(1 for x in rows if x.version > 1 or x.revised_value is not None or x.adjusted_value is not None)
    benchmarks = category_benchmarks(db)
    risks = [risk_assessment(x, historical=benchmarks) for x in rows]
    risk = sum(item["level"] == "high" for item in risks)
    status_distribution = {status: sum(x.execution_status == status for x in rows) for status in EXECUTION_TRANSITIONS}
    return {"planned_value":planned,"executed_value":executed,"execution_rate":round(executed/planned*100,2) if planned else 0,"demands":len(rows),"altered_demands":altered,"risk_demands":risk,"medium_risk_demands":sum(item["level"] == "medium" for item in risks),"extraordinary_inclusions":sum(x.extraordinary for x in rows),"cancelled":sum(x.execution_status=="cancelled" for x in rows),"reprogrammed":sum(x.execution_status=="reprogrammed" for x in rows),"status_distribution":status_distribution,"notice":"Indicadores demonstrativos com dados fictícios; não correspondem a execução institucional."}

@app.get("/api/reports/executive.{format}")
def executive_report(format: str, db: Session = Depends(get_session)):
    rows = db.query(Demand).filter(Demand.deleted_at.is_(None)).order_by(Demand.code).all(); metrics = dashboard(db)
    if format == "pdf": return Response(executive_pdf(metrics, rows), media_type="application/pdf", headers={"Content-Disposition":"attachment; filename=PAC-Digital-MPRJ-Relatorio-Executivo.pdf"})
    if format == "xlsx": return Response(executive_xlsx(metrics, rows), media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", headers={"Content-Disposition":"attachment; filename=PAC-Digital-MPRJ-Relatorio-Executivo.xlsx"})
    raise HTTPException(404, "Formato suportado: pdf, xlsx")

@app.get("/api/exports/demands.{format}")
def export_demands(format: str, db: Session = Depends(get_session)):
    rows = db.query(Demand).filter(Demand.deleted_at.is_(None)).order_by(Demand.code).all()
    if format == "json": return [demand_payload(x) for x in rows]
    if format == "csv": return Response(csv_export(rows), media_type="text/csv; charset=utf-8", headers={"Content-Disposition":"attachment; filename=PAC-Digital-MPRJ.csv"})
    if format == "xlsx":
        book=Workbook(); sheet=book.active; sheet.title="Demandas"
        columns=["Código","Objeto","Unidade","Categoria","Planejado","Executado","Execução"]
        sheet.append(columns)
        for x in rows: sheet.append([x.code,x.title,x.unit,x.category,float(x.adjusted_value or x.revised_value or x.original_value),float(x.executed_value),x.execution_status])
        stream=io.BytesIO(); book.save(stream); stream.seek(0)
        return StreamingResponse(stream, media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", headers={"Content-Disposition":"attachment; filename=PAC-Digital-MPRJ.xlsx"})
    raise HTTPException(404, "Formato suportado: csv, json, xlsx")

@app.get("/api/demands/{demand_id}/pncp-payload")
def validate_pncp(demand_id: int, db: Session = Depends(get_session)):
    return pncp_payload(get_demand(db, demand_id))
