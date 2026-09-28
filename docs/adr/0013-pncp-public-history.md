# ADR 0013 — histórico público PNCP separado do PAC

**Status:** aceita na v0.10.

## Decisão

Importar dados abertos do PNCP em tabelas próprias, com filtro fixo no CNPJ do MPRJ, proveniência verificável e minimização de dados. A carteira fictícia e a base pública nunca compartilham os mesmos registros.

## Uso no risco

O tempo entre publicação da contratação e assinatura é resumido por categoria. O P75 somente influencia o risco após amostra mínima, e sua contribuição permanece explícita na resposta da API e na interface.

## Consequências

- indisponibilidade ou limitação do PNCP não bloqueia o PAC;
- sincronizações são retomáveis e idempotentes;
- dados de fornecedores não são necessários e não são persistidos;
- a fase preparatória interna continuará não normativa até que marcos autorizados do SEI estejam disponíveis.
