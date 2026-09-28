# Vertical v0.11 — Transparência

## Objetivo

Disponibilizar uma posição pública do PAC que seja estável, versionada, verificável e separada da carteira operacional.

## Entregas

- tabela `public_pac_snapshots` e migration `0005`;
- geração determinística e hash SHA-256 do conteúdo;
- comando `python -m app.snapshot_publish --year 2026`;
- consultas `GET /api/public/pac/snapshots` e `GET /api/public/pac/latest`;
- aba Transparência com resumo, carteira publicada e prova de integridade;
- exclusão deliberada de identificadores SEI e campos internos;
- melhorias de navegação por teclado, foco e movimento reduzido.

O snapshot demonstrativo contém somente dados fictícios. A publicação no portal institucional depende de canal, revisão de conteúdo e homologação do MPRJ.
