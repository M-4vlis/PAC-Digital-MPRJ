import csv, io, json, os
from datetime import date, timedelta
from sqlalchemy.orm import Session
from .models import Demand, DemandVersion, AuditEvent

NON_NORMATIVE_DEFAULTS = {"goods": {"contract": 120, "preparatory": 60}, "services": {"contract": 150, "preparatory": 60}, "works": {"contract": 210, "preparatory": 90}, "it": {"contract": 180, "preparatory": 75}}

def demand_payload(demand: Demand):
    return {key: (value.isoformat() if hasattr(value, "isoformat") else float(value) if isinstance(value, (int, float)) is False and value is not None and key.endswith("value") else value) for key, value in {"id": demand.id, "code": demand.code, "title": demand.title, "unit": demand.unit, "category": demand.category, "status": demand.status, "execution_status": demand.execution_status, "desired_date": demand.desired_date, "original_value": demand.original_value, "revised_value": demand.revised_value, "adjusted_value": demand.adjusted_value, "executed_value": demand.executed_value, "loa_justification": demand.loa_justification, "change_justification": demand.change_justification, "pncp_item_code": demand.pncp_item_code, "sei_process_number": demand.sei_process_number, "sei_protocol_id": demand.sei_protocol_id, "sei_status": demand.sei_status, "extraordinary": demand.extraordinary, "version": demand.version}.items()}

def snapshot(db: Session, demand: Demand, reason: str, detail: str):
    db.add(DemandVersion(demand_id=demand.id, version=demand.version, reason=reason, payload=json.dumps(demand_payload(demand), ensure_ascii=False)))
    db.add(AuditEvent(demand_id=demand.id, action=reason, detail=detail))

def backplan(desired_date: date, category: str, parameters: dict | None = None):
    values = dict(NON_NORMATIVE_DEFAULTS.get(category, NON_NORMATIVE_DEFAULTS["services"]))
    if parameters:
        values.update({k: v for k, v in parameters.items() if k in values and isinstance(v, int) and 1 <= v <= 730})
    contract_start = desired_date - timedelta(days=values["contract"])
    preparatory_start = contract_start - timedelta(days=values["preparatory"])
    return {"desired_date": desired_date.isoformat(), "category": category, "parameters": values, "non_normative_notice": "Parâmetros demonstrativos configuráveis; não representam prazos normativos do MPRJ.", "milestones": [{"name": "Início da contratação", "date": contract_start.isoformat()}, {"name": "Início da fase preparatória", "date": preparatory_start.isoformat()}, {"name": "Demanda deve estar validada", "date": (preparatory_start - timedelta(days=15)).isoformat()}]}

def pncp_payload(demand: Demand):
    amount = demand.adjusted_value or demand.revised_value or demand.original_value
    item = {"numeroItem": demand.code, "descricao": demand.title, "categoriaItemPca": demand.category, "quantidadeEstimada": 1, "valorTotalEstimado": float(amount), "valorOrcamentoExercicio": float(amount), "dataDesejada": demand.desired_date.isoformat(), "unidadeRequisitante": demand.unit, "codigoItemCatalogo": demand.pncp_item_code}
    errors = []
    if not demand.pncp_item_code: errors.append("codigoItemCatalogo ausente: completar mapeamento com catálogo PNCP antes de qualquer envio.")
    if demand.extraordinary and not demand.change_justification: errors.append("inclusão extraordinária exige justificativa.")
    return {"valid": not errors, "publishable": False, "notice": "Payload de pré-validação. Não envia dados ao PNCP e não usa credenciais.", "payload": {"anoPca": demand.desired_date.year, "itens": [item]}, "errors": errors}

