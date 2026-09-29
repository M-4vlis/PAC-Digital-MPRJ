# Metodologia da inteligência histórica PNCP

## Universo e amostra temporal

`Contratos importados` é a quantidade de registros distintos retornados pelo endpoint público de contratos do PNCP para o CNPJ `28.305.936/0001-40`. A unicidade é controlada por `numeroControlePNCP`.

`Prazos calculáveis` é um subconjunto: registros que possuem referência de contratação consultável, data de publicação da contratação e data de assinatura do contrato, com diferença entre zero e 3.000 dias. Logo, quando a tela mostra 964 contratos e seis prazos calculáveis, P50, P75 e P90 usam somente os seis casos — nunca os 964.

## Duração observada

`public_phase_days = data de assinatura do contrato − data de publicação da contratação no PNCP`, em dias corridos.

Essa duração não contém a fase preparatória interna, não mede o tempo total da necessidade até a contratação e não é prazo normativo do MPRJ.

## Percentis

Os valores são ordenados e calculados pelo método empírico de posto mais próximo: posição `ceil(p × n)`.

- P50: mediana; ao menos 50% das observações ficam abaixo ou iguais ao valor.
- P75: ao menos 75% ficam abaixo ou iguais; 25% demoraram mais.
- P90: ao menos 90% ficam abaixo ou iguais.

Com amostras pequenas, os percentis são instáveis. Por isso a tela os marca como exploratórios e o motor só aceita referência histórica por categoria com `n ≥ 30`.

Posição observada após a implantação da RC2 em 29/09/2026: 966 contratos, nove prazos calculáveis e cobertura de 0,93%. A API do PNCP respondeu HTTP 429 durante o enriquecimento; a execução foi registrada como parcial e nenhuma inferência foi usada para preencher datas ausentes.

## Uso no motor de risco

Sem 30 casos válidos na mesma categoria, nenhum percentil histórico altera o risco. Permanecem apenas regras explicáveis de situação, data desejada, retroplanejamento não normativo, catálogo e vínculo SEI.

Com amostra suficiente, o motor acrescenta alerta quando o prazo restante é menor que o P75 da mesma categoria. A resposta registra valor do P75 e tamanho da amostra usada.

## Qualidade e proveniência

Para cada contrato são preservados: número de controle PNCP, referência da compra, categoria de origem, objeto, unidade, valor inicial, datas necessárias, URL consultada, hash do registro de origem e data de importação. Dados de fornecedores não são armazenados.

A sincronização é incremental, idempotente e registra quantidade vista, inserida, atualizada, enriquecida, estado, avisos e horários. Respostas 429 e indisponibilidades produzem execução parcial segura; não autorizam completar datas por inferência.

Fonte técnica: [Manual de Integração do PNCP v2.6](https://pncp.gov.br/manual/pt-br/latest/), além da API pública de consulta do portal.

## Validações automatizadas

Os testes cobrem unicidade, filtro pelo CNPJ MPRJ, cálculo da duração, percentis, limiar mínimo de 30 observações e incorporação condicionada ao risco. A validação institucional deve ainda comparar uma amostra manual com os registros exibidos no Portal PNCP.
