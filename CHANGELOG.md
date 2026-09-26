# Changelog

## v0.8.0 — Candidata à demonstração executiva

- Interface redesenhada com visão executiva, carteira pesquisável, integrações e governança.
- Risco explicável, detalhe de demanda, retroplanejamento, prontidão PNCP e histórico na mesma experiência.
- Catálogo de integrações SEI, PCA/PNCP e identidade institucional com estado de configuração explícito.
- Endpoints de auditoria, prontidão operacional e healthcheck de banco.
- Cabeçalhos de segurança e implantação portátil com PostgreSQL, Nginx e Docker Compose.
- Pipeline de integração contínua, roteiro de demonstração e documentação operacional.
- Transmissões externas continuam deliberadamente bloqueadas.
- Dockerfile do frontend corrigido para instalação reprodutível com o lockfile pnpm.
- Implantação controlada validada em Oracle ARM64, com proxy HTTPS protegido e rede de borda opcional.
- Alias interno exclusivo para impedir colisões entre APIs de diferentes pilhas Docker.

## v0.7.0 — Vertical utilizável e preparação SEI

- Build do frontend concluído e dependências tornadas reprodutíveis no ambiente corporativo.
- Inclusão de formulário de demanda, avanço controlado da execução e vínculo demonstrativo ao SEI.
- Migration `0002` com referências ao processo SEI.
- Adaptador de estágio que descreve configuração e operações necessárias, sempre com transmissão desabilitada.
- Testes ampliados para criação, workflow, vínculo SEI e segurança do modo de estágio.

## v0.6.0 — Governança e interoperabilidade

### Adicionado

- Aplicação transacional de revisão aprovada e registro histórico de cada versão.
- Adequação pós-LOA e justificativas auditáveis.
- Retroplanejamento configurável por categoria de contratação.
- Dashboard executivo, exportações abertas e pré-validador PCA/PNCP.
- Dataset fictício ampliado, testes de integração e migrations reprodutíveis.

### Segurança e portabilidade

- Nenhuma rota publica no PNCP ou consome credenciais externas.
- Ambiente suportado sem SaaS obrigatório: FastAPI, SQLite para demonstração e XLSX aberto.
