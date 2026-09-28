# Qualidade final — v0.13

## Critérios automatizados

- 12 testes de integração e ponta a ponta;
- ciclo completo: demanda, revisão, aprovação, execução, SEI e PNCP;
- p95 local do dashboard abaixo de 750 ms em 25 leituras sequenciais;
- build React/TypeScript/Vite e migration limpa até `0005`;
- rejeição de corpos acima de 1 MiB e formatos de relatório desconhecidos;
- verificação de padrões de segredos no CI.

## Continuidade

`deploy/backup-postgres.sh` produz dump PostgreSQL em formato custom, permissão restrita e checksum SHA-256. `deploy/validate-restore.sh` restaura exclusivamente em `pac_restore_validation`, verifica as tabelas essenciais e remove a base temporária ao terminar.

## Limites

O ensaio de desempenho é um orçamento de regressão local, não substitui teste de carga na infraestrutura de homologação. A autenticação atual protege somente a demonstração; uso institucional requer OIDC/LDAP e autorização por unidade.
