# PAC Digital MPRJ

Plataforma open source e portátil para governança do Plano Anual de Contratações do MPRJ. Centraliza planejamento, revisões, execução, riscos, adequações pós-LOA, auditoria e preparação de integrações com SEI! e PCA/PNCP.

> O repositório utiliza exclusivamente dados e perfis fictícios. A v0.8 não transmite informações ao SEI ou ao PNCP.

## Capacidades da v0.8

- painel executivo planejado × executado, riscos e movimentações críticas;
- carteira de demandas com fluxo de execução, histórico e versionamento;
- adequação pós-LOA e revisões aprovadas com justificativa preservada;
- retroplanejamento explicável com parâmetros explicitamente não normativos;
- exportações CSV, JSON e XLSX;
- pré-validação de payload PCA/PNCP, sempre sem publicação;
- vínculo local e adaptador de estágio SEI SOAP/WSDL;
- trilha de auditoria e diagnóstico de prontidão institucional;
- implantação portátil com Docker, PostgreSQL, API FastAPI e frontend React.

## Execução local

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
alembic upgrade head
python -m uvicorn app.main:app --reload
```

Em outro terminal:

```powershell
cd frontend
pnpm install
pnpm run dev
```

Frontend: `http://localhost:5173` · API: `http://localhost:8000/docs`

## Implantação

Consulte [deploy/README.md](deploy/README.md). A composição de produção usa PostgreSQL e não exige SaaS. Para exposição pública, é obrigatório adicionar HTTPS e controle de acesso institucional.

## Documentação

- [Status atual](STATUS.md)
- [Roteiro de demonstração executiva](docs/ROTEIRO-DEMONSTRACAO.md)
- [Vertical v0.8](docs/21-vertical-v0.8.md)
- [Integração SEI](docs/20-integracao-sei.md)
- [Backlog](docs/BACKLOG.md)
- [Política de segurança](SECURITY.md)
