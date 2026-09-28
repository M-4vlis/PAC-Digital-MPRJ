# Status — v0.12.0

**Situação:** candidata à demonstração executiva, implantada de forma controlada em VPS Oracle. O domínio do PAC está funcional; integrações externas e identidade institucional dependem de autorização e dados do MPRJ.

## Validado

- Backend: 9 testes de integração aprovados.
- Migrations: cadeia `0001 → 0005` aplicável em banco limpo.
- Frontend: build React/TypeScript/Vite concluído, com 30 módulos e bundle aproximado de 170 kB.
- Interface em execução: visão executiva, carteira, detalhe da demanda, integrações e governança inspecionados no navegador.
- Identidade visual: frontend harmonizado com o padrão observado no ecossistema VISÃO MPRJ, usando cabeçalho vinho, detalhe dourado, fundo marfim, navegação horizontal e cartões institucionais responsivos.
- Banco para implantação: PostgreSQL 16 em composição Docker; SQLite continua disponível para desenvolvimento e demonstração local.
- Segurança básica: cabeçalhos HTTP, healthcheck de prontidão, segredos fora do repositório e transmissões externas bloqueadas.
- Implantação Oracle ARM64: v0.11 ativa em HTTPS, com migration `0005` aplicada.
- Inteligência PNCP em produção: 964 contratos públicos do MPRJ importados (2022–2026), total inicial agregado de R$ 1,432 bilhão e enriquecimento temporal incremental protegido contra limites da API pública.
- Integração de borda: frontend conectado ao proxy compartilhado por alias exclusivo; banco e API permanecem na rede interna.

## Entregue na v0.10

- Nova interface executiva responsiva, com estados e rótulos em português.
- Risco explicável por demanda, combinado com retroplanejamento não normativo.
- Detalhe unificado com valores, marcos, pendências PNCP, vínculo SEI e histórico.
- Painel explícito de prontidão para SEI!, PCA/PNCP e identidade OIDC/LDAP.
- Trilha de auditoria navegável e endpoint de eventos.
- Diagnóstico operacional e endpoints de saúde/prontidão.
- Topologia de implantação `web → API → PostgreSQL`, com healthchecks.
- Pipeline CI para testes e build.
- Linguagem visual institucional aplicada sem copiar conteúdo protegido ou incorporar ativos da intranet.
- Logotipo público oficial do MPRJ incorporado ao cabeçalho, com origem documentada.
- Fluxos sequenciais de aprovação configuráveis, alçada opcional, decisão por perfil e auditoria de cada etapa.
- Coletor incremental do PNCP limitado por código ao CNPJ do MPRJ, sem credenciais e em modo somente leitura.
- Base histórica separada da carteira operacional, com URL de origem, hash, data de importação e execução da sincronização.
- Minimização: identificadores e nomes de fornecedores não são armazenados.
- P50, P75 e P90 por categoria e referência histórica incorporada ao risco quando a amostra é suficiente.
- Tratamento de limites e indisponibilidade do PNCP com repetição progressiva, retomada e conclusão parcial segura.

## Entregue na v0.11

- Snapshot público imutável e versionado por exercício.
- Hash SHA-256 do JSON canônico para verificação de integridade.
- API e interface de transparência separadas da carteira operacional.
- Minimização de dados, sem identificadores de processo SEI na publicação.
- Melhorias de acessibilidade para teclado, foco, mensagens e movimento reduzido.
- Validação visual em produção concluída sem erros de console: snapshot v1, hash e seis demandas demonstrativas exibidos corretamente.

## Entregue na v0.12

- Relatório executivo PDF autônomo para apresentação e arquivamento.
- Planilha XLSX executiva com resumo, identidade de cores e carteira filtrável.
- Geração local, sem dependência de SaaS, com validação automatizada dos arquivos.

## Dependências para uso institucional real

1. Conectar autenticação institucional e definir matriz de perfis/unidades.
2. Obter autorização, WSDL, operações e credencial/IP do SEI-MPRJ.
3. Homologar o payload PCA/PNCP, mapear catálogo e receber credencial institucional.
4. Definir domínio institucional definitivo, política de backup e observabilidade; o endereço HTTPS atual é apenas para demonstração controlada.
5. Validar conteúdo, regras, acessibilidade e fluxo de aprovação com as áreas responsáveis.

Nenhum desses itens pode ser fabricado no projeto: são decisões ou credenciais institucionais. A arquitetura mantém cada integração desacoplada para que sejam conectadas sem reescrever o domínio do PAC.
