import os, tempfile, time
import httpx
from fastapi.testclient import TestClient

TEST_DB = tempfile.NamedTemporaryFile(suffix=".db", delete=False).name
os.environ["DATABASE_URL"] = f"sqlite:///{TEST_DB}"
from app.main import app
from app.database import SessionLocal
from app.pncp_history import MPRJ_CNPJ, sync_history

def setup_module():
    with TestClient(app): pass

def test_health():
    response = TestClient(app).get("/health")
    assert response.status_code == 200 and response.json()["version"] == "1.0.0-rc.1"
    assert response.headers["x-content-type-options"] == "nosniff"
    assert response.headers["x-frame-options"] == "DENY"
    assert "default-src 'none'" in response.headers["content-security-policy"]
    assert response.headers["x-request-id"]
    assert TestClient(app).get("/health/ready").json()["status"] == "ready"

def test_dashboard_and_exports():
    client=TestClient(app)
    dashboard = client.get("/api/governance/dashboard").json()
    assert dashboard["demands"] >= 6 and "status_distribution" in dashboard
    assert client.get("/api/exports/demands.csv").text.startswith("code,title")
    assert client.get("/api/exports/demands.json").status_code == 200
    assert client.get("/api/exports/demands.xlsx").headers["content-type"].startswith("application/vnd")
    pdf = client.get("/api/reports/executive.pdf")
    assert pdf.status_code == 200 and pdf.content.startswith(b"%PDF-1.4")
    report = client.get("/api/reports/executive.xlsx")
    assert report.status_code == 200 and report.content.startswith(b"PK")

def test_public_snapshot_is_versioned_and_verifiable():
    client = TestClient(app)
    listing = client.get("/api/public/pac/snapshots?year=2026")
    assert listing.status_code == 200 and listing.json()
    latest = client.get("/api/public/pac/latest?year=2026").json()
    assert latest["version"] >= 1 and len(latest["content_hash"]) == 64
    assert latest["data"]["data_classification"] == "fictitious_demo"
    assert latest["data"]["summary"]["demands"] >= 6
    assert all("sei_process_number" not in item for item in latest["data"]["demands"])

def test_approved_review_creates_version():
    client=TestClient(app); item=client.get("/api/demands").json()[0]
    before=client.get(f"/api/demands/{item['id']}/versions").json()
    review=client.post(f"/api/demands/{item['id']}/reviews",json={"proposed_title":"Objeto revisado fictício","proposed_value":510000,"justification":"Revisão demonstrativa aprovada pela governança."}).json()
    response=client.post(f"/api/reviews/{review['id']}/approve")
    assert response.status_code==200 and response.json()["demand"]["version"]==2
    assert len(client.get(f"/api/demands/{item['id']}/versions").json()) == len(before)+1

def test_loa_backplanning_and_pncp_validation():
    client=TestClient(app); item=client.get("/api/demands").json()[1]
    adjusted=client.post(f"/api/demands/{item['id']}/loa-adjustment",json={"revised_value":230000,"adjusted_value":225000,"justification":"Ajuste fictício posterior à LOA."})
    assert adjusted.status_code==200 and adjusted.json()["adjusted_value"]==225000
    plan=client.post("/api/backplanning",json={"desired_date":"2026-10-01","category":"services"}).json()
    assert plan["milestones"][0]["date"] < plan["desired_date"] and "não representam" in plan["non_normative_notice"]
    pncp=client.get(f"/api/demands/{item['id']}/pncp-payload").json()
    assert pncp["publishable"] is False and pncp["valid"] is True

def test_create_transition_and_sei_staging():
    client=TestClient(app)
    created=client.post("/api/demands",json={"title":"Contratação fictícia criada pela interface","unit":"Unidade Demonstrativa","category":"services","desired_date":"2027-02-01","original_value":150000}).json()
    assert created["status"] == "draft" and created["execution_status"] == "not_started"
    moved=client.post(f"/api/demands/{created['id']}/execution-transition",json={"target":"preparatory"})
    assert moved.status_code == 200 and moved.json()["execution_status"] == "preparatory"
    invalid=client.post(f"/api/demands/{created['id']}/execution-transition",json={"target":"contracted"})
    assert invalid.status_code == 409
    linked=client.post(f"/api/demands/{created['id']}/sei-link",json={"process_number":"20.22.0001.0000010.2027-10"})
    assert linked.status_code == 200 and linked.json()["sei_status"] == "linked_manually"
    plan=client.get(f"/api/demands/{created['id']}/sei-integration-plan").json()
    assert plan["will_transmit"] is False and "WSDL" in plan["notice"]

def test_executive_readiness_integrations_and_audit():
    client = TestClient(app)
    readiness = client.get("/api/system/readiness")
    assert readiness.status_code == 200
    assert readiness.json()["application"] == "ready_for_institutional_validation"
    assert readiness.json()["external_transmission_enabled"] is False
    integrations = client.get("/api/integrations").json()
    assert {item["id"] for item in integrations} == {"sei", "pncp", "identity"}
    assert all(item["transmission_enabled"] is False for item in integrations)
    events = client.get("/api/audit-events?limit=5").json()
    assert 1 <= len(events) <= 5 and events[0]["demand_code"].startswith("PAC-")
    demands = client.get("/api/demands").json()
    assert all(item["risk"]["level"] in {"low", "medium", "high"} for item in demands)

