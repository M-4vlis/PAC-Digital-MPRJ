# Changelog

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
