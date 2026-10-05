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

## Borda HTTPS da demonstração

- URL canônica temporária: `https://pacdigital-mprj.163-176-228-150.sslip.io/`;
- o host antigo `pac.163-176-228-150.sslip.io` deve responder com redirecionamento permanente;
- validar sem credenciais: página, `/health` e um endpoint de leitura em `/api/` devem responder em HTTPS;
- no arranjo atual, `sslh` recebe a porta 443 e encaminha TLS para o proxy em `127.0.0.1:8443`; destino diferente torna o site inacessível;
- a rota Caddy deve encaminhar o host canônico para `pac-digital-web:8080`, sem `basic_auth`, e enviar `X-Robots-Tag: noindex, nofollow, noarchive`;
- como o proxy é compartilhado, uma implantação de outro sistema não pode substituir o arquivo inteiro sem preservar a rota do PAC;
- a ausência de login é exclusiva da demonstração com dados fictícios. Antes de qualquer dado real, habilitar OIDC/LDAP e autorização no backend.

## Segredos

Senhas, chaves e tokens devem permanecer em cofre institucional ou variáveis protegidas. Não registrar valores em commits, issues, relatórios ou logs.