def test_configurable_sequential_approval_flow():
    client = TestClient(app)
    flows = client.get("/api/approval-flows").json()
    standard = next(flow for flow in flows if len(flow["steps"]) == 2)
    demand = client.post("/api/demands", json={"title":"Serviço fictício sujeito a aprovação","unit":"Unidade Demonstrativa","category":"services","desired_date":"2027-06-01","original_value":200000}).json()
    started = client.post(f"/api/demands/{demand['id']}/approvals", json={"flow_id":standard["id"]})
    assert started.status_code == 201 and started.json()["steps"][0]["status"] == "current"
    approval_id = started.json()["id"]
    forbidden = client.post(f"/api/approvals/{approval_id}/decisions", json={"decision":"approve","actor_role":"governance"})
    assert forbidden.status_code == 403
    first = client.post(f"/api/approvals/{approval_id}/decisions", json={"decision":"approve","actor_role":"requesting_unit"})
    assert first.status_code == 200 and first.json()["current_position"] == 2
    final = client.post(f"/api/approvals/{approval_id}/decisions", json={"decision":"approve","actor_role":"governance"})
    assert final.status_code == 200 and final.json()["status"] == "approved"

def test_pncp_public_history_is_restricted_and_explainable():
    contracts = [{
        "numeroControlePNCP": f"{MPRJ_CNPJ}-2-{index:06d}/2025",
        "numeroControlePncpCompra": f"{MPRJ_CNPJ}-1-{index:06d}/2025",
        "numeroContratoEmpenho": str(index), "anoContrato": 2025,
        "categoriaProcesso": {"nome": "Serviços"}, "objetoContrato": f"Contrato público fictício {index}",
        "unidadeOrgao": {"codigoUnidade": "1", "nomeUnidade": "MPRJ"}, "valorInicial": 1000 * index,
        "dataAssinatura": "2025-08-01", "dataPublicacaoPncp": "2025-08-02T10:00:00",
    } for index in range(1, 13)]
    def handler(request: httpx.Request):
        if request.url.path.endswith("/contratos"):
            assert request.url.params["cnpjOrgao"] == MPRJ_CNPJ
            return httpx.Response(200, json={"data": contracts, "totalPaginas": 1})
        return httpx.Response(200, json={"modalidadeNome":"Pregão - Eletrônico","dataPublicacaoPncp":"2025-01-01T10:00:00","dataAberturaProposta":"2025-01-02T10:00:00","dataEncerramentoProposta":"2025-01-15T10:00:00"})
    with SessionLocal() as db, httpx.Client(transport=httpx.MockTransport(handler)) as mocked:
        result = sync_history(db, 2025, 2025, enrich_limit=12, client=mocked, request_delay=0)
    assert result["status"] == "completed" and result["inserted"] == 12 and result["enriched"] == 12
    metrics = TestClient(app).get("/api/pncp/history/metrics").json()
    services = next(item for item in metrics["categories"] if item["category"] == "services")
    assert metrics["source_cnpj"] == MPRJ_CNPJ and services["sample_size"] >= 12
    client = TestClient(app)
    created = client.post("/api/demands", json={"title":"Serviço para risco histórico","unit":"Unidade Demonstrativa","category":"services","desired_date":"2027-09-01","original_value":100000}).json()
    demand = client.get(f"/api/demands/{created['id']}").json()
    assert demand["risk"]["historical_reference"]["sample_size"] >= 12

def test_end_to_end_demand_governance_execution_flow():
    client = TestClient(app)
    created = client.post("/api/demands", json={"title":"Serviço completo de demonstração E2E","unit":"Unidade E2E","category":"services","desired_date":"2027-12-01","original_value":320000,"pncp_item_code":"E2E-001"}).json()
    review = client.post(f"/api/demands/{created['id']}/reviews", json={"proposed_title":"Serviço revisado pela governança E2E","proposed_value":330000,"justification":"Revisão completa para validação ponta a ponta."}).json()
    applied = client.post(f"/api/reviews/{review['id']}/approve")
    assert applied.status_code == 200 and applied.json()["history_preserved"] is True
    flow = next(item for item in client.get("/api/approval-flows").json() if len(item["steps"]) == 2)
    approval = client.post(f"/api/demands/{created['id']}/approvals", json={"flow_id":flow["id"]}).json()
    for role in ("requesting_unit", "governance"):
        decided = client.post(f"/api/approvals/{approval['id']}/decisions", json={"decision":"approve","actor_role":role})
        assert decided.status_code == 200
    assert decided.json()["status"] == "approved"
    assert client.post(f"/api/demands/{created['id']}/execution-transition", json={"target":"preparatory"}).status_code == 200
    assert client.post(f"/api/demands/{created['id']}/sei-link", json={"process_number":"20.22.0001.0000999.2027-10"}).status_code == 200
    assert client.get(f"/api/demands/{created['id']}/pncp-payload").json()["valid"] is True
    assert len(client.get(f"/api/demands/{created['id']}/versions").json()) >= 3

def test_security_limits_and_api_cache_policy():
    client = TestClient(app)
    oversized = client.post("/api/demands", content=b"{}", headers={"content-type":"application/json", "content-length":"1048577"})
    assert oversized.status_code == 413
    response = client.get("/api/demands")
    assert response.headers["cache-control"] == "no-store"
    assert client.get("/api/reports/executive.exe").status_code == 404

def test_read_endpoint_performance_budget():
    client = TestClient(app); samples = []
    for _ in range(25):
        started = time.perf_counter(); response = client.get("/api/governance/dashboard"); samples.append((time.perf_counter() - started) * 1000)
        assert response.status_code == 200
    samples.sort(); p95 = samples[int(len(samples) * .95) - 1]
    assert p95 < 750, f"p95 local acima do orçamento: {p95:.1f} ms"
