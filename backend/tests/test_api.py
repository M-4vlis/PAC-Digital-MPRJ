import os, tempfile
from fastapi.testclient import TestClient

TEST_DB = tempfile.NamedTemporaryFile(suffix=".db", delete=False).name
os.environ["DATABASE_URL"] = f"sqlite:///{TEST_DB}"
from app.main import app

def setup_module():
    with TestClient(app): pass

def test_health():
    response = TestClient(app).get("/health")
    assert response.status_code == 200 and response.json()["version"] == "0.8.0"
    assert response.headers["x-content-type-options"] == "nosniff"
    assert TestClient(app).get("/health/ready").json()["status"] == "ready"

def test_dashboard_and_exports():
    client=TestClient(app)
    dashboard = client.get("/api/governance/dashboard").json()
    assert dashboard["demands"] >= 6 and "status_distribution" in dashboard
    assert client.get("/api/exports/demands.csv").text.startswith("code,title")
    assert client.get("/api/exports/demands.json").status_code == 200
    assert client.get("/api/exports/demands.xlsx").headers["content-type"].startswith("application/vnd")

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
    assert readiness.json()["application"] == "ready_for_demonstration"
    assert readiness.json()["external_transmission_enabled"] is False
    integrations = client.get("/api/integrations").json()
    assert {item["id"] for item in integrations} == {"sei", "pncp", "identity"}
    assert all(item["transmission_enabled"] is False for item in integrations)
    events = client.get("/api/audit-events?limit=5").json()
    assert 1 <= len(events) <= 5 and events[0]["demand_code"].startswith("PAC-")
    demands = client.get("/api/demands").json()
    assert all(item["risk"]["level"] in {"low", "medium", "high"} for item in demands)
