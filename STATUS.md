# Status — v0.8.0

**Situação:** candidata à demonstração executiva, implantada de forma controlada em VPS Oracle. O domínio do PAC está funcional; integrações externas e identidade institucional dependem de autorização e dados do MPRJ.

## Validado

- Backend: 6 testes de integração aprovados.
- Migrations: cadeia `0001 → 0002` aplicável em banco limpo.
- Frontend: build React/TypeScript/Vite concluído, com 30 módulos e bundle aproximado de 162 kB.
- Interface em execução: visão executiva, carteira, detalhe da demanda, integrações e governança inspecionados no navegador.
- Banco para implantação: PostgreSQL 16 em composição Docker; SQLite continua disponível para desenvolvimento e demonstração local.
- Segurança básica: cabeçalhos HTTP, healthcheck de prontidão, segredos fora do repositório e transmissões externas bloqueadas.
- Implantação Oracle ARM64: imagens construídas na VPS, PostgreSQL saudável, migrations no head `0002`, acesso HTTPS protegido e seis demandas fictícias carregadas.
- Integração de borda: frontend conectado ao proxy compartilhado por alias exclusivo; banco e API permanecem na rede interna.

## Entregue na v0.8

- Nova interface executiva responsiva, com estados e rótulos em português.
- Risco explicável por demanda, combinado com retroplanejamento não normativo.
- Detalhe unificado com valores, marcos, pendências PNCP, vínculo SEI e histórico.
- Painel explícito de prontidão para SEI!, PCA/PNCP e identidade OIDC/LDAP.
- Trilha de auditoria navegável e endpoint de eventos.
- Diagnóstico operacional e endpoints de saúde/prontidão.
- Topologia de implantação `web → API → PostgreSQL`, com healthchecks.
- Pipeline CI para testes e build.

## Dependências para uso institucional real

1. Conectar autenticação institucional e definir matriz de perfis/unidades.
2. Obter autorização, WSDL, operações e credencial/IP do SEI-MPRJ.
3. Homologar o payload PCA/PNCP, mapear catálogo e receber credencial institucional.
4. Definir domínio institucional definitivo, política de backup e observabilidade; o endereço HTTPS atual é apenas para demonstração controlada.
5. Validar conteúdo, regras, acessibilidade e fluxo de aprovação com as áreas responsáveis.

Nenhum desses itens pode ser fabricado no projeto: são decisões ou credenciais institucionais. A arquitetura mantém cada integração desacoplada para que sejam conectadas sem reescrever o domínio do PAC.
