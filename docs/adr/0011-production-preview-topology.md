# ADR 0011 — Topologia da candidata operacional

## Status

Aceita na v0.8.

## Contexto

A demonstração precisa ser portátil para VPS e, ao mesmo tempo, representar uma futura instalação institucional sem introduzir dependência obrigatória de SaaS.

## Decisão

Adotar frontend estático em Nginx, API FastAPI e PostgreSQL em contêineres separados. Migrations são aplicadas na inicialização da API; serviços possuem healthchecks; segredos entram por variáveis de ambiente. SQLite permanece apenas como opção de desenvolvimento.

Integrações externas continuam desligadas. HTTPS e autenticação devem ser providos antes de exposição pública.

## Consequências

A mesma aplicação pode ser implantada em Oracle Cloud, outra VPS ou infraestrutura própria. A futura adoção de orquestração institucional não altera o domínio nem os adaptadores.
