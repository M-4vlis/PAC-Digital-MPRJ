# Guia técnico de integrações e fronteiras reais

## Matriz de verdade

| Integração | Existe no código | Não existe ainda | Condição para ativar |
|---|---|---|---|
| SEI! | vínculo manual de processo; validação de formato; plano de integração; configuração externa por WSDL e chave; operações candidatas isoladas | cliente SOAP efetivo, autenticação, consulta/criação de processo, inclusão de documento, fila e reconciliação | WSDL da instância MPRJ, serviço cadastrado, IP/chave, unidades/tipos/operações autorizados e homologação |
| PCA/PNCP | coletor público somente leitura; persistência de proveniência; estrutura local `codigoUnidade`, `anoPca`, `itensPlano`; validação de campos obrigatórios | autenticação e POST externo; retificação/exclusão remota; reconciliação e recibos | código de unidade, catálogo homologado, ambiente/URL, credencial institucional e autorização |
| Identidade | variáveis e fronteira OIDC/LDAP documentadas; papéis de domínio | login institucional, validação de token, grupos, lotação e restrição por unidade | issuer/metadados, client, grupos e matriz de autorização homologada |

## PNCP

O gerador segue os nomes e tipos documentados no serviço `POST /v1/orgaos/{cnpj}/pca` do [Manual PNCP v2.6](https://pncp.gov.br/manual/pt-br/latest/plano_de_contratacao/inserir_plano_de_contratacoes.html). O serviço oficial exige autenticação. O projeto retorna sempre `publishable: false` e não contém rotina de transmissão.

Variáveis reservadas: `PNCP_API_BASE_URL`, `PNCP_API_TOKEN`, `PNCP_UNIT_CODE`. A presença de configuração não habilita transmissão automaticamente.

## SEI!

O endpoint `GET /api/demands/{id}/sei-integration-plan` descreve a intenção de integração e nunca chama o SEI. `POST /api/demands/{id}/sei-link` registra apenas um número informado pelo usuário.

Variáveis reservadas: `SEI_WSDL_URL` e `SEI_SERVICE_KEY`. Antes de implementar o cliente, a TI deve confirmar no WSDL real os nomes, contratos, códigos de unidade/tipo, limites de documento e regras de tratamento de dados. Os nomes `consultarProcedimento`, `gerarProcedimento` e `incluirDocumento` são candidatos, não garantia da instância MPRJ.

## Identidade e autorização

O cabeçalho `X-Actor-Role` é um mecanismo demonstrativo e não é fronteira de segurança. A demonstração pública temporária não exige login e, por isso, deve conter somente dados fictícios, sem transmissões externas habilitadas. Em homologação, o backend deve validar identidade emitida pelo provedor institucional e derivar papéis e unidade no servidor.

Matriz funcional prevista:

- unidade requisitante: criar, corrigir e retirar rascunho próprio; enviar para validação;
- governança: diligenciar, consolidar, revisar, ajustar após LOA e acompanhar execução;
- autoridade: deliberar nas alçadas configuradas;
- auditoria/consulta: leitura dos eventos e versões conforme autorização;
- público: somente snapshot aprovado e minimizado.

## Anexos

`UPLOAD_DIR` deve apontar para armazenamento persistente. A composição de produção monta o volume `pac_uploads`. Para uso institucional ainda são obrigatórios antivírus, política de retenção, cópia de segurança, limite de cota, classificação de acesso e, se exigido, criptografia em repouso.

## Contratos principais

- `POST /api/demands`: cria DFD validado e versão 1.
- `PATCH /api/demands/{id}`: corrige rascunho e cria nova versão.
- `DELETE /api/demands/{id}`: retirada lógica justificada.
- `POST/GET /api/demands/{id}/attachments`: anexa/lista DFD.
- `GET /api/demands/{id}/pncp-payload`: pré-valida a estrutura PCA sem transmitir.
- `POST /api/demands/{id}/sei-link`: registra vínculo local.
- `GET /api/pncp/history/metrics`: métricas e condições de uso da base pública.

## Roteiro de homologação técnica

1. Implantar em rede de homologação com PostgreSQL, storage e identidade institucionais.
2. Executar migrations em cópia controlada e validar backup/restauração.
3. Configurar usuários e testar segregação por papel e unidade, inclusive tentativas negativas.
4. Comparar payload PCA gerado com exemplos e validador do ambiente PNCP autorizado.
5. Testar SEI em ambiente autorizado com documentos fictícios e registrar recibos/erros.
6. Testar indisponibilidade, repetição idempotente, timeouts e reconciliação antes de habilitar transmissão.
7. Executar segurança, acessibilidade, carga e aceite funcional; somente então alterar os indicadores de integração para ativos.
