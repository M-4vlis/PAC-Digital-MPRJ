# v0.6 — Governança e interoperabilidade

## Revisões e versões

Uma revisão pendente contém somente a proposta de mudança. A aprovação aplica a proposta à demanda vigente, incrementa a versão e grava um snapshot JSON em `demand_versions`; o estado anterior continua disponível. Uma revisão decidida não pode ser aplicada novamente.

## Adequação pós-LOA

O registro mantém `original_value`, `revised_value`, `adjusted_value` e a justificativa. O valor usado para acompanhamento é o mais específico disponível: ajustado, revisado ou original.

## Retroplanejamento

O endpoint calcula marcos retroativos desde a data desejada. Os valores padrão por categoria estão no código apenas para a demonstração e são explicitamente marcados como parâmetros não normativos, configuráveis por chamada. Não substituem prazos da Resolução GPGJ nº 2.326/2020 ou ato superveniente.

## Interoperabilidade e transparência

As exportações respondem com CSV, JSON ou XLSX. O gerador PCA/PNCP cria uma estrutura de pré-validação por demanda e retorna pendências, como código de catálogo ausente. `publishable` permanece sempre `false`; não existe endpoint de envio externo.

## Validação

O fluxo de testes cobre healthcheck, painel, exportações, revisão aplicada com histórico, adequação pós-LOA, retroplanejamento e payload PNCP. Execute `pytest` em `backend` e `npm run build` em `frontend`.