def risk_assessment(demand: Demand, reference_date: date | None = None):
    reference = reference_date or date.today()
    if demand.execution_status in {"contracted", "cancelled"}:
        return {"level": "low", "label": "Baixo", "reasons": ["Fluxo encerrado."]}
    plan = backplan(demand.desired_date, demand.category)
    preparatory_start = date.fromisoformat(plan["milestones"][1]["date"])
    reasons = []
    score = 0
    if demand.execution_status == "reprogrammed":
        score += 3; reasons.append("Demanda reprogramada.")
    if demand.execution_status == "not_started" and reference >= preparatory_start:
        score += 3; reasons.append("Fase preparatória ainda não iniciada após a data retroplanejada.")
    if not demand.pncp_item_code:
        score += 1; reasons.append("Código de catálogo PNCP pendente.")
    if not demand.sei_process_number and demand.execution_status in {"preparatory", "contracting"}:
        score += 1; reasons.append("Processo SEI ainda não vinculado.")
    if demand.desired_date < reference and demand.execution_status not in {"contracted", "cancelled"}:
        score += 2; reasons.append("Data desejada já ultrapassada.")
    level, label = ("high", "Alto") if score >= 4 else (("medium", "Médio") if score >= 2 else ("low", "Baixo"))
    return {"level": level, "label": label, "score": score, "reasons": reasons or ["Sem alerta relevante pelos parâmetros demonstrativos."]}

def integration_catalog():
    sei_wsdl = bool(os.getenv("SEI_WSDL_URL"))
    sei_key = bool(os.getenv("SEI_SERVICE_KEY"))
    pncp_base = bool(os.getenv("PNCP_API_BASE_URL"))
    pncp_key = bool(os.getenv("PNCP_API_TOKEN"))
    return [
        {
            "id": "sei", "name": "SEI!", "protocol": "SOAP/WSDL",
            "status": "configured" if sei_wsdl and sei_key else "staging",
            "configured": sei_wsdl and sei_key, "transmission_enabled": False,
            "requirements": ["WSDL da instância MPRJ", "serviço e operações autorizadas", "chave de acesso ou IP liberado"],
            "notice": "Adaptador preparado. Nenhuma chamada externa é feita nesta versão.",
        },
        {
            "id": "pncp", "name": "PCA/PNCP", "protocol": "REST/JSON",
            "status": "configured" if pncp_base and pncp_key else "staging",
            "configured": pncp_base and pncp_key, "transmission_enabled": False,
            "requirements": ["homologação do payload", "credencial institucional", "mapeamento do catálogo"],
            "notice": "Geração e validação local habilitadas; publicação externa bloqueada.",
        },
        {
            "id": "identity", "name": "Identidade institucional", "protocol": "OIDC/LDAP",
            "status": "configured" if os.getenv("OIDC_ISSUER_URL") else "planned",
            "configured": bool(os.getenv("OIDC_ISSUER_URL")), "transmission_enabled": False,
            "requirements": ["issuer institucional", "client id", "mapeamento de grupos e unidades"],
            "notice": "Ponto de integração desacoplado; o provedor institucional ainda não foi informado.",
        },
    ]

def csv_export(demands):
    output = io.StringIO(); fields = ["code", "title", "unit", "category", "status", "execution_status", "original_value", "revised_value", "adjusted_value", "executed_value"]
    writer = csv.DictWriter(output, fieldnames=fields); writer.writeheader()
    for demand in demands:
        writer.writerow({f: demand_payload(demand).get(f) for f in fields})
    return output.getvalue()

EXECUTION_TRANSITIONS = {
    "not_started": {"preparatory", "reprogrammed", "cancelled"},
    "preparatory": {"contracting", "reprogrammed", "cancelled"},
    "contracting": {"contracted", "reprogrammed", "cancelled"},
    "reprogrammed": {"preparatory", "cancelled"},
    "contracted": set(), "cancelled": set(),
}

def sei_integration_plan(demand: Demand):
    wsdl = os.getenv("SEI_WSDL_URL")
    return {
        "enabled": bool(wsdl and os.getenv("SEI_SERVICE_KEY")),
        "mode": "configured" if wsdl else "staging",
        "wsdl_configured": bool(wsdl),
        "credentials_configured": bool(os.getenv("SEI_SERVICE_KEY")),
        "will_transmit": False,
        "demand": {"code": demand.code, "title": demand.title, "unit": demand.unit, "process_number": demand.sei_process_number},
        "required_sei_permissions": ["consultar processo", "gerar processo", "incluir documento"],
        "candidate_operations": ["consultarProcedimento", "gerarProcedimento", "incluirDocumento"],
        "notice": "Operações devem ser confirmadas no WSDL e liberadas pela administração do SEI do MPRJ antes da homologação.",
    }
