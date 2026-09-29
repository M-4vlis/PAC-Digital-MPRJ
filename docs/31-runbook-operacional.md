# Runbook operacional

## Verificação diária

1. consultar `/health` e `/health/ready`;
2. confirmar estado dos contêineres e disponibilidade do PostgreSQL;
3. verificar capacidade de disco, erros do proxy e falhas da API;
4. confirmar a data do último backup e seu checksum.

## Implantação

1. exigir CI verde no commit aprovado;
2. atualizar o repositório por avanço simples;
3. reconstruir os contêineres e aplicar migrations antes da API;
4. validar saúde, prontidão, versão e endpoints críticos;
5. registrar commit, horário e resultado.

## Backup e recuperação

- executar `sh deploy/backup-postgres.sh`;
- preservar o dump e o arquivo `.sha256` fora da VPS conforme política institucional;
- testar com `sh deploy/validate-restore.sh CAMINHO_DO_DUMP`;
- nunca restaurar sobre `pac_digital` sem janela, backup prévio e autorização.

## Incidente

1. preservar logs e identificar o `X-Request-ID` afetado;
2. desabilitar transmissões externas sem interromper consultas, quando aplicável;
3. registrar impacto, intervalo, versão e ação tomada;
4. recuperar a partir do último backup validado somente com autorização.

## Segredos

Senhas, chaves e tokens devem permanecer em cofre institucional ou variáveis protegidas. Não registrar valores em commits, issues, relatórios ou logs.
