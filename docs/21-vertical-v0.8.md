# Vertical v0.8 — prontidão executiva e operacional

## Objetivo

Transformar a vertical funcional da v0.7 em uma candidata apresentável, navegável e implantável, sem antecipar autorizações institucionais ou habilitar transmissões externas.

## Experiência executiva

A navegação foi organizada em quatro áreas: visão executiva, carteira do PAC, integrações e governança. A visão executiva combina valores planejado e executado, distribuição da carteira, alterações e demandas que requerem atenção. O detalhe da demanda reúne risco, retroplanejamento, PNCP, SEI e histórico.

## Risco explicável

O nível combina situação de execução, marcos retroplanejados, data desejada, catálogo PNCP e vínculo SEI. Cada resultado apresenta motivos. As regras são parâmetros demonstrativos de gestão; não constituem norma do MPRJ.

## Interoperabilidade

O catálogo de integrações torna explícitos protocolo, dependências, configuração e bloqueio de transmissão. SEI usa a fronteira SOAP/WSDL; PCA/PNCP usa REST/JSON; identidade prevê OIDC/LDAP. O domínio do PAC não depende diretamente de nenhum fornecedor ou SaaS.

## Implantação

A topologia de referência contém frontend Nginx, API FastAPI e PostgreSQL, com healthchecks e migrations na inicialização. Segredos são fornecidos exclusivamente por variáveis de ambiente. A exposição externa requer HTTPS e controle de acesso.

## Critério de conclusão

- build do frontend aprovado;
- testes do backend aprovados;
- migrations reproduzíveis;
- navegação e integração frontend/API inspecionadas em execução;
- documentação, CI e roteiro de demonstração atualizados.
