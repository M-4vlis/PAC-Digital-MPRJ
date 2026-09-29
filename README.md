# PAC Digital MPRJ

Plataforma open source e portátil para governança do Plano Anual de Contratações do MPRJ. Centraliza planejamento, revisões, execução, riscos, adequações pós-LOA, auditoria e preparação de integrações com SEI! e PCA/PNCP.

> A carteira utiliza dados fictícios. A inteligência histórica utiliza somente dados abertos do PNCP filtrados pelo CNPJ do MPRJ; a v1.0 RC2 não transmite informações ao SEI ou ao PNCP.

## Capacidades da v1.0 RC2

- painel executivo planejado × executado, riscos e movimentações críticas;
- carteira de demandas com DFD completo, anexo, correção versionada, retirada governada e fluxo de execução;
- adequação pós-LOA e revisões aprovadas com justificativa preservada;
- retroplanejamento explicável com parâmetros explicitamente não normativos;
- exportações CSV, JSON e XLSX;
- pré-validação de payload PCA/PNCP, sempre sem publicação;
- vínculo local e adaptador de estágio SEI SOAP/WSDL;
- trilha de auditoria e diagnóstico de prontidão institucional;
- implantação portátil com Docker, PostgreSQL, API FastAPI e frontend React.
- importação incremental de contratos públicos do MPRJ no PNCP, com proveniência e minimização de dados;
- referências P50, P75 e P90 da fase pública usadas de forma explicável pelo motor de risco somente com ao menos 30 observações válidas por categoria;
- snapshots públicos versionados com hash SHA-256, minimização de dados e interface de transparência.
- melhorias iniciais de acessibilidade para teclado, foco, avisos e movimento reduzido.
- relatórios executivos portáteis em PDF e XLSX, sem SaaS obrigatório.
- cenário ponta a ponta, orçamento de desempenho, hardening HTTP e restauração validável do PostgreSQL.

## Execução local

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
alembic upgrade head
python -m app.pncp_sync --start-year 2022 --end-year 2026 --enrich-limit 250
python -m app.snapshot_publish --year 2026
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
- [Vertical v0.9](docs/23-vertical-v0.9.md)
- [Vertical v0.10](docs/25-vertical-v0.10.md)
- [Vertical v0.11](docs/26-vertical-v0.11.md)
- [Vertical v0.12](docs/27-vertical-v0.12.md)
- [Qualidade v0.13](docs/28-quality-v0.13.md)
- [Visão executiva v1 RC](docs/29-visao-executiva-v1-rc.md)
- [Plano de homologação](docs/30-plano-homologacao-institucional.md)
- [Runbook operacional](docs/31-runbook-operacional.md)
- [Notas da v1.0 RC1](docs/32-release-notes-v1-rc1.md)
- [Revisão de prontidão institucional](docs/33-revisao-prontidao-institucional.md)
- [Matriz de requisitos do PAC/DFD](docs/34-matriz-requisitos-pac-dfd.md)
- [Metodologia da inteligência PNCP](docs/35-metodologia-inteligencia-pncp.md)
- [Guia técnico de integrações](docs/36-guia-tecnico-integracoes.md)
- [Checklist de liberação](RELEASE-CHECKLIST.md)
- [Roadmap fechado até a v1.0](docs/24-roadmap-v1.md)
- [Integração SEI](docs/20-integracao-sei.md)
- [Backlog](docs/BACKLOG.md)
- [Política de segurança](SECURITY.md)
