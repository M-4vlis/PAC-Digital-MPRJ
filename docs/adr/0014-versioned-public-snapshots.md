# ADR 0014 — Snapshots públicos versionados

## Decisão

A transparência consumirá snapshots publicados e imutáveis, em vez de expor diretamente a carteira operacional.

Cada snapshot recebe versão sequencial por exercício, data de publicação e hash SHA-256 calculado sobre JSON canônico. Campos operacionais internos, como identificadores de processos SEI, não integram o contrato público.

## Consequências

- uma publicação continua reproduzível mesmo após novas alterações internas;
- correções geram nova versão, sem sobrescrever a anterior;
- o Portal da Transparência pode consumir uma API estável ou arquivos derivados;
- a decisão sobre o canal institucional de publicação permanece externa ao projeto.
