# Implantação da versão demonstrativa

Pré-requisitos: Linux com Docker Engine e Docker Compose, porta HTTP liberada e acesso SSH administrativo.

```bash
cp .env.example .env
# edite PAC_DB_PASSWORD antes de iniciar
docker compose -f deploy/docker-compose.production.yml --env-file .env up -d --build
docker compose -f deploy/docker-compose.production.yml --env-file .env ps
```

A interface ficará disponível apenas no loopback da VPS, na porta definida por `PAC_HTTP_PORT` (padrão `8080`). Para exposição pública, use domínio e proxy HTTPS. A demonstração temporária pode operar sem login somente com carteira fictícia, integrações externas bloqueadas, cabeçalho `X-Robots-Tag: noindex` e ciência de que os papéis demonstrativos não constituem controle de segurança. Dados ou documentos reais exigem identidade institucional antes da exposição.

Quando já existir um proxy reverso em outra pilha Docker, use o arquivo opcional de borda para conectar somente o frontend à rede compartilhada:

```bash
printf 'PAC_EDGE_NETWORK=nome_da_rede_do_proxy\n' >> .env
docker compose \
  -f deploy/docker-compose.production.yml \
  -f deploy/docker-compose.edge.yml \
  --env-file .env up -d --build
```

O proxy poderá encaminhar as requisições para `pac-digital-web:8080`. Banco e API continuam isolados na rede interna da aplicação.

## Demonstração pública temporária

O arquivo `Caddyfile.public-demo` contém a rota de referência sem autenticação básica. No ambiente compartilhado, incorpore somente os blocos do PAC à configuração já existente do proxy; não substitua rotas de outros sistemas. O endereço de demonstração validado em 05/10/2026 é:

`https://pacdigital-mprj.163-176-228-150.sslip.io/`

O endereço antigo redireciona permanentemente para o novo. Um endereço institucional, como `pacdigital.mprj.mp.br`, depende de reserva DNS e certificado administrados pelo MPRJ; basta substituir os nomes dos hosts na configuração, sem alterar a aplicação.

As variáveis SEI e PNCP apenas indicam prontidão de configuração. A v1.0 RC2 não transmite dados externos, mesmo quando valores forem informados. A leitura de dados abertos do PNCP é independente dessas credenciais. `PNCP_UNIT_CODE` identifica a unidade no payload local de pré-validação; não habilita publicação.

O volume `pac_uploads` preserva os anexos de DFD entre recriações dos contêineres. A cópia de segurança institucional deve abranger o PostgreSQL e esse volume.

## Backup e restauração

```bash
sh deploy/backup-postgres.sh
sh deploy/validate-restore.sh backups/pac-digital-AAAAMMDDTHHMMSSZ.dump
```

O backup recebe permissão `0600` e checksum SHA-256. A validação restaura somente em uma base temporária de nome fixo e nunca sobrescreve `pac_digital`.
