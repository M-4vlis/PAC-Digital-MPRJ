from datetime import date
from sqlalchemy.orm import Session
from .models import ApprovalDecision, ApprovalFlow, ApprovalStep, Demand, DemandApproval
from .services import snapshot

DEMO = [
 {"code":"PAC-2026-001","title":"Manutenção preventiva de sistemas de climatização","unit":"Diretoria de Operação e Manutenção","category":"services","desired_date":date(2026,8,1),"original_value":480000,"revised_value":495000,"adjusted_value":492000,"executed_value":492000,"loa_justification":"Adequação demonstrativa após aprovação da LOA.","execution_status":"contracted","pncp_item_code":"DEMO-001"},
 {"code":"PAC-2026-002","title":"Aquisição de materiais elétricos","unit":"Diretoria de Operação e Manutenção","category":"goods","desired_date":date(2026,7,15),"original_value":220000,"executed_value":120000,"execution_status":"preparatory","pncp_item_code":"DEMO-002"},
 {"code":"PAC-2026-003","title":"Modernização de rede lógica predial","unit":"Diretoria de Tecnologia da Informação","category":"it","desired_date":date(2026,10,1),"original_value":750000,"revised_value":790000,"adjusted_value":790000,"executed_value":0,"loa_justification":"Compatibilização fictícia com disponibilidade orçamentária.","execution_status":"not_started","pncp_item_code":None},
 {"code":"PAC-2026-004","title":"Adequações de acessibilidade em unidades","unit":"Diretoria de Engenharia","category":"works","desired_date":date(2026,9,1),"original_value":300000,"executed_value":0,"execution_status":"reprogrammed","change_justification":"Reprogramação fictícia por priorização de intervenções.","pncp_item_code":"DEMO-004"},
 {"code":"PAC-2026-005","title":"Licenças de colaboração segura","unit":"Diretoria de Tecnologia da Informação","category":"it","desired_date":date(2026,11,15),"original_value":180000,"executed_value":0,"execution_status":"cancelled","change_justification":"Cancelamento demonstrativo por solução corporativa alternativa.","pncp_item_code":"DEMO-005"},
 {"code":"PAC-2026-006","title":"Aquisição emergencial de EPIs","unit":"Diretoria de Operação e Manutenção","category":"goods","desired_date":date(2026,6,20),"original_value":65000,"executed_value":65000,"execution_status":"contracted","extraordinary":True,"change_justification":"Inclusão extraordinária fictícia por necessidade operacional superveniente.","pncp_item_code":"DEMO-006"},
]

def seed(db: Session):
    if not db.query(Demand).count():
        for item in DEMO:
            demand = Demand(**item); db.add(demand); db.flush(); snapshot(db, demand, "seed_created", "Registro fictício de demonstração v0.10.")
    if not db.query(ApprovalFlow).count():
        standard = ApprovalFlow(name="Fluxo padrão demonstrativo", description="Validação sequencial configurável para demandas ordinárias.")
        strategic = ApprovalFlow(name="Fluxo estratégico demonstrativo", description="Etapa adicional para contratações de maior materialidade.", minimum_value=500000)
        db.add_all([standard, strategic]); db.flush()
        standard_steps = [
            ApprovalStep(flow_id=standard.id, position=1, name="Validação da unidade", actor_role="requesting_unit"),
            ApprovalStep(flow_id=standard.id, position=2, name="Análise de governança", actor_role="governance"),
        ]
        strategic_steps = [
            ApprovalStep(flow_id=strategic.id, position=1, name="Validação da unidade", actor_role="requesting_unit"),
            ApprovalStep(flow_id=strategic.id, position=2, name="Análise de governança", actor_role="governance"),
            ApprovalStep(flow_id=strategic.id, position=3, name="Deliberação da autoridade", actor_role="authorizing_authority"),
        ]
        db.add_all(standard_steps + strategic_steps); db.flush()
        demand = db.query(Demand).filter_by(code="PAC-2026-003").first()
        if demand:
            approval = DemandApproval(demand_id=demand.id, flow_id=strategic.id, current_position=2)
            db.add(approval); db.flush()
            db.add(ApprovalDecision(approval_id=approval.id, step_id=strategic_steps[0].id, decision="approve", actor_role="requesting_unit", justification="Validação fictícia para demonstração."))
    db.commit()
