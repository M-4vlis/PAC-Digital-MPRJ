import csv, io, json, os
from datetime import date, timedelta
from sqlalchemy.orm import Session
from .models import Demand, DemandVersion, AuditEvent

NON_NORMATIVE_DEFAULTS = {"goods": {"contract": 120, "preparatory": 60}, "services": {"contract": 150, "preparatory": 60}, "works": {"contract": 210, "preparatory": 90}, "it": {"contract": 180, "preparatory": 75}}

def demand_payload(demand: Demand):
    decimal_fields = {"quantity", "unit_value", "original_value", "revised_value", "adjusted_value", "executed_value"}
    values = {
        "id": demand.id, "code": demand.code, "title": demand.title, "unit": demand.unit,
        "justification": demand.justification, "quantity": demand.quantity, "unit_measure": demand.unit_measure,
        "unit_value": demand.unit_value, "priority": demand.priority, "dependency_description": demand.dependency_description,
        "requester_name": demand.requester_name, "requester_email": demand.requester_email,
        "desired_start_date": demand.desired_start_date, "desired_date": demand.desired_date,
        "renewal_contract": demand.renewal_contract, "category": demand.category, "status": demand.status,
        "execution_status": demand.execution_status, "original_value": demand.original_value,
        "revised_value": demand.revised_value, "adjusted_value": demand.adjusted_value,
        "executed_value": demand.executed_value, "loa_justification": demand.loa_justification,
        "change_justification": demand.change_justification, "pncp_item_code": demand.pncp_item_code,
        "pncp_catalog_code": demand.pncp_catalog_code, "pncp_classification": demand.pncp_classification,
        "pncp_superior_code": demand.pncp_superior_code, "pncp_superior_name": demand.pncp_superior_name,
        "sei_process_number": demand.sei_process_number, "sei_protocol_id": demand.sei_protocol_id,
        "sei_status": demand.sei_status, "extraordinary": demand.extraordinary, "version": demand.version,
    }
    return {key: (value.isoformat() if hasattr(value, "isoformat") else float(value) if key in decimal_fields and value is not None else value) for key, value in values.items()}

def snapshot(db: Session, demand: Demand, reason: str, detail: str, actor_role: str = "governance_demo"):
    db.add(DemandVersion(demand_id=demand.id, version=demand.version, reason=reason, payload=json.dumps(demand_payload(demand), ensure_ascii=False)))
    db.add(AuditEvent(demand_id=demand.id, action=reason, actor_role=actor_role, detail=detail))

def backplan(desired_date: date, category: str, parameters: dict | None = None):
    values = dict(NON_NORMATIVE_DEFAULTS.get(category, NON_NORMATIVE_DEFAULTS["services"]))
    if parameters:
        values.update({k: v for k, v in parameters.items() if k in values and isinstance(v, int) and 1 <= v <= 730})
    contract_start = desired_date - timedelta(days=values["contract"])
    preparatory_start = contract_start - timedelta(days=values["preparatory"])
    return {"desired_date": desired_date.isoformat(), "category": category, "parameters": values, "non_normative_notice": "Parâmetros demonstrativos configuráveis; não representam prazos normativos do MPRJ.", "milestones": [{"name": "Início da contratação", "date": contract_start.isoformat()}, {"name": "Início da fase preparatória", "date": preparatory_start.isoformat()}, {"name": "Demanda deve estar validada", "date": (preparatory_start - timedelta(days=15)).isoformat()}]}

def pncp_payload(demand: Demand):
    amount = demand.adjusted_value or demand.revised_value or demand.original_value
    category_codes = {"goods": 1, "services": 2, "works": 3, "it": 2}
    classification = demand.pncp_classification or (1 if demand.category == "goods" else 2)
    unit_code = os.getenv("PNCP_UNIT_CODE")
    item = {
        "numeroItem": demand.id,
        "categoriaItemPca": category_codes.get(demand.category),
        "catalogo": demand.pncp_catalog_code,
        "classificacaoCatalogo": classification,
        "classificacaoSuperiorCodigo": demand.pncp_superior_code,
        "classificacaoSuperiorNome": demand.pncp_superior_name,
        "codigoItem": demand.pncp_item_code,
        "descricao": demand.title,
        "unidadeFornecimento": demand.unit_measure,
        "quantidade": float(demand.quantity or 1),
        "valorUnitario": float(demand.unit_value or amount),
        "valorTotal": float(amount),
        "valorOrcamentoExercicio": float(amount),
        "renovacaoContrato": bool(demand.renewal_contract),
        "dataDesejada": demand.desired_date.isoformat(),
        "unidadeRequisitante": demand.unit,
        "grupoContratacaoCodigo": "",
        "grupoContratacaoNome": demand.dependency_description or "",
    }
    errors = []
    if not unit_code: errors.append("Código PNCP da unidade administrativa não configurado.")
    if not demand.pncp_catalog_code: errors.append("Catálogo PNCP não definido.")
    if not demand.pncp_superior_code or not demand.pncp_superior_name: errors.append("Classe do material ou grupo do serviço não mapeado.")
    if demand.extraordinary and not demand.change_justification: errors.append("inclusão extraordinária exige justificativa.")
    return {"valid": not errors, "publishable": False, "notice": "Estrutura local de pré-validação baseada no Manual de Integração do PNCP v2.6. Não envia dados nem usa credenciais.", "payload": {"codigoUnidade": unit_code, "anoPca": demand.desired_date.year, "itensPlano": [item]}, "errors": errors}

def risk_assessment(demand: Demand, reference_date: date | None = None, historical: dict | None = None):
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
    benchmark = (historical or {}).get(demand.category)
    remaining_days = (demand.desired_date - reference).days
    if benchmark and demand.execution_status in {"not_started", "preparatory", "contracting", "reprogrammed"} and remaining_days >= 0 and remaining_days < benchmark["p75_days"]:
        score += 2
        reasons.append(f"Prazo disponível de {remaining_days} dias abaixo do P75 histórico de {benchmark['p75_days']} dias na fase pública ({benchmark['sample_size']} contratos PNCP do MPRJ).")
    level, label = ("high", "Alto") if score >= 4 else (("medium", "Médio") if score >= 2 else ("low", "Baixo"))
    return {"level": level, "label": label, "score": score, "reasons": reasons or ["Sem alerta relevante pelos parâmetros demonstrativos."], "historical_reference": benchmark}

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
