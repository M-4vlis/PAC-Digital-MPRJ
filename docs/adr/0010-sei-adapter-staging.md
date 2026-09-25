# ADR 0010 — Adaptador SEI em modo de estágio

**Status:** aceito.

## Decisão

A integração com o SEI será feita por adaptador desacoplado baseado no WSDL disponibilizado pela instância do MPRJ. Até existir autorização, cadastro do sistema e ambiente de homologação, o adaptador permanecerá sem transmissão.

## Motivo

As operações e permissões do Web Service são definidas pela administração de cada instância. Gravar endpoint, chave, unidade ou tipo de processo no produto criaria acoplamento institucional inseguro.

## Consequências

- configuração exclusivamente por variáveis/secret manager;
- menor privilégio por operação, unidade e tipo documental;
- vínculo manual disponível durante a demonstração;
- nenhuma chamada real no pacote público.
