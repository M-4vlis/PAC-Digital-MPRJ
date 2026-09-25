import io, json
from contextlib import asynccontextmanager
from datetime import datetime, UTC
from fastapi import Depends, FastAPI, HTTPException, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from openpyxl import Workbook
from sqlalchemy.orm import Session
from .database import Base, engine, get_session
from .models import Demand, DemandVersion, Review
from .schemas import BackplanRequest, DemandCreate, LoaAdjustment, ReviewCreate, SeiLinkRequest, TransitionRequest
from .seed import seed
from .services import EXECUTION_TRANSITIONS, backplan, csv_export, demand_payload, pncp_payload, sei_integration_plan, snapshot

@asynccontextmanager
async def lifespan(_: FastAPI):
    Base.metadata.create_all(bind=engine)
    db = next(get_session())
    try: seed(db)
    finally: db.close()
    yield

app = FastAPI(title="PAC Digital MPRJ", version="0.7.0", description="API demonstrativa; dados estritamente fictícios.", lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=["http://localhost:5173"], allow_methods=["GET", "POST"], allow_headers=["Content-Type"])

def get_demand(db, demand_id):
    demand = db.get(Demand, demand_id)
    if not demand: raise HTTPException(404, "Demanda não encontrada")
    return demand

@app.get("/health")
def health(): return {"status":"ok", "version":"0.7.0", "data_classification":"fictitious_demo"}

@app.get("/api/demands")
def demands(db: Session = Depends(get_session)):
    return [demand_payload(d) for d in db.query(Demand).order_by(Demand.code).all()]

@app.post("/api/demands", status_code=201)
def create_demand(body: DemandCreate, db: Session = Depends(get_session)):
    if body.extraordinary and not body.justification:
        raise HTTPException(422, "Inclusão extraordinária exige justificativa")
    code = f"PAC-{body.desired_date.year}-{db.query(Demand).count() + 1:03d}"
    demand = Demand(code=code, title=body.title, unit=body.unit, category=body.category, desired_date=body.desired_date, original_value=body.original_value, pncp_item_code=body.pncp_item_code, extraordinary=body.extraordinary, change_justification=body.justification, status="draft")
    db.add(demand); db.flush(); snapshot(db, demand, "demand_created", body.justification or "Demanda criada pela interface."); db.commit(); db.refresh(demand)
    return demand_payload(demand)

@app.get("/api/demands/{demand_id}")
def demand(demand_id: int, db: Session = Depends(get_session)):
    return demand_payload(get_demand(db, demand_id))

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
    return {"available": True, "protocol": "SOAP/WSDL", "configured": False, "transmission_enabled": False, "requirements": ["WSDL da instância MPRJ", "cadastro do PAC Digital em Administração > Sistemas", "serviço e operações autorizadas", "chave ou IP liberado", "unidades e tipos de processo/documento permitidos"]}

@app.get("/api/governance/dashboard")
def dashboard(db: Session = Depends(get_session)):
    rows = db.query(Demand).all(); planned = sum(float(x.adjusted_value or x.revised_value or x.original_value) for x in rows); executed = sum(float(x.executed_value) for x in rows)
    altered = sum(1 for x in rows if x.version > 1 or x.revised_value is not None or x.adjusted_value is not None)
    risk = sum(1 for x in rows if x.execution_status in {"not_started","reprogrammed"})
    return {"planned_value":planned,"executed_value":executed,"execution_rate":round(executed/planned*100,2) if planned else 0,"demands":len(rows),"altered_demands":altered,"risk_demands":risk,"extraordinary_inclusions":sum(x.extraordinary for x in rows),"cancelled":sum(x.execution_status=="cancelled" for x in rows),"reprogrammed":sum(x.execution_status=="reprogrammed" for x in rows),"notice":"Indicadores demonstrativos com dados fictícios; não correspondem a execução institucional."}

@app.get("/api/exports/demands.{format}")
def export_demands(format: str, db: Session = Depends(get_session)):
    rows = db.query(Demand).order_by(Demand.code).all()
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
