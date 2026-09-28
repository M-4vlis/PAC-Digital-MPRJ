# Vertical v0.10 — inteligência histórica PNCP

## Objetivo

Substituir parte dos parâmetros puramente demonstrativos por referências empíricas derivadas de dados abertos do próprio MPRJ, sem misturar histórico público com a carteira operacional fictícia.

## Fonte e limites

- fonte: API pública de consultas do PNCP;
- filtro invariável no código: CNPJ `28.305.936/0001-40`;
- modo: somente leitura, sem login ou credencial;
- conteúdo armazenado: contrato, categoria, unidade, valor, datas e vínculo da contratação;
- conteúdo deliberadamente descartado: CPF/CNPJ e nome de fornecedores;
- escopo temporal: fase pública entre publicação da contratação e assinatura do contrato.

O PNCP não substitui os marcos internos do SEI. Portanto, as referências históricas não são prazos normativos e não medem ainda a fase preparatória completa.

## Funcionamento

`python -m app.pncp_sync --start-year 2022 --end-year 2026 --enrich-limit 250`

O coletor faz upsert por número de controle PNCP, preserva hash e URL de origem e pode ser executado novamente. Limites `429` e indisponibilidades temporárias geram espera, estado parcial e retomada posterior.

O risco usa o P75 de sua categoria apenas quando existem ao menos dez observações temporais válidas. A razão, o tamanho da amostra e o prazo histórico são incluídos na explicação do alerta.
