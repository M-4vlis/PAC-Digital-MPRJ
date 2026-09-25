# ADR 0009 — Revisões materiais, ajustes orçamentários e interoperabilidade em estágio

**Status:** aceito.

## Contexto

Uma revisão aprovada não pode apenas alterar o registro em uso, pois isso elimina a trilha necessária para governança. A adequação após a LOA precisa preservar os valores de referência. O PNCP é uma integração institucional dependente de credenciais e validação oficial.

## Decisão

- Aprovação de revisão cria nova versão persistente com snapshot e evento de auditoria.
- Valores original, revisado e ajustado coexistem com justificativa.
- Retroplanejamento é configurável e não normativo.
- O adaptador PCA/PNCP só gera e valida payload local: sem publicação, credenciais ou conexão externa.

## Consequências

O projeto preserva rastreabilidade e permanece PNCP-ready, mas a futura integração real exigirá homologação técnica e autorização institucional.
