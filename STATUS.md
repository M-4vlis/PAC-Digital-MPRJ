# Status — v1.0.0-rc.2

**Situação:** candidata pronta para apresentação executiva e início da homologação institucional, implantada de forma controlada em VPS Oracle. O escopo funcional da v1 está congelado; integrações externas e identidade dependem de autorização e dados do MPRJ.

## Validado

- Backend: 13 testes de integração, ponta a ponta, segurança e desempenho aprovados.
- Migrations: cadeia `0001 → 0006` aplicável em banco limpo.
- Frontend: build React/TypeScript/Vite concluído, com 30 módulos e bundle aproximado de 182 kB.
- Interface em execução: visão executiva, carteira, detalhe da demanda, integrações e governança inspecionados no navegador.
- Identidade visual: frontend harmonizado com o padrão observado no ecossistema VISÃO MPRJ, usando cabeçalho vinho, detalhe dourado, fundo marfim, navegação horizontal e cartões institucionais responsivos.
- Banco para implantação: PostgreSQL 16 em composição Docker; SQLite continua disponível para desenvolvimento e demonstração local.
- Segurança básica: cabeçalhos HTTP, healthcheck de prontidão, segredos fora do repositório e transmissões externas bloqueadas.
- Implantação Oracle ARM64: v1.0.0-rc.2 ativa em HTTPS, migration `0006` aplicada, API e frontend saudáveis e backup prévio executado.
- Inteligência PNCP em 29/09/2026: 966 contratos públicos do MPRJ importados (2022–2026), nove registros temporalmente calculáveis e cobertura de 0,93%. A última sincronização enriqueceu sete registros e terminou parcial após resposta HTTP 429 do PNCP. A amostra continua insuficiente, fica marcada como exploratória e não calibra o risco.
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
- Downloads PDF e XLSX validados em produção com resposta HTTP 200 e formatos reconhecidos.

## Entregue na v0.13

- Cenário E2E do ciclo completo da demanda e suas integrações preparatórias.
- Orçamento de regressão de desempenho para o dashboard.
- Limite de requisição, CSP, `no-store`, correlação de respostas e cache seguro de ativos.
- Verificação de padrões de segredos no pipeline de integração contínua.
- Backup PostgreSQL com checksum e restauração isolada e destrutível somente da base temporária de validação.
- Recuperação comprovada na VPS a partir de dump de 169 KiB: checksum íntegro, seis demandas restauradas, migration presente e base temporária removida.

## Entregue na v1.0 RC1

- Escopo funcional congelado e alterações limitadas a correções e exigências de homologação.
- Visão executiva de uma página, roteiro de 10 minutos e respostas para perguntas esperadas.
- Plano de homologação com frentes, entradas e evidências de aceite.
- Runbook de implantação, saúde, backup, recuperação e incidente.
- Checklist que separa produto concluído de dependências institucionais.

## Entregue na v1.0 RC2

- Correção do cadastro que criava a demanda, mas desmontava o formulário antes de limpá-lo e exigia recarga visual.
- DFD ampliado conforme os campos do art. 2º da Resolução GPGJ nº 2.326/2020, com validação de total e período.
- Valor unitário com formatação em reais, quantidade e total calculado.
- Correção versionada e retirada lógica justificada de rascunhos pela unidade requisitante.
- Anexo de DFD em PDF, DOC e DOCX, com limite, validação mínima e armazenamento persistente.
- Inteligência PNCP com população, amostra, cobertura, denominador e definições de P50/P75; uso no risco bloqueado abaixo de 30 casos por categoria.
- Tela de transparência sem exposição de hash técnico.
- Pré-validação PCA alinhada aos campos do Manual PNCP v2.6 e documentação explícita das fronteiras de SEI, PNCP e identidade.
- Revisão de prontidão, matriz normativa, metodologia estatística e guia técnico de integrações.

## Dependências para uso institucional real

1. Conectar autenticação institucional e definir matriz de perfis/unidades.
2. Obter autorização, WSDL, operações e credencial/IP do SEI-MPRJ.
3. Homologar o payload PCA/PNCP, mapear catálogo e receber credencial institucional.
4. Definir domínio institucional definitivo, política de backup e observabilidade; o endereço HTTPS atual é apenas para demonstração controlada.
5. Validar conteúdo, regras, acessibilidade e fluxo de aprovação com as áreas responsáveis.

Nenhum desses itens pode ser fabricado no projeto: são decisões ou credenciais institucionais. A arquitetura mantém cada integração desacoplada para que sejam conectadas sem reescrever o domínio do PAC.
