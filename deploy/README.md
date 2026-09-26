# Implantação da versão demonstrativa

Pré-requisitos: Linux com Docker Engine e Docker Compose, porta HTTP liberada e acesso SSH administrativo.

```bash
cp .env.example .env
# edite PAC_DB_PASSWORD antes de iniciar
docker compose -f deploy/docker-compose.production.yml --env-file .env up -d --build
docker compose -f deploy/docker-compose.production.yml --env-file .env ps
```

A interface ficará disponível apenas no loopback da VPS, na porta definida por `PAC_HTTP_PORT` (padrão `8080`). Para exposição pública, use domínio e proxy HTTPS institucional; não exponha a aplicação sem controle de acesso enquanto a autenticação OIDC não estiver conectada.

As variáveis SEI e PNCP apenas indicam prontidão de configuração. A v0.8 não transmite dados externos, mesmo quando valores forem informados.
