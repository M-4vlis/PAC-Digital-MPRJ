# Status — v0.7

**Situação:** vertical funcional demonstrativo, com frontend compilado e preparação PNCP/SEI sem transmissão externa.

## Validação no ambiente de entrega

- Backend: testes de integração aprovados (`5 passed`).
- Migrations: cadeia `0001 → 0002` validada em SQLite novo.
- Frontend: dependências instaladas e build React/TypeScript/Vite concluído (`30 módulos`, bundle JS de aproximadamente 149 kB).
- Cadeia de dependências: tipos React, runtime React e TypeScript vendorizados para contornar o certificado/proxy corporativo; Vite permanece como dependência aberta instalada pelo gerenciador.

## Escopo entregue

- Revisões aprovadas aplicadas à demanda em nova versão, com histórico imutável de payload e auditoria.
- Adequação pós-LOA: valores original, revisado e ajustado, com justificativa obrigatória.
- Retroplanejamento por marcos, com parâmetros configuráveis e aviso explícito de que não são prazos normativos.
- Painel de governança: planejado × executado, alterações, riscos, inclusões extraordinárias, cancelamentos e reprogramações.
- Exportações CSV, JSON e XLSX.
- Payload PCA/PNCP gerado e validado localmente; a saída declara que não é publicável e não transmite dados.
- Dataset demonstrativo com seis demandas fictícias em cenários distintos.
- Restrições de API: CORS limitado ao ambiente local de desenvolvimento, validação de entrada, erros 404/409 e sem rotas de publicação externa.
- Criação de demanda pela interface e transições controladas da execução.
- Vínculo local a processo SEI e diagnóstico de integração SOAP/WSDL, sem comunicação real.

## Limites deliberados

- A autenticação continua demonstrativa: não há conexão com identidade institucional.
- O modelo de payload PNCP é uma pré-validação de interoperabilidade, não homologação com a API oficial.
- Os prazos do retroplanejamento são parâmetros de gestão e não norma MPRJ.
- Não há dados internos reais, credenciais, publicação institucional ou dependência mandatória de SaaS.
- A integração SEI depende de cadastro e autorização pela administração da instância MPRJ, além da confirmação do WSDL e das operações liberadas.
