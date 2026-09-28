# Changelog

## v0.13.0 — Qualidade final

- Cenário ponta a ponta cobre criação, revisão, aprovação, execução, SEI e validação PNCP.
- Orçamento automatizado de desempenho para o dashboard executivo.
- Limite de corpo de requisição, identificador de correlação, cache seguro e cabeçalhos CSP.
- Verificação de segredos versionados incorporada ao CI.
- Scripts de backup PostgreSQL com checksum e restauração isolada para validação.
- Cabeçalhos de segurança e cache de ativos reforçados no frontend.

## v0.12.0 — Relatórios executivos

- Relatório executivo em PDF, gerado localmente e sem serviço externo.
- Workbook XLSX com resumo institucional e carteira filtrável.
- Endpoints de download com tipos de conteúdo e nomes de arquivo adequados.
- Testes de integração verificam as assinaturas binárias PDF e XLSX.

## v0.11.0 — Transparência e acessibilidade

- Snapshot público imutável, versionado e verificável por hash SHA-256.
- API pública de listagem e consulta da última posição publicada do PAC.
- Minimização de dados no snapshot, sem números de processo SEI ou campos internos.
- Nova visão de transparência com carteira, totais e prova de integridade.
- Atalho de navegação, foco visível, região de avisos e preferência de movimento reduzido.
- Migration `0005`, teste de integração e comando local de publicação.

## v0.10.0 — Inteligência histórica PNCP

- Importador público e incremental de contratos do PNCP, restrito ao CNPJ do MPRJ.
- Persistência separada com proveniência, hash e rastreabilidade de sincronizações.
- Enriquecimento por contratação vinculada, sem armazenar fornecedores.
- Métricas P50, P75 e P90 da fase entre publicação da contratação e assinatura.
- Referência P75 integrada ao risco de forma explicável e somente com amostra mínima.
- Painel “Inteligência PNCP” distingue claramente carteira fictícia e histórico público real.
- Tolerância a `429` e indisponibilidades externas, com retomada incremental.
- Roadmap fechado e data-alvo da v1.0 registrados no repositório.

## v0.9.0 — Aprovação configurável e identidade institucional

- Logotipo público oficial do MPRJ aplicado ao cabeçalho da aplicação.
- Modelos e migration para fluxos, etapas, instâncias e decisões de aprovação.
- APIs para consultar fluxos, iniciar aprovação e decidir etapas com validação de perfil.
- Rejeições exigem justificativa; decisões e início do fluxo são registrados na auditoria.
- Painel de governança passa a exibir o progresso sequencial de cada demanda.
- Dataset fictício inclui dois fluxos demonstrativos, sem presumir autoridades ou alçadas reais.
- Testes de integração ampliados e migration validada em banco limpo.

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
- Frontend harmonizado com a linguagem visual do ecossistema VISÃO MPRJ: vinho institucional, detalhe dourado, fundo marfim, navegação horizontal e cartões de baixa elevação.
- Referência visual aplicada sem armazenar credenciais, capturas ou ativos protegidos da intranet no repositório.

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
